import logging
import os
import random
import sys
from datetime import datetime
from os import environ
from os import path

import sqlalchemy as db
from dateutil.relativedelta import relativedelta
from dotenv import dotenv_values
from sqlalchemy.orm import sessionmaker

from app.db.models import DownloadStatus, Ticker
from download_ticker_list import get_ticker_list, clean_ticker_list
from download_ticker_ohlc import (
    get_ticker_info,
    get_ticker_ohlc,
    cleanup_folders,
)

logging.basicConfig(
    format="▸ %(asctime)s.%(msecs)03d %(filename)s:%(lineno)d %(levelname)s %(message)s",
    level=logging.INFO,
    datefmt="%H:%M:%S",
)


class Downloader:
    def __init__(self):
        os.chdir(os.path.dirname(os.getcwd()))
        if path.exists(path.join(os.getcwd(), ".env")):
            config = dotenv_values(path.join(os.getcwd(), ".env"))
        else:
            config = {
                "SQLALCHEMY_DATABASE_URI": environ.get("SQLALCHEMY_DATABASE_URI"),
                "DATA_DIR": environ.get("DATA_DIR"),
            }

        self.base_path = config.get("DATA_DIR")

        try:
            engine = db.create_engine(config.get("SQLALCHEMY_DATABASE_URI"))
            self.session = sessionmaker(bind=engine)

            sess = self.session()
            download_status = sess.query(DownloadStatus).first()

            if not download_status:
                init_date = datetime.now() - relativedelta(days=1)
                download_status = DownloadStatus(
                    ticker_list_last_download=init_date,
                    ticker_list_last_cleanup=init_date,
                    ticker_ohlc_last_download=init_date,
                    ticker_ohlc_last_cleanup=init_date,
                )
                sess.add(download_status)
            else:
                download_status.ticker_list_download_in_progress = False
                download_status.ticker_list_cleanup_in_progress = False
                download_status.ticker_ohlc_download_in_progress = False
                download_status.ticker_ohlc_cleanup_in_progress = False

            sess.commit()
            sess.close()

        except Exception as e:
            logging.exception("Exception: %s", e)
            sys.exit()

    def run(self, task_name):
        if task_name == "get_ticker_list":
            self.get_ticker_list()
        elif task_name == "clean_ticker_list":
            self.clean_ticker_list()
        elif task_name == "get_ticker_data":
            self.get_ticker_data()
        elif task_name == "clean_ticker_data":
            self.clean_ticker_data()

    def get_ticker_list(self):
        sess = self.session()
        download_status = sess.query(DownloadStatus).first()
        if not download_status:
            sys.exit()

        if (
            not download_status.ticker_list_download_in_progress
            and (
                datetime.now() - download_status.ticker_list_last_download
            ).total_seconds()
            > 2 * 60 * 60
        ):
            try:
                start_time = datetime.now()
                download_status.ticker_list_download_in_progress = True
                sess.commit()

                get_ticker_list(self.session())

                logging.info(
                    "finished downloading ticker list, duration: %s sec"
                    % (datetime.now() - start_time).seconds
                )

                download_status.ticker_list_last_download = datetime.now()

            except Exception as e:
                logging.exception("Exception: %s", e)

        download_status.ticker_list_download_in_progress = False
        sess.commit()
        sess.close()

    def clean_ticker_list(self):
        sess = self.session()
        download_status = sess.query(DownloadStatus).first()
        if not download_status:
            sys.exit()

        if (
            not download_status.ticker_list_cleanup_in_progress
            and (
                datetime.now() - download_status.ticker_list_last_cleanup
            ).total_seconds()
            > 24 * 60 * 60
        ):
            try:
                start_time = datetime.now()
                download_status.ticker_list_download_in_progress = True
                sess.commit()

                # clean tickers that are older than 3 days and are not downloaded
                query_date = (datetime.now() - relativedelta(days=3)).date()
                clean_ticker_list(self.session(), query_date, False)

                # clean tickers that are older than 5 days and are downloaded
                query_date = (datetime.now() - relativedelta(days=5)).date()
                clean_ticker_list(self.session(), query_date, True)

                logging.info(
                    "finished cleaning up ticker list, duration: %s sec"
                    % (datetime.now() - start_time).seconds
                )

            except Exception as e:
                logging.exception("Exception: %s", e)

        download_status.ticker_list_last_cleanup = datetime.now()
        download_status.ticker_list_cleanup_in_progress = False
        sess.commit()
        sess.close()

    def get_ticker_data(self):
        sess = self.session()
        download_status = sess.query(DownloadStatus).first()
        if not download_status:
            sys.exit()

        logging.info(
            "ohlc download in progress: %s"
            % (download_status.ticker_ohlc_download_in_progress)
        )

        if (
            not download_status.ticker_ohlc_download_in_progress
            and (
                datetime.now() - download_status.ticker_ohlc_last_download
            ).total_seconds()
            > 60
        ):
            try:
                start_time = datetime.now()
                download_status.ticker_ohlc_download_in_progress = True
                sess.commit()

                tickers = sess.query(Ticker).filter(Ticker.downloaded == False).all()

                if tickers:
                    ticker = random.choice(tickers)

                    logging.info("downloading data for ticker: %s" % ticker.ticker_name)
                    downloaded = get_ticker_info(self.base_path, ticker)
                    if downloaded:
                        get_ticker_ohlc(self.base_path, ticker)
                        ticker.date_added = datetime.now()
                        ticker.downloaded = True
                        sess.merge(ticker)
                        logging.info(
                            "finished downloading ticker: %s, duration: %s sec"
                            % (
                                ticker.ticker_name,
                                (datetime.now() - start_time).seconds,
                            )
                        )
                    else:
                        sess.delete(ticker)
            except Exception as e:
                logging.exception("Exception: %s", e)

        download_status.ticker_ohlc_download_in_progress = False
        download_status.ticker_ohlc_last_download = datetime.now()
        sess.commit()
        sess.close()

    def clean_ticker_data(self):
        sess = self.session()
        download_status = sess.query(DownloadStatus).first()
        if not download_status:
            sys.exit()

        if (
            download_status.ticker_ohlc_cleanup_in_progress
            and (
                datetime.now() - download_status.ticker_ohlc_last_cleanup
            ).total_seconds()
            > 24 * 60 * 60
        ):
            try:
                start_time = datetime.now()
                download_status.ticker_ohlc_cleanup_in_progress = True
                sess.commit()

                cleanup_folders(self.base_path)

                logging.info(
                    "finished cleaning up downloaded tickers, duration: %s sec"
                    % (datetime.now() - start_time).seconds
                )

            except Exception as e:
                logging.exception("Exception: %s", e)

        download_status.ticker_ohlc_cleanup_in_progress = False
        download_status.ticker_ohlc_last_cleanup = datetime.now()
        sess.commit()
        sess.close()


if __name__ == "__main__":
    downloader = Downloader()
    downloader.run(sys.argv[1])
