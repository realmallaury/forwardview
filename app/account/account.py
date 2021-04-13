from flask import session

from app.db import db
from app.db.models import Account, Order


class Accounts:
    def __init__(self, user):
        self.accounts = db.session.query(Account).filter(Account.id == user.id).all()
        if not self.accounts:
            account = Account(
                user_id=user.id,
                active=True,
                initial_amount=10000.00,
                current_amount=10000.00,
                return_ptc=0,
            )
            db.session.add(account)
            db.session.commit()
            self.accounts = [account]

        self.current_account = (
            db.session.query(Account)
            .filter(Account.id == user.id and Account.active is True)
            .one()
        )
        self.current_account_total = self.current_account.current_amount

    def get_accounts(self):
        return self.accounts

    def place_order(self, order_data, df):
        if order_data.get("order_type") == "LONG":
            entry_price = round(float(order_data.get("entry_price")), 3)
        else:
            entry_price = round(df[["open", "high", "low", "close"]].iloc[-1].min(), 3)

        order = Order(
            account_id=self.current_account.id,
            ticker_name=order_data.get("ticker_name"),
            order_type=order_data.get("order_type"),
            entry_price=entry_price,
            exit_price=0,
            order_size=int(order_data.get("order_size")),
            take_profit=float(order_data.get("take_profit")),
            stop_loss=float(order_data.get("stop_loss")),
            account_total=self.current_account_total,
            profit_loss=0,
            risk=1,
            risk_as_percentage_of_account=0,
            baseline_profit_loss=0,
            order_filled=False,
            exited_trade=False,
        )

        db.session.add(order)
        db.session.commit()

        self.process_order(order_data, df)

    def process_order(self, order_data, df):
        if order_data.get("order_type") == "LONG":
            self._process_long_order(order_data, df)
        else:
            self._process_short_order(order_data, df)

    def _process_long_order(self, order_data, df):
        if order_data.get("order_placed"):
            order = (
                db.session.query(Order)
                .filter(Order.account_id == self.current_account.id)
                .order_by(Order.id.desc())
                .first()
            )

            price = order.entry_price
            account_total = order.account_total
            order_size = order.order_size
            take_profit = order.take_profit
            stop_loss = order.stop_loss

            baseline_prices = order_data.get("baseline_prices")

            df = df[df.index >= order_data.get("entry_date")]
            for date, row in df.iterrows():
                current_prices = [
                    round(row["open"], 3),
                    round(row["high"], 3),
                    round(row["low"], 3),
                    round(row["close"], 3),
                ]

                if not order.order_filled:
                    if min(current_prices) <= price:
                        order.entry_date = date
                        order.risk = round((price - stop_loss) * order_size, 3)
                        order.risk_as_percentage_of_account = round(
                            (order.risk / order.account_total) * 100, 2
                        )
                        order.account_total = round(
                            account_total - price * order_size, 3
                        )
                        order.order_filled = True
                        order_data.update(
                            {
                                "entry_date": date,
                                "order_filled": order.order_filled,
                            }
                        )
                        session["order_data"] = order_data

                if order.order_filled and not order.exited_trade:
                    if max(current_prices) >= take_profit:
                        order.profit_loss = round((take_profit - price) * order_size, 3)
                        order.account_total = round(
                            account_total + (take_profit * order_size), 3
                        )
                        order.exit_date = date
                        order.exit_price = round(take_profit, 3)
                        order.update_baseline_profit_loss(baseline_prices)
                        order.exited_trade = True
                        break

                    elif min(current_prices) <= stop_loss:
                        order.profit_loss = round((stop_loss - price) * order_size, 3)
                        order.account_total = round(
                            account_total + (stop_loss * order_size), 3
                        )
                        order.exit_date = date
                        order.exit_price = round(stop_loss, 3)
                        order.update_baseline_profit_loss(baseline_prices)
                        order.exited_trade = True
                        break

            if (
                order.order_filled
                and not order.exited_trade
                and (order_data.get("holdout_period") == 0 or order_data.get("exit"))
            ):
                end_price = df[["open", "high", "low", "close"]].iloc[-1].max()
                order.profit_loss = round((end_price - price) * order_size, 3)
                order.account_total = round(account_total + (end_price * order_size), 3)
                order.exit_date = df.last_valid_index()
                order.exit_price = round(end_price, 3)
                order.update_baseline_profit_loss(baseline_prices)
                order.exited_trade = True

            if order.exited_trade:
                order_data.update(
                    {
                        "exited_trade": order.exited_trade,
                        "exit_date": order.exit_date,
                    }
                )
                session["order_data"] = order_data
                self.current_account.update_current_amount_and_return(
                    order.account_total
                )

            db.session.commit()

    def _process_short_order(self, order_data, df):
        if order_data.get("order_placed"):
            order = (
                db.session.query(Order)
                .filter(Order.account_id == self.current_account.id)
                .order_by(Order.id.desc())
                .first()
            )

            price = order.entry_price
            account_total = order.account_total
            order_size = order.order_size
            take_profit = order.take_profit
            stop_loss = order.stop_loss

            baseline_prices = order_data.get("baseline_prices")

            df = df[df.index >= order_data.get("entry_date")]
            for date, row in df.iterrows():
                current_prices = [
                    round(row["open"], 3),
                    round(row["high"], 3),
                    round(row["low"], 3),
                    round(row["close"], 3),
                ]

                if not order.order_filled:
                    order.entry_date = date
                    order.risk = round((stop_loss - price) * order_size, 3)
                    order.risk_as_percentage_of_account = round(
                        (order.risk / order.account_total) * 100, 2
                    )
                    order.account_total = round(account_total + price * order_size, 3)
                    order.order_filled = True
                    order_data.update(
                        {
                            "entry_date": date,
                            "order_filled": order.order_filled,
                        }
                    )
                    session["order_data"] = order_data

                if order.order_filled and not order.exited_trade:
                    if max(current_prices) >= stop_loss:
                        order.profit_loss = round((price - stop_loss) * order_size, 3)
                        order.account_total = round(
                            account_total - (stop_loss * order_size), 3
                        )
                        order.exit_date = date
                        order.exit_price = round(stop_loss, 3)
                        order.update_baseline_profit_loss(baseline_prices)
                        order.exited_trade = True
                        break

                    elif min(current_prices) <= take_profit:
                        order.profit_loss = round((price - take_profit) * order_size, 3)
                        order.account_total = round(
                            account_total - (take_profit * order_size), 3
                        )
                        order.exit_date = date
                        order.exit_price = round(take_profit, 3)
                        order.update_baseline_profit_loss(baseline_prices)
                        order.exited_trade = True
                        break

            if (
                order.order_filled
                and not order.exited_trade
                and (order_data.get("holdout_period") == 0 or order_data.get("exit"))
            ):
                end_price = df[["open", "high", "low", "close"]].iloc[-1].min()
                order.profit_loss = round((price - end_price) * order_size, 3)
                order.account_total = round(account_total - (end_price * order_size), 3)
                order.exit_date = df.last_valid_index()
                order.exit_price = round(end_price, 3)
                order.update_baseline_profit_loss(baseline_prices)
                order.exited_trade = True

            if order.exited_trade:
                order_data.update(
                    {
                        "exited_trade": order.exited_trade,
                        "exit_date": order.exit_date,
                    }
                )
                session["order_data"] = order_data
                self.current_account.update_current_amount_and_return(
                    order.account_total
                )

            db.session.commit()

    def validate_order(
        self, order_type, entry_price, order_size, take_profit, stop_loss
    ):
        if order_type not in ["LONG", "SHORT"]:
            raise ValueError("Order type should be LONG or SHORT.")

        if order_size < 1:
            raise ValueError("Order size should be > 0")
        if take_profit < 0 or stop_loss < 0:
            raise ValueError("Take profit and stop loss should be > 0.")

        if order_type == "SHORT":
            entry_price = 0
            if take_profit >= stop_loss:
                raise ValueError("SHORT: take profit should be less then stop loss.")
        elif order_type == "LONG":
            if take_profit <= stop_loss:
                raise ValueError("LONG: take profit should be greater then stop loss.")

            if self.current_account_total < (order_size * entry_price):
                raise ValueError("LONG: total order is greater that current account.")

        return order_type, entry_price, order_size, take_profit, stop_loss
