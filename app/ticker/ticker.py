import json
import pickle
import random

import pandas as pd
from flask_login import current_user
from sqlalchemy import exists

from app.db import db
from app.db.models import Ticker, TickerUser
from flask import current_app

from os import path


class Tickers:
    def __init__(self, ticker_name=None):
        self.base_path = current_app.config.get("DATA_DIR")
        if not ticker_name:
            self.ticker = self._get_random_ticker()
        else:
            self.ticker = self._get_ticker(ticker_name)

    def _get_random_ticker(self):
        tickers = (
            db.session.query(Ticker)
            .filter(
                Ticker.downloaded
                & ~exists().where(Ticker.ticker_name == TickerUser.ticker_name)
            )
            .all()
        )

        if not tickers:
            return None

        ticker = random.choice(tickers)
        db.session.add(
            TickerUser(user_id=current_user.id, ticker_name=ticker.ticker_name)
        )
        db.session.commit()
        db.session.flush()

        return ticker

    def _get_ticker(self, ticker_name):
        ticker = (
            db.session.query(Ticker).filter(Ticker.ticker_name == ticker_name).one()
        )

        return ticker

    def get_ticker_info(self, cutoff_date):
        start_date = cutoff_date - pd.Timedelta(days=30)

        dir_path = path.join(
            self.base_path, self.ticker.date_added.strftime("%d-%m-%Y")
        )

        ticker_info_path = path.join(dir_path, self.ticker.ticker_name + "_info")
        with open(ticker_info_path, "rb") as f:
            info = pickle.load(f)

        df = pd.DataFrame.from_dict(info.get("news"))
        df.set_index(
            pd.DatetimeIndex(df["Date"]),
            inplace=True,
        )
        df.sort_index(ascending=False, inplace=True)
        df = df.drop(columns=["Date"], axis=1)
        df = df[(start_date <= df.index) & (df.index <= cutoff_date)]

        info["news"] = json.loads(df.reset_index().to_json(orient="records"))
        return info
