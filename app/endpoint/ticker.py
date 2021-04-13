import ast

from flask import (
    Blueprint,
    make_response,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_login import current_user, login_required

from app import cache
from app.account.account import Accounts
from app.ticker.ohlc import OHLC
from app.ticker.ticker import Tickers

ticker = Blueprint("ticker", __name__)


@ticker.route("/ticker")
@login_required
def get_ticker():
    if not session.get("ticker_data"):
        tickers = Tickers()

        if not tickers.ticker:
            return render_template(
                "ticker.html",
                ticker_present=False,
            )

        ticker = tickers.ticker

        session["ticker_data"] = {
            "ticker_name": ticker.ticker_name,
            "day": 0,
            "max_days": 15,
        }

        session["order_data"] = {
            "ticker_name": ticker.ticker_name,
            "order_placed": False,
            "exited_trade": False,
        }

    return render_template(
        "ticker.html",
        ticker_present=True,
        ticker_data=session.get("ticker_data"),
        order_data=session.get("order_data"),
    )


@ticker.route("/new-ticker")
@login_required
def new_ticker():
    tickers = Tickers()

    if not tickers.ticker:
        return render_template(
            "ticker.html",
            ticker_present=False,
        )

    ticker = tickers.ticker

    session["ticker_data"] = {
        "ticker_name": ticker.ticker_name,
        "day": 0,
        "max_days": 15,
    }

    session["order_data"] = {
        "ticker_name": ticker.ticker_name,
        "order_placed": False,
        "exited_trade": False,
    }

    return redirect(url_for("ticker.get_ticker"))


@ticker.route("/ticker.json")
@login_required
def get_ticker_ohcl():
    interval = request.args.get("interval")
    next = request.args.get("next")

    ticker_data = session.get("ticker_data")
    ticker_name = ticker_data.get("ticker_name")
    holdout_period = max(ticker_data.get("max_days") - ticker_data.get("day"), 0)

    if next and holdout_period >= 0:
        ticker_data["day"] = min(
            ticker_data.get("day") + 1, ticker_data.get("max_days")
        )
        session["ticker_data"] = ticker_data
        holdout_period = max(holdout_period - 1, 0)

    cache_key = "ticker-info-%s-%s-%s" % (ticker_name, interval, holdout_period)
    result = cache.get(cache_key)
    if result:
        return result
    else:
        tickers = Tickers(ticker_name)
        ohlc = OHLC(tickers.ticker)

        order_data = session.get("order_data")
        order_data.update(
            {
                "holdout_period": holdout_period,
            }
        )
        session["order_data"] = order_data

        if order_data.get("order_placed") and not order_data.get("exited_trade"):
            acc = Accounts(current_user)
            df = ohlc.get_ticker_ohlc("60min", holdout_period)
            acc.process_order(order_data, df)

        df = ohlc.get_ticker_ohlc(interval, holdout_period, order_data)
        result = df.reset_index().to_json(orient="records", date_format="iso")

        cache.set(cache_key, result)

    return result


@ticker.route("/ticker-info.json")
@login_required
def get_ticker_data():
    ticker_data = session.get("ticker_data")
    ticker_name = ticker_data.get("ticker_name")
    holdout_period = max(ticker_data.get("max_days") - ticker_data.get("day"), 0)

    cache_key = "ticker-info-%s-%s" % (ticker_name, holdout_period)
    result = cache.get(cache_key)
    if result:
        return result
    else:
        tickers = Tickers(ticker_name)
        ohlc = OHLC(tickers.ticker)

        df = ohlc.get_ticker_ohlc("60min", holdout_period)
        info = tickers.get_ticker_info(df.last_valid_index())
        cache.set(cache_key, info)

    return info


@ticker.route("/place-order", methods=["POST"])
@login_required
def place_order():
    order_data = session.get("order_data")
    if not order_data.get("order_placed"):
        acc = Accounts(current_user)

        try:
            order = ast.literal_eval(request.data.decode("UTF-8"))
            (
                order_type,
                entry_price,
                order_size,
                take_profit,
                stop_loss,
            ) = acc.validate_order(
                order.get("orderType"),
                0
                if order.get("orderType") == "SHORT"
                else round(float(order.get("price")), 3),
                int(order.get("orderSize")),
                round(float(order.get("takeProfit")), 3),
                round(float(order.get("stopLoss")), 3),
            )
        except ValueError as e:
            return make_response({"message": str(e)}, 400)

        ticker_data = session.get("ticker_data")
        ticker_name = ticker_data.get("ticker_name")
        holdout_period = ticker_data.get("max_days") - ticker_data.get("day")

        tickers = Tickers(ticker_name)
        ohlc = OHLC(tickers.ticker)

        df = ohlc.get_ticker_ohlc("60min", holdout_period)
        full_df = ohlc.get_ticker_ohlc("60min", 0)

        order_data.update(
            {
                "order_placed": True,
                "order_type": order_type,
                "entry_price": entry_price,
                "order_size": order_size,
                "take_profit": take_profit,
                "stop_loss": stop_loss,
                "entry_date": df.index[-1],
                "baseline_prices": (
                    df[["open", "high", "low", "close"]].iloc[-1].min(),
                    full_df[["open", "high", "low", "close"]].iloc[-1].max(),
                ),
            }
        )
        session["order_data"] = order_data
        acc.place_order(order_data, df)

        return make_response({"message": "Order submitted."}, 200)

    else:
        return make_response({"message": "Order already submitted."}, 200)


@ticker.route("/exit-trade")
@login_required
def exit_trade():
    order_data = session.get("order_data")
    if order_data.get("order_placed") and not order_data.get("exited_trade"):
        acc = Accounts(current_user)

        ticker_data = session.get("ticker_data")
        ticker_name = ticker_data.get("ticker_name")
        holdout_period = ticker_data.get("max_days") - ticker_data.get("day")

        tickers = Tickers(ticker_name)
        ohlc = OHLC(tickers.ticker)
        df = ohlc.get_ticker_ohlc("60min", holdout_period)

        order_data.update({"exit": True})
        session["order_data"] = order_data

        acc.process_order(order_data, df)

        return make_response({"message": "Order exited."}, 200)

    else:
        return make_response({"message": "Order not placed or already exited."}, 200)
