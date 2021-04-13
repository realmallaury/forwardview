import random
from datetime import date, datetime

from dateutil.relativedelta import relativedelta


def to_date(date):
    return datetime.strptime(date, "%Y-%m-%d")


def current_date():
    return datetime.now().strftime("%Y-%m-%d")


def add_days_to_date(date, delta):
    ed = datetime.strptime(date, "%Y-%m-%d") + relativedelta(days=delta)
    return ed.strftime("%Y-%m-%d")


def subtract_days_from_date(date, delta):
    ed = datetime.strptime(date, "%Y-%m-%d") - relativedelta(days=delta)
    return ed.strftime("%Y-%m-%d")


def add_months_to_date(date, delta):
    ed = datetime.strptime(date, "%Y-%m-%d") + relativedelta(months=delta)
    return ed.strftime("%Y-%m-%d")


def subtract_months_from_date(date, delta):
    ed = datetime.strptime(date, "%Y-%m-%d") - relativedelta(months=delta)
    return ed.strftime("%Y-%m-%d")


def generate_random_date(start_date, end_date):
    sd = datetime.strptime(start_date, "%Y-%m-%d")
    ed = datetime.strptime(end_date, "%Y-%m-%d")

    rd = date.fromordinal(random.randint(sd.toordinal(), ed.toordinal()))
    return rd.strftime("%Y-%m-%d")
