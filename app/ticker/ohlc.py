import pandas as pd

from app.ticker.indicators import atr, keltner_channel, macd
from flask import current_app


class OHLC:
    """OHLC reads serialized OHLC data."""

    def __init__(
        self,
        ticker,
    ):
        """Initialize OHLC object and populate dataframes."""
        self.base_path = current_app.config.get("DATA_DIR")
        self.ticker = ticker

        self.intraday_15min_df = self._read_ticker_ohlc("15min")
        self.intraday_60min_df = self._read_ticker_ohlc("60min")
        self.daily_df = self._read_ticker_ohlc("1d")

    def get_ticker_ohlc(self, interval, holdout_period, order_data=None):
        if interval == "15min":
            df = self.intraday_15min_df.copy()
        elif interval == "60min":
            df = self.intraday_60min_df.copy()
        elif interval == "1d":
            df = self.daily_df.copy()
        else:
            df = self.intraday_60min_df.copy()

        working_dates = self._get_no_of_working_dates(df)
        cutoff_date = pd.to_datetime(
            working_dates[len(working_dates) - 1 - holdout_period]
        )

        df = df[df.index < cutoff_date]
        df = self._add_indicators_to_ticker_ohlc(df)

        if order_data:
            df = self._take_profit_stop_loss_band(df, order_data)

        if df.size > 200:
            df = df.tail(200)

        return df

    def _read_ticker_ohlc(self, interval):
        ticker_ohlc_path = "%s/%s/%s_%s" % (
            self.base_path,
            self.ticker.date_added.strftime("%d-%m-%Y"),
            self.ticker.ticker_name,
            interval,
        )

        df = pd.read_feather(ticker_ohlc_path)
        df.set_index(
            pd.DatetimeIndex(df["time"]),
            inplace=True,
        )
        df.sort_index(ascending=True, inplace=True)
        df = df.drop(columns=["time"], axis=1)

        return df

    def _get_no_of_working_dates(self, df):
        dates = list(
            set([d.date() for d in list(df.sort_index(ascending=True).index.tolist())])
        )
        dates.sort()

        return dates

    def _add_indicators_to_ticker_ohlc(self, df):
        df = macd(df, fast_window=10, slow_window=3, signal_window=16)
        df = atr(df, window=14)
        df = keltner_channel(df, 20)

        return df

    def _take_profit_stop_loss_band(self, df, order_data):
        if order_data.get("order_filled"):
            start_date = order_data.get("entry_date")

            if order_data.get("exited_trade"):
                end_date = order_data.get("exit_date")
            else:
                end_date = df.last_valid_index()

            date_mask = (start_date <= df.index) & (df.index <= end_date)
            df.loc[date_mask, "TAKE_PROFIT"] = order_data.get("take_profit")
            df.loc[date_mask, "STOP_LOSS"] = order_data.get("stop_loss")

        return df


# import json
# import os
# import pickle
# import random
# from io import BytesIO
#
# import backoff
# import numpy as np
# import pandas as pd
# import requests
#
# from app.ticker.indicators import macd, atr, keltner_channel
# from app.utils.utils import subtract_months_from_date
#
#
# class OHLC:
#     """OHLC downloads and adjusts OHLC data for specified ticker through alpha vantage api."""
#
#     def __init__(
#         self,
#         ticker_name,
#     ):
#         """Initialize OHLC object and populate dataframes."""
#         self.base_path = os.path.abspath(os.getcwd())
#         self.ticker_name = ticker_name
#
#         self.api_keys = [
#             "GGW3SH4C64RDZ3B0",
#             "6TSSQK5WX9EO9YUG",
#             "SVJBVSR16G5VNSJ5",
#             "I8EZZM4OQ8RAUZMW",
#             "RTPA7UO4ZFNR8VKZ",
#             "J54PXNMMH1PNUPK9",
#         ]
#
#         self.intraday_15min_df = self._read_intraday_ticker_ohlc("15min")
#         self.intraday_60min_df = self._read_intraday_ticker_ohlc("60min")
#         self.daily_df = self._read_ticker_ohlc("1d")
#         self.overview = self._read_ticker_overview()
#
#     def get_ticker_ohlc(self, interval, holdout_period, order_data=None):
#         if interval == "15min":
#             df = self.intraday_15min_df.copy()
#             df = df.tail(600)
#         elif interval == "60min":
#             df = self.intraday_60min_df.copy()
#             df = df.tail(270)
#         elif interval == "1d":
#             df = self.daily_df.copy()
#             df = df.tail(210)
#         else:
#             df = self.intraday_60min_df.copy()
#
#         working_dates = self._get_no_of_working_dates(df)
#         cutoff_date = pd.to_datetime(
#             working_dates[len(working_dates) - 1 - holdout_period]
#         )
#
#         df = df[df.index < cutoff_date]
#         df = self._add_indicators_to_ticker_ohlc(df)
#
#         if order_data:
#             df = self._take_profit_stop_loss_band(df, order_data)
#
#         return df
#
#     def get_ticker_overview(self):
#         return self.overview
#
#     def _get_no_of_working_dates(self, df):
#         dates = list(
#             set([d.date() for d in list(df.sort_index(ascending=True).index.tolist())])
#         )
#         dates.sort()
#         return dates
#
#     def _read_ticker_ohlc(self, interval):
#         serialized_daily_ticker_ohlc_path = (
#             self.base_path + "/data/" + self.ticker_name + "_" + interval
#         )
#
#         if not os.path.exists(serialized_daily_ticker_ohlc_path):
#             daily_df = self._download_and_store_ticker_ohlc(
#                 serialized_daily_ticker_ohlc_path
#             )
#         else:
#             daily_df = pd.read_feather(serialized_daily_ticker_ohlc_path)
#
#         daily_df.set_index(
#             pd.DatetimeIndex(daily_df["time"]),
#             inplace=True,
#         )
#         daily_df.sort_index(ascending=True, inplace=True)
#         daily_df = daily_df.drop(columns=["time"], axis=1)
#
#         return daily_df
#
#     def _read_intraday_ticker_ohlc(self, interval):
#         serialized_intraday_ticker_ohlc_path = (
#             self.base_path + "/data/" + self.ticker_name + "_intraday_" + interval
#         )
#
#         if not os.path.exists(serialized_intraday_ticker_ohlc_path):
#             intraday_df = self._download_and_store_intraday_ticker_ohlc(
#                 serialized_intraday_ticker_ohlc_path, interval
#             )
#         else:
#             intraday_df = pd.read_feather(serialized_intraday_ticker_ohlc_path)
#
#         intraday_df.set_index(
#             pd.DatetimeIndex(intraday_df["time"]),
#             inplace=True,
#         )
#         intraday_df.sort_index(ascending=True, inplace=True)
#         intraday_df = intraday_df.drop(columns=["time"], axis=1)
#
#         return intraday_df
#
#     def _read_ticker_overview(self):
#         serialized_ticker_overview_path = (
#             self.base_path + "/data/" + self.ticker_name + "_overview"
#         )
#
#         if not os.path.exists(serialized_ticker_overview_path):
#             overview = self._download_and_store_ticker_overview(
#                 serialized_ticker_overview_path
#             )
#         else:
#             with open(serialized_ticker_overview_path, "rb") as f:
#                 overview = pickle.load(f)
#
#         return overview
#
#     def _add_indicators_to_ticker_ohlc(self, df):
#         df = macd(df, fast_window=10, slow_window=3, signal_window=16)
#         df = atr(df, window=14)
#         df = keltner_channel(df, 20)
#
#         return df
#
#     def _take_profit_stop_loss_band(self, df, order_data):
#         if order_data.get("order_filled"):
#             start_date = order_data.get("entry_date")
#
#             if order_data.get("exited_trade"):
#                 end_date = order_data.get("exit_date")
#             else:
#                 end_date = df.last_valid_index()
#
#             date_mask = (start_date <= df.index) & (df.index <= end_date)
#             df.loc[date_mask, "TAKE_PROFIT"] = order_data.get("take_profit")
#             df.loc[date_mask, "STOP_LOSS"] = order_data.get("stop_loss")
#
#         return df
#
#     def _download_and_store_ticker_ohlc(self, serialized_daily_ticker_data_path):
#         data_url = (
#             "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=%s&outputsize=full&datatype=csv&apikey=%s"
#             % (self.ticker_name, self.api_keys[random.randint(0, 5)])
#         )
#         resp = self._get_data(data_url)
#         daily_df = pd.read_csv(BytesIO(resp.content), index_col=0)
#
#         # rename index
#         daily_df.index.name = "time"
#
#         # sort by time index
#         daily_df.sort_index(inplace=True)
#
#         # store last 2 years
#         daily_df = daily_df[
#             daily_df.index >= subtract_months_from_date(daily_df.last_valid_index(), 18)
#         ]
#
#         # Adjust for splits and dividends
#         daily_df = self._adjust_ohlc_for_dividends_and_split(
#             daily_df, ["open", "high", "low", "close"]
#         )
#
#         # reset time index to column before save
#         daily_df.reset_index(inplace=True)
#         # Store daily ticker data
#         daily_df.to_feather(serialized_daily_ticker_data_path)
#
#         return daily_df
#
#     def _download_and_store_intraday_ticker_ohlc(
#         self, serialized_intraday_ticker_data_path, interval
#     ):
#         """Download and store adjusted daily ticker data"""
#         intraday_df = pd.DataFrame()
#
#         for data_url in self._get_intraday_ohlc_urls(interval):
#             resp = self._get_data(data_url)
#
#             intraday_slice_df = pd.read_csv(BytesIO(resp.content), index_col=0)
#             intraday_df = intraday_df.append(intraday_slice_df)
#
#         # sort by time index
#         intraday_df.sort_index(inplace=True)
#         # reset time index to column before save
#         intraday_df.reset_index(inplace=True)
#         # Store daily ticker data
#         intraday_df.to_feather(serialized_intraday_ticker_data_path)
#
#         return intraday_df
#
#     def _download_and_store_ticker_overview(self, serialized_ticker_overview_path):
#         overview = {}
#         financials = {"overview": "OVERVIEW", "incomeStatement": "INCOME_STATEMENT"}
#         for key, value in financials.items():
#             data_url = (
#                 "https://www.alphavantage.co/query?function=%s&symbol=%s&apikey=%s"
#                 % (value, self.ticker_name, self.api_keys[random.randint(0, 5)])
#             )
#
#             resp = self._get_data(data_url)
#             overview.update({key: json.loads(resp.content)})
#
#         with open(serialized_ticker_overview_path, "xb") as f:
#             pickle.dump(overview, f)
#
#         return overview
#
#     def _get_intraday_ohlc_urls(self, interval):
#         time_slice = []
#         for i, j in [(i, j) for i in range(1, 2) for j in range(1, 3)]:
#             time_slice.append("year%dmonth%d" % (i, j))
#
#         data_urls = []
#         for i, slice in enumerate(time_slice):
#             data_urls.append(
#                 "https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY_EXTENDED&symbol=%s&interval=%s&slice=%s&apikey=%s"
#                 % (self.ticker_name, interval, slice, self.api_keys[i % 6])
#             )
#
#         return data_urls
#
#     @backoff.on_predicate(
#         backoff.constant,
#         lambda req: str(req.content).find("Thank you for using Alpha Vantage!") != -1,
#         interval=70,
#     )
#     def _get_data(self, data_url):
#         return requests.get(data_url)
#
#     def _adjust_ohlc_for_dividends_and_split(self, df, columns):
#         """Vectorized approach for calculating the adjusted prices for the specified columns
#         with formula used is from blogpost:
#         https://joshschertz.com/2016/08/27/Vectorizing-Adjusted-Close-with-Python/
#
#         A0 = A1 + A1 * ((P0 / S) - P1 - D1) / P1
#
#         The formula works on descending time series and starts on first row,
#         since for the 0th row actual closing price and the adjusted closing price are the same.
#         """
#         dividend_col = df["dividend_amount"].values
#         split_col = df["split_coefficient"].values
#
#         for column in columns:
#             price_col = df[column].values
#             adj_price_col = np.zeros(len(df.index))
#             adj_price_col[0] = price_col[0]
#
#             for i in range(1, len(price_col)):
#                 adj_price_col[i] = round(
#                     (
#                         adj_price_col[i - 1]
#                         + (
#                             adj_price_col[i - 1]
#                             * (
#                                 (
#                                     (price_col[i] / split_col[i - 1])
#                                     - price_col[i - 1]
#                                     - dividend_col[i - 1]
#                                 )
#                                 / price_col[i - 1]
#                             )
#                         )
#                     ),
#                     4,
#                 )
#
#             df.update(pd.Series(adj_price_col, name=column, index=df.index))
#
#         return df
