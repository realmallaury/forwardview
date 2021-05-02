from flask_login import UserMixin
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from app.db import db


class User(UserMixin, db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(1000), nullable=False)


class Account(db.Model):
    __tablename__ = "account"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    active = db.Column(db.Boolean, default=True, nullable=False)
    initial_amount = db.Column(db.Float, default=0.0, nullable=False)
    current_amount = db.Column(db.Float, default=0.0, nullable=False)
    return_ptc = db.Column(db.Float, default=0.0, nullable=False)
    orders = db.relationship("Order", backref="account", lazy=False)

    def update_current_amount_and_return(self, amount):
        self.current_amount = amount
        self.return_ptc = round(
            (self.current_amount / self.initial_amount - 1) * 100,
            2,
        )


class Order(db.Model):
    __tablename__ = "order"
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey("account.id"))

    ticker_name = db.Column(db.String(100), nullable=False)
    order_type = db.Column(db.String(100), nullable=False)

    entry_date = db.Column(db.DateTime, nullable=True)
    entry_price = db.Column(db.Float, nullable=False)
    order_size = db.Column(db.Integer, nullable=False)

    exit_date = db.Column(db.DateTime, nullable=True)
    exit_price = db.Column(db.Float, nullable=False)

    take_profit = db.Column(db.Float, nullable=False)
    stop_loss = db.Column(db.Float, default=0.0, nullable=False)

    account_total = db.Column(db.Float, nullable=False)
    profit_loss = db.Column(db.Float, nullable=False)
    risk = db.Column(db.Float, nullable=False)
    risk_as_percentage_of_account = db.Column(db.Float, nullable=False)
    baseline_profit_loss = db.Column(db.Float, nullable=False)

    order_filled = db.Column(db.Boolean, default=False, nullable=False)
    exited_trade = db.Column(db.Boolean, default=False, nullable=False)

    def get_profit_loss_multiple_of_risk(self):
        return round(self.profit_loss / self.risk, 2)

    def update_baseline_profit_loss(self, baseline_prices):
        self.baseline_profit_loss = round(
            (baseline_prices[1] - baseline_prices[0]) * self.order_size, 3
        )


class OrderSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Order
        load_instance = True


class Ticker(db.Model):
    __tablename__ = "ticker"
    ticker_name = db.Column(db.String(100), primary_key=True)
    date_added = db.Column(db.DateTime, nullable=True)
    downloaded = db.Column(db.Boolean, default=False)


class TickerUser(db.Model):
    __tablename__ = "ticker_user"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    ticker_name = db.Column(db.String(100), nullable=False)


class DownloadStatus(db.Model):
    __tablename__ = "download_status"
    id = db.Column(db.Integer, primary_key=True)
    ticker_list_last_download = db.Column(db.DateTime, nullable=False)
    ticker_list_last_cleanup = db.Column(db.DateTime, nullable=False)
    ticker_ohlc_last_download = db.Column(db.DateTime, nullable=False)
    ticker_ohlc_last_cleanup = db.Column(db.DateTime, nullable=False)

    ticker_list_download_in_progress = db.Column(db.Boolean, default=False)
    ticker_list_cleanup_in_progress = db.Column(db.Boolean, default=False)
    ticker_ohlc_download_in_progress = db.Column(db.Boolean, default=False)
    ticker_ohlc_cleanup_in_progress = db.Column(db.Boolean, default=False)
