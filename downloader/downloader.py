import asyncio
import logging
import os
import random
from datetime import datetime
from os import environ
from os import path

import aiocron
from dateutil.relativedelta import relativedelta
from dotenv import dotenv_values
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from app.db.models import DownloadStatus, Ticker
from download_ticker_list import get_ticker_list, cleanup_tickers
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
        self.loop = asyncio.new_event_loop()

        os.chdir(os.path.dirname(os.getcwd()))
        config = dotenv_values(path.join(os.getcwd(), ".env"))
        if not config:
            config = {
                "SQLALCHEMY_DATABASE_URI": environ.get("SQLALCHEMY_DATABASE_URI"),
                "DATA_DIR": environ.get("DATA_DIR"),
            }

        flask_app = Flask(__name__)
        flask_app.config["SQLALCHEMY_DATABASE_URI"] = config.get(
            "SQLALCHEMY_DATABASE_URI"
        )
        flask_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        self.db = SQLAlchemy(flask_app)
        self.base_path = config.get("DATA_DIR")

        self.download_status = self.db.session.query(DownloadStatus).first()
        if not self.download_status:
            self.download_status = DownloadStatus()
            self.db.session.add(self.download_status)
            self.db.session.commit()
            self.db.session.flush()

    async def run(self):
        aiocron.crontab("* * * * *", func=self.get_ticker_info_periodic, start=True)
        aiocron.crontab("* * * * *", func=self.clean_tickers_periodic, start=True)
        aiocron.crontab("* * * * *", func=self.get_ticker_data_periodic, start=True)
        aiocron.crontab("* * * * *", func=self.cleanup_folders_periodic, start=True)

        while True:
            await asyncio.sleep(1)

    async def get_ticker_info_periodic(self):
        """
        once every 2 hours get new ticker list
        """
        if (
            not self.download_status.ticker_list_last_download
            or (
                datetime.now() - self.download_status.ticker_list_last_download
            ).total_seconds()
            > 2 * 60 * 60
        ):
            # if there is error dont update ticker_list_last_download and try again
            try:
                start_time = datetime.now()
                get_ticker_list(self.db)
                logging.info(
                    "finished downloading ticker list at: %s, duration: %s sec"
                    % (datetime.now(), (datetime.now() - start_time).seconds)
                )

                self.download_status.ticker_list_last_download = datetime.now()
                self.db.session.commit()
                self.db.session.flush()
            except Exception as e:
                logging.exception("Exception: %s", e)
                return

    async def clean_tickers_periodic(self):
        """
        once every 2 hours check for tickers to cleanup
        """
        if (
            (
                self.download_status.ticker_list_last_download
                and not self.download_status.ticker_list_last_update
            )
        ) or (
            datetime.now() - self.download_status.ticker_list_last_update
        ).total_seconds() > 2 * 60 * 60:
            # if there is error dont update ticker_list_last_update and try again
            try:
                start_time = datetime.now()
                query_date = (datetime.now() - relativedelta(days=1)).date()
                # tickers that are older than 3 days and are not downloaded
                cleanup_tickers(self.db, query_date, False)

                query_date = (datetime.now() - relativedelta(days=3)).date()
                # tickers that are older than 7 days and are downloaded
                cleanup_tickers(self.db, query_date, True)

                self.download_status.ticker_list_last_update = datetime.now()
                self.db.session.commit()
                self.db.session.flush()
                logging.info(
                    "finished cleaning up ticker list at: %s, duration: %s sec"
                    % (datetime.now(), (datetime.now() - start_time).seconds)
                )
            except Exception as e:
                logging.exception("Exception: %s", e)
                return

    async def get_ticker_data_periodic(self):
        """
        once every minute download new ticker
        """
        if (
            self.download_status.ticker_list_last_download
            and not self.download_status.ticker_ohlc_last_download
        ) or (
            datetime.now() - self.download_status.ticker_ohlc_last_download
        ).total_seconds() > 60:
            # if there is error dont update ticker_list_last_download and try again
            try:
                tickers = (
                    self.db.session.query(Ticker)
                    .filter(Ticker.downloaded == False)
                    .all()
                )
                ticker = random.choice(tickers)

                if ticker:
                    start_time = datetime.now()
                    downloaded = get_ticker_info(self.base_path, ticker)
                    if downloaded:
                        get_ticker_ohlc(self.base_path, ticker)
                        ticker.date_added = datetime.now()
                        ticker.downloaded = True
                        self.download_status.ticker_ohlc_last_download = datetime.now()
                    else:
                        self.db.session.delete(ticker)

                    self.db.session.commit()
                    self.db.session.flush()
                    logging.info(
                        "finished downloading ticker list at: %s, duration: %s sec"
                        % (datetime.now(), (datetime.now() - start_time).seconds)
                    )
            except Exception as e:
                logging.exception("Exception: %s", e)
                return

    async def cleanup_folders_periodic(self):
        """
        once every 24 hours clean old folders
        """
        if (
            self.download_status.ticker_list_last_download
            and not self.download_status.ticker_ohlc_last_update
        ) or (
            datetime.now() - self.download_status.ticker_ohlc_last_update
        ).total_seconds() > 24 * 60 * 60:
            # if there is error dont update ticker_list_last_download and try again
            try:
                start_time = datetime.now()
                cleanup_folders(self.base_path)

                self.download_status.ticker_ohlc_last_update = datetime.now()
                self.db.session.flush()
                logging.info(
                    "finished cleaning up downloaded tickers at: %s, duration: %s sec"
                    % (datetime.now(), (datetime.now() - start_time).seconds)
                )
            except Exception as e:
                logging.exception("Exception: %s", e)
                return


d = Downloader()
asyncio.run(d.run())
