from flask import Blueprint, render_template, jsonify, request
from flask_login import current_user, login_required

from app.account.account import Accounts

main = Blueprint("main", __name__)


@main.route("/")
@login_required
def index():
    acc = Accounts(current_user)
    return render_template(
        "index.html",
        name=current_user.name,
        current_amount=acc.current_account.current_amount,
        return_ptc=acc.current_account.return_ptc,
    )


@main.route("/order-history.json")
@login_required
def order_history():
    page = int(request.args.get("page", 1))

    acc = Accounts(current_user)
    order_history = acc.get_order_history(page)

    return order_history


@main.route("/knowledgebase")
@login_required
def knowledgebase():
    return render_template("knowledgebase.html", name=current_user.name)
