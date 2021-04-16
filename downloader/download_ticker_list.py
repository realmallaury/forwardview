from datetime import datetime

import backoff
from finvizfinance.quote import finvizfinance
from finvizfinance.screener.technical import Overview

from app.db.models import Ticker, TickerUser


def get_ticker_list(db):
    ticker_names = set()
    # for each signal get set of distinct ticker names
    for signal in signals():
        tickers_df = get_overview(signal)

        for ticker_name in tickers_df["Ticker"]:
            ticker_names.add(ticker_name)

    # get list of existing ticker
    ids = [id[0] for id in db.session.query(Ticker.ticker_name)]

    # add new tickers or update existing ones
    for ticker_name in list(ticker_names):
        stock_fundamentals = get_stock_fundamentals(ticker_name)
        if stock_fundamentals.get("Income") != "-":
            if ticker_name not in ids:
                db.session.add(
                    Ticker(
                        ticker_name=ticker_name,
                        date_added=datetime.now(),
                        downloaded=False,
                    )
                )
            else:
                db.session.query(Ticker).filter(
                    Ticker.ticker_name == ticker_name
                ).update(
                    {
                        Ticker.date_added: datetime.now(),
                        Ticker.downloaded: False,
                    }
                )

    db.session.commit()


def cleanup_tickers(db, query_date, ticker_download_status):
    for ticker_name in [
        id[0]
        for id in db.session.query(Ticker.ticker_name).filter(
            (Ticker.date_added < query_date)
            & (Ticker.downloaded == ticker_download_status)
        )
    ]:
        db.session.query(Ticker).filter(Ticker.ticker_name == ticker_name).delete()

        db.session.query(TickerUser).filter(
            TickerUser.ticker_name == ticker_name
        ).delete()

    db.session.commit()


def signals():
    return [
        "Upgrades",
        "Most Active",
        "Overbought",
        "Major News",
        "Horizontal S/R",
        "TL Support",
        "TL Resistance",
        "Wedge Up",
        "Wedge Down",
        "Channel Up",
        "Channel Down",
        "Double Top",
        "Double Bottom",
        "Triangle Ascending",
        "Triangle Descending",
    ]


@backoff.on_predicate(
    backoff.constant,
    lambda result: type(result) is Exception,
    interval=10,
    max_tries=5,
)
def get_overview(signal):
    overview = Overview()
    overview.set_filter(signal=signal)
    return overview.ScreenerView(verbose=0)


@backoff.on_predicate(
    backoff.constant,
    lambda result: type(result) is Exception,
    interval=10,
    max_tries=5,
)
def get_stock_fundamentals(ticker_name):
    stock = finvizfinance(ticker_name)
    return stock.TickerFundament()
