import json
import os
import pickle
import random
import shutil
from datetime import datetime
from io import BytesIO
from os import path

import backoff
import numpy as np
import pandas as pd
import requests
from dateutil.relativedelta import relativedelta
from finvizfinance.quote import finvizfinance

from app.utils.utils import subtract_months_from_date


def get_ticker_info(base_path, ticker):
    downloaded = False
    info = {"news": "", "overview": ""}

    ticker_info = get_finvizfinance(ticker.ticker_name)
    try:
        ratings_df = ticker_info.TickerOuterRatings()
    except:
        ratings_df = pd.DataFrame()

    try:
        news_df = ticker_info.TickerNews()
    except:
        news_df = pd.DataFrame()

    try:
        insider_df = ticker_info.TickerInsideTrader()
    except:
        insider_df = pd.DataFrame()

    if "Date" in ratings_df.columns:
        ratings_df["Date"] = ratings_df["Date"].dt.date

    if "Date" in news_df.columns:
        news_df["Date"] = news_df["Date"].dt.date

    if "Date" in insider_df.columns:
        insider_df["Date"] = pd.to_datetime(insider_df["Date"], format="%b %d").dt.date

    df = pd.concat([ratings_df, news_df, insider_df])

    overview = {}
    financials = {
        "overview": "OVERVIEW",
        "incomeStatement": "INCOME_STATEMENT",
        "balanceSheet": "BALANCE_SHEET",
        "cashFlow": "CASH_FLOW",
    }
    for key, value in financials.items():
        data_url = (
            "https://www.alphavantage.co/query?function=%s&symbol=%s&apikey=%s"
            % (value, ticker.ticker_name, alphavantage_api_key())
        )

        resp = get_alphavantage_data(data_url)
        overview.update({key: json.loads(resp.content)})

    if overview.get("overview").get("Name") and not df.empty and "Date" in df.columns:
        df.set_index(
            pd.DatetimeIndex(df["Date"]),
            inplace=True,
        )
        df.sort_index(ascending=False, inplace=True)
        df = df.drop(columns=["Date"], axis=1)

        info["news"] = df.reset_index().to_dict(orient="records")
        info["overview"] = overview

        save_ticker_info(base_path, ticker, info)
        downloaded = True

    return downloaded


def get_ticker_ohlc(base_path, ticker):
    dir_path = path.join(base_path, ticker.date_added.strftime("%d-%m-%Y"))

    data_url = (
        "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=%s&outputsize=full&datatype=csv&apikey=%s"
        % (ticker.ticker_name, alphavantage_api_key())
    )
    resp = get_alphavantage_data(data_url)
    daily_df = pd.read_csv(BytesIO(resp.content), index_col=0)

    # rename index
    daily_df.index.name = "time"

    # sort by time index
    daily_df.sort_index(inplace=True)

    # store last 2 years
    daily_df = daily_df[
        daily_df.index >= subtract_months_from_date(daily_df.last_valid_index(), 18)
    ]

    # Adjust for splits and dividends
    daily_df = adjust_ohlc_for_dividends_and_split(
        daily_df, ["open", "high", "low", "close"]
    )

    # reset time index to column before save
    daily_df.reset_index(inplace=True)

    # Store ticker data
    ticker_ohlc_path = path.join(dir_path, ticker.ticker_name + "_1d")
    daily_df.to_feather(ticker_ohlc_path)

    for interval in ["15min", "60min"]:
        intraday_df = pd.DataFrame()

        time_slice = []
        for i, j in [(i, j) for i in range(1, 2) for j in range(1, 3)]:
            time_slice.append("year%dmonth%d" % (i, j))

        data_urls = []
        for i, slice in enumerate(time_slice):
            data_urls.append(
                "https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY_EXTENDED&symbol=%s&interval=%s&slice=%s&apikey=%s"
                % (
                    ticker.ticker_name,
                    interval,
                    slice,
                    alphavantage_api_key(),
                )
            )
        for data_url in data_urls:
            resp = get_alphavantage_data(data_url)
            intraday_slice_df = pd.read_csv(BytesIO(resp.content), index_col=0)
            intraday_df = intraday_df.append(intraday_slice_df)

        # sort by time index
        intraday_df.sort_index(inplace=True)
        # reset time index to column before save
        intraday_df.reset_index(inplace=True)

        # Store ticker data
        ticker_ohlc_path = path.join(dir_path, ticker.ticker_name + "_" + interval)
        intraday_df.to_feather(ticker_ohlc_path)


def cleanup_folders(base_path):
    folder_date = (datetime.now() - relativedelta(days=7)).date()
    for dir in os.listdir(base_path):
        if os.path.isdir(dir) and datetime.strptime(dir, "%Y-%m-%d") < folder_date:
            dir_path = path.join(base_path, dir)
            shutil.rmtree(dir_path)


def save_ticker_info(base_path, ticker, info):
    dir_path = path.join(base_path, ticker.date_added.strftime("%d-%m-%Y"))
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)

    ticker_info_path = path.join(dir_path, ticker.ticker_name + "_info")
    with open(ticker_info_path, "xb") as f:
        pickle.dump(info, f)


def alphavantage_api_key():
    api_keys = [
        "GGW3SH4C64RDZ3B0",
        "6TSSQK5WX9EO9YUG",
        "SVJBVSR16G5VNSJ5",
        "I8EZZM4OQ8RAUZMW",
        "RTPA7UO4ZFNR8VKZ",
        "J54PXNMMH1PNUPK9",
    ]

    return random.choice(api_keys)


@backoff.on_predicate(
    backoff.constant,
    lambda result: type(result) is Exception,
    interval=5,
    max_tries=5,
)
def get_finvizfinance(ticker_name):
    return finvizfinance(ticker_name)


@backoff.on_predicate(
    backoff.constant,
    lambda req: str(req.content).find("Thank you for using Alpha Vantage!") != -1,
    interval=20,
)
def get_alphavantage_data(data_url):
    return requests.get(data_url, timeout=(2, 5))


def adjust_ohlc_for_dividends_and_split(df, columns):
    """Vectorized approach for calculating the adjusted prices for the specified columns
    with formula used is from blogpost:
    https://joshschertz.com/2016/08/27/Vectorizing-Adjusted-Close-with-Python/

    A0 = A1 + A1 * ((P0 / S) - P1 - D1) / P1

    The formula works on descending time series and starts on first row,
    since for the 0th row actual closing price and the adjusted closing price are the same.
    """
    dividend_col = df["dividend_amount"].values
    split_col = df["split_coefficient"].values

    for column in columns:
        price_col = df[column].values
        adj_price_col = np.zeros(len(df.index))
        adj_price_col[0] = price_col[0]

        for i in range(1, len(price_col)):
            adj_price_col[i] = round(
                (
                    adj_price_col[i - 1]
                    + (
                        adj_price_col[i - 1]
                        * (
                            (
                                (price_col[i] / split_col[i - 1])
                                - price_col[i - 1]
                                - dividend_col[i - 1]
                            )
                            / price_col[i - 1]
                        )
                    )
                ),
                4,
            )

        df.update(pd.Series(adj_price_col, name=column, index=df.index))

    return df
