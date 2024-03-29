import datetime
from os import environ

from bottle import error, redirect, request, response, route, run, view
from pytz import timezone


def iso(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%S")


def unix(dt):
    return str(int(dt.timestamp()))


FORMATTERS = {"iso": iso, "i": iso, "unix": unix, "u": unix}
FORWARDS_TIMEWORDS = {"later", "fromnow", "from-now", "future"}
BACKWARDS_TIMEWORDS = {"ago", "back"}
TIMEZONE_SHORTHANDS = {
    "pacific": "US/Pacific",
    "pt": "US/Pacific",
    "p": "US/Pacific",
    "mountain": "US/Mountain",
    "mt": "US/Mountain",
    "m": "US/Mountain",
    "central": "US/Central",
    "ct": "US/Central",
    "c": "US/Central",
    "eastern": "US/Eastern",
    "et": "US/Eastern",
    "e": "US/Eastern",
}


def dual_format(function):
    def wrapper(*args, **kwargs):
        host = request.urlparts.netloc
        if host.startswith("unix.") or host.startswith("u."):
            return function(*args, fmt=unix, **kwargs)
        else:
            return function(*args, fmt=iso, **kwargs)

    return wrapper


@route("/now")
@route("/")
@view("base_template")
@dual_format
def now(fmt):
    return {"time": fmt(datetime.datetime.utcnow())}


def generate_delta(digits, unit, timeword):
    absolute_delta = int(digits)

    if timeword in FORWARDS_TIMEWORDS:
        delta = absolute_delta
    elif timeword in BACKWARDS_TIMEWORDS:
        delta = -absolute_delta
    else:
        raise ValueError(f"Invalid timeword {timeword}")

    if unit in ["minutes", "mins", "min", "m"]:
        return datetime.timedelta(minutes=delta)
    if unit in ["hours", "hrs", "h"]:
        return datetime.timedelta(hours=delta)
    if unit in ["days", "dys", "day", "d"]:
        return datetime.timedelta(days=delta)
    if unit in ["years", "year", "y"]:
        # timedelta function does not have a year parameter
        # therefore get the total number of days * 365
        year_delta = delta * 365
        return datetime.timedelta(days=year_delta)

    raise ValueError(f"Invalid unit {unit}")


# noinspection PyUnresolvedReferences
@route("/<digits:int><unit>/<timeword>")
@view("base_template")
@dual_format
def relative(digits, unit, timeword, fmt):
    try:
        delta = generate_delta(digits, unit, timeword)
    except ValueError:
        return redirect("/readme")

    return {"time": fmt(datetime.datetime.now() + delta)}


@route("/readme")
@route("/about")
@view("readme_html")
def readme():
    return {}


@route("/midnight-tonight/<tz_name>")
@route("/midnight/<tz_name>")
@route("/m/<tz_name>")
@view("base_template")
@dual_format
def midnight_tonight(fmt, tz_name):
    if tz_name in TIMEZONE_SHORTHANDS:
        tz_name = TIMEZONE_SHORTHANDS[tz_name]

    midnight = datetime.datetime.now(timezone(tz_name)).replace(
        hour=0, minute=0, second=0, microsecond=0
    ) + datetime.timedelta(days=1)

    time = fmt(timezone("UTC").normalize(midnight))

    return {"time": time}


@route("/midnight-last-night/<tz_name>")
@route("/midnight-yesterday/<tz_name>")
@route("/mln/<tz_name>")
@route("/my/<tz_name>")
@view("base_template")
@dual_format
def midnight_yesterday(fmt, tz_name):
    if tz_name in TIMEZONE_SHORTHANDS:
        tz_name = TIMEZONE_SHORTHANDS[tz_name]

    midnight = datetime.datetime.now(timezone(tz_name)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )

    time = fmt(timezone("UTC").normalize(midnight))

    return {"time": time}


@error(404)
def error404(error):
    response.status = 303
    response.headers["Location"] = "/readme"


if "PORT" in environ:
    run(
        host="0.0.0.0", port=int(environ["PORT"]), server="gunicorn", workers=4
    )
else:
    run(host="localhost", port=8080, debug=True, reloader=True)
