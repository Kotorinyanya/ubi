import time
from flask import Flask
from flask import request
from flask import render_template

from db import init_dolphin
from db import get_detail
from db import get_apps
from db import get_review_changes as get_review_changes_from_db
from db import get_review_result as get_review_result_from_db
from db import get_review as get_review_from_db
from helper import succeed
from helper import fail

ACCEPTABLE_WINDOW_LENGTH = [3, 7, 15]

app = Flask(__name__)


@app.route("/apps/<int:appid>/results")
def get_review_result(appid):
    # Get parameters.
    window_length = request.args.get("window_length", "")
    window_end_date = request.args.get("window_end_date", "")
    # Check whether valid date and window length.
    try:
        time.strptime(window_end_date, "%Y-%m-%d")
        window_length = int(window_length)
        if window_length not in ACCEPTABLE_WINDOW_LENGTH:
            raise Exception("Window length unacceptable.")
    except Exception as e:
        return fail(e)
    # Get result from DB.
    init_dolphin()
    result = get_review_result_from_db(appid, window_length, window_end_date)
    if result:
        return succeed(result)
    else:
        return fail("No such data.")


@app.route("/apps/<int:appid>/changes")
def get_review_changes(appid):
    # Get parameters.
    start_date = request.args.get("start_date", "")
    end_date = request.args.get("end_date", "")
    # Check whether valid dates.
    try:
        time.strptime(start_date, "%Y-%m-%d")
        time.strptime(end_date, "%Y-%m-%d")
    except Exception as e:
        return fail(e)
    # Get results from DB.
    init_dolphin()
    results = get_review_changes_from_db(appid, start_date, end_date)
    if results:
        return succeed(results)
    else:
        return fail("No such data.")


@app.route("/reviews/<int:recommendationid>")
def get_review(recommendationid):
    # Get result from DB.
    init_dolphin()
    result = get_review_from_db(recommendationid)
    if result:
        return succeed(result)
    else:
        return fail("No such data.")


@app.route("/")
def index():
    init_dolphin()
    apps = get_apps()
    return render_template("home.html", apps=apps)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/apps/<int:appid>")
def detail(appid):
    init_dolphin()
    details = get_detail(appid)
    return render_template("detail.html", detail=details)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
