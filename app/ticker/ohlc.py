import pandas as pd

from app import cache
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
        cache_key = "ticker-info-%s-%s" % (self.ticker.ticker_name, interval)
        df = cache.get(cache_key)
        if df is None:
            if interval == "15min":
                df = self.intraday_15min_df.copy()
            elif interval == "60min":
                df = self.intraday_60min_df.copy()
            elif interval == "1d":
                df = self.daily_df.copy()
            else:
                df = self.intraday_60min_df.copy()

            cache.set(cache_key, df)

        working_dates = self._get_no_of_working_dates(df)
        cutoff_date = pd.to_datetime(
            working_dates[len(working_dates) - 1 - holdout_period]
        )

        df = df[df.index < cutoff_date]
        df = self._add_indicators_to_ticker_ohlc(df)

        if df.size > 250:
            df = df.tail(250)

        if order_data:
            df = self._take_profit_stop_loss_band(df, order_data)

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

            max = df["KELTNER_HBAND"].max()
            min = df["KELTNER_LBAND"].min()

            if order_data.get("order_type") == "LONG":
                if max > order_data.get("take_profit"):
                    max = order_data.get("take_profit")

                if min < order_data.get("stop_loss"):
                    min = order_data.get("stop_loss")

            elif order_data.get("order_type") == "SHORT":
                if max > order_data.get("stop_loss"):
                    max = order_data.get("stop_loss")

                if min < order_data.get("take_profit"):
                    min = order_data.get("take_profit")

            date_mask = (start_date <= df.index) & (df.index <= end_date)
            df.loc[date_mask, "TAKE_PROFIT"] = max
            df.loc[date_mask, "STOP_LOSS"] = min

        return df
