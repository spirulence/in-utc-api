from os import environ
import datetime
from pytz import timezone

from bottle import run, route, template, request, redirect, error, response


def iso(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%S")


def unix(dt):
    return str(int(dt.timestamp()))


FORMATTERS = {
    "iso": iso,
    "i": iso,
    "unix": unix,
    "u": unix
}

base_template = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>UTC Time</title>
</head>

<body style='text-align: center'>
    <p style='font-size: 50px; font-family: sans-serif'>{{time}}</p>
</body>

</html>
"""


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
@dual_format
def now(fmt):
    return template(base_template, time=fmt(datetime.datetime.utcnow()))


FORWARDS_TIMEWORDS = {'later', 'fromnow', 'from-now', 'future'}
BACKWARDS_TIMEWORDS = {'ago', 'back'}


def generate_delta(digits, unit, timeword):
    absolute_delta = int(digits)

    if timeword in FORWARDS_TIMEWORDS:
        delta = absolute_delta
    elif timeword in BACKWARDS_TIMEWORDS:
        delta = - absolute_delta
    else:
        raise ValueError(f'Invalid timeword {timeword}')

    if unit in ['minutes', 'mins', 'min', 'm']:
        return datetime.timedelta(minutes=delta)
    if unit in ['hours', 'hrs', 'h']:
        return datetime.timedelta(hours=delta)
    if unit in ['days', 'dys', 'day', 'd']:
        return datetime.timedelta(days=delta)

    raise ValueError(f'Invalid unit {unit}')


# noinspection PyUnresolvedReferences
@route("/<digits:int><unit>/<timeword>")
@dual_format
def relative(digits, unit, timeword, fmt):
    try:
        delta = generate_delta(digits, unit, timeword)
    except ValueError:
        return redirect('/readme')

    return template(base_template, time=fmt(datetime.datetime.utcnow() + delta))


readme_html = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>UTC Time</title>
</head>

<body style='text-align: center'>
    <h2 style='font-family: sans-serif'>Things you can try:</h2>
    <p style='font-size: 20px; font-family: sans-serif'><a href='/now'>/now</a></p>
    <p style='font-size: 20px; font-family: sans-serif'><a href='/3hours/later'>/3hours/later</a></p>
    <p style='font-size: 20px; font-family: sans-serif'><a href='/1day/ago'>/1day/ago</a></p>
    <p style='font-size: 20px; font-family: sans-serif'><a href='/midnight/pacific'>/midnight/pacific</a></p>
    <p style='font-size: 20px; font-family: sans-serif'><a href='/midnight-yesterday/eastern'>/midnight-yesterday/eastern</a></p>
    <p style='font-size: 16px; font-family: sans-serif'>Don't forget the unix timestamp flavors: <a href='https://unix.inutc.com/readme'>https://unix.inutc.com/readme</a></h3>
</body>

</html>
"""


@route("/readme")
@route("/about")
def readme():
    return template(readme_html)


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
    "e": "US/Eastern"
}


@route('/midnight-tonight/<tz_name>')
@route('/midnight/<tz_name>')
@route('/m/<tz_name>')
@dual_format
def midnight_tonight(fmt, tz_name):
    if tz_name in TIMEZONE_SHORTHANDS:
        tz_name = TIMEZONE_SHORTHANDS[tz_name]

    midnight = datetime.datetime.now(timezone(tz_name)).replace(hour=0, minute=0, second=0, microsecond=0) \
               + datetime.timedelta(days=1)

    time = fmt(timezone("UTC").normalize(midnight))

    return template(base_template, time=time)


@route('/midnight-last-night/<tz_name>')
@route('/midnight-yesterday/<tz_name>')
@route('/mln/<tz_name>')
@route('/my/<tz_name>')
@dual_format
def midnight_yesterday(fmt, tz_name):
    if tz_name in TIMEZONE_SHORTHANDS:
        tz_name = TIMEZONE_SHORTHANDS[tz_name]

    midnight = datetime.datetime.now(timezone(tz_name)).replace(hour=0, minute=0, second=0, microsecond=0)

    time = fmt(timezone("UTC").normalize(midnight))

    return template(base_template, time=time)


@error(404)
def error404(error):
    response.status = 303
    response.headers['Location'] = '/readme'


if 'PORT' in environ:
    run(host='0.0.0.0', port=int(environ["PORT"]), server='gunicorn', workers=4)
else:
    run(host='localhost', port=8080, debug=True, reloader=True)
