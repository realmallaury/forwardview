from flask import Blueprint, render_template, jsonify
from flask_login import current_user, login_required

from app.account.account import Accounts

main = Blueprint("main", __name__)


@main.route("/")
@login_required
def index():
    acc = Accounts(current_user)
    accounts = acc.get_accounts()
    return render_template("index.html", name=current_user.name, accounts=accounts)


@main.route("/account")
@login_required
def account():
    acc = Accounts(current_user)
    accounts = acc.get_accounts()
    return render_template("account.html", name=current_user.name, accounts=accounts)


@main.route("/order-history.json")
@login_required
def order_history():
    acc = Accounts(current_user)
    order_history = acc.get_order_history()

    return order_history


@main.route("/knowledgebase")
@login_required
def knowledgebase():
    return render_template("knowledgebase.html")
