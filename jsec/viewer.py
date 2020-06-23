#!/usr/bin/env python
import argparse
import configparser
import time
import datetime
import threading
import webbrowser
from typing import List, Tuple

import pymongo
import pytz
from bson.objectid import ObjectId
from flask import Flask, render_template, request
from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired

from jsec.settings import STATIC_DIR
from jsec.utils import MongoConnection

app = Flask(__name__)
app.config["SECRET_KEY"] = "this-is-very-secret-and-should-be-fixed"

# FIXME load from config file
name = "javacard-analysis"
host = "localhost"
port = "27017"


class Marks:
    tick_sign = "&#10004;"
    cross_sign = "&#10060;"
    # circle_sign = "&#9898;"
    circle_sign = "&#9675;"

    @property
    def tick(self) -> str:
        return '<span class="tick">%s</span>' % self.tick_sign

    @property
    def cross(self) -> str:
        return '<span class="cross">%s</span>' % self.cross_sign

    @property
    def skip(self) -> str:
        return '<span class="skip">%s</span>' % self.circle_sign

    @property
    def unknown(self) -> str:
        return '<span class="unknown">%s</span>' % self.circle_sign

    @property
    def legend(self):
        items = {
            "tick": {"message": "stage successful", "html": self.tick},
            "cross": {"message": "stage failed", "html": self.cross},
            "skip": {"message": "stage skipped", "html": self.skip},
            "unknown": {"message": "stage unknown", "html": self.unknown},
        }
        return items


def load_config():
    config = configparser.ConfigParser()
    config.read()


def get_stylesheet_content():
    # FIXME this approach is quite naive and does not handle fonts
    with open(STATIC_DIR / "css" / "stylesheet.css") as f:
        stylesheet = f.read()

    return stylesheet


def get_analysis_choices() -> List[Tuple[str, str]]:
    name = "javacard-analysis"
    host = "localhost"
    port = "27017"
    with MongoConnection(database=name, host=host, port=port) as con:
        all_attack_ids = con.col.find(
            projection=["_id"], sort=[("start-time", pymongo.ASCENDING)]
        )

    choices = []
    for index, attack in enumerate(all_attack_ids):
        _id = attack["_id"]
        label = str(index) + ": " + add_whitespace_id(str(_id))
        choices.append((str(_id), label))

    # choices = [(str(x["_id"]), str(i + 1)) for i, x in enumerate(all_attack_ids)]
    # we will reverse the order to show the newest analysis runs on top
    return choices[::-1]


# @app.route("/attack/<id>/stage/<stage_index>", methods=["GET"])
@app.route("/get_stage_data/<analysis_id>/<attack_name>/<stage_index>/<stage_name>")
def get_stage_data(analysis_id, attack_name, stage_index, stage_name):
    with MongoConnection(database=name, host=host, port=port) as con:
        analysis = con.col.find_one({"_id": ObjectId(analysis_id)})

    stage = analysis["analysis-results"][attack_name][int(stage_index)]
    # return jsonify(stage)
    return render_template("stage.html", stage=stage, attack_name=attack_name)


@app.route("/", methods=["GET", "POST"])
def index():
    # FIXME add stage viewer
    if request.method == "POST":
        attack_id = request.form["analysis"]
        with MongoConnection(database=name, host=host, port=port) as con:
            analysis = con.col.find_one({"_id": ObjectId(attack_id)})
    else:
        with MongoConnection(database=name, host=host, port=port) as con:
            analysis = con.col.find_one(sort=[("start-time", pymongo.DESCENDING)])
            # FIXME get only ids?

    form = AnalysisResultForm()
    form.analysis.choices = get_analysis_choices()

    # with open("analysis-results.html", "w") as f:
    #     template = render_template(
    #         "index.html",
    #         results=last_attack,
    #         marks=Marks(),
    #         dump_results=True,
    #         stylesheet_content=get_stylesheet_content(),
    #     )
    #     f.write(template)
    now = time.time()
    analysis["start-time-ago"] = now - analysis["start-time"]
    analysis["end-time-ago"] = now - analysis["end-time"]

    return render_template("index.html", analysis=analysis, form=form, marks=Marks())


class AnalysisResultForm(FlaskForm):
    analysis = SelectField(u"Run")
    submit = SubmitField("Show")


@app.template_filter()
def as_datetime(utc_timestamp: str, dt_format: str = "%H:%M:%S %d/%m/%Y") -> str:
    r"""
    `utc_timestamp`: assumed to be UTC timestamp, that will be displayed
    """
    # FIXME this might still not work for daylight saving time, but is good enough for now
    dt = datetime.datetime.fromtimestamp(float(utc_timestamp))
    dt.replace(tzinfo=pytz.utc)
    return dt.astimezone().strftime(dt_format)


@app.template_filter()
def format_duration(utc_timestamp: str) -> str:
    r"""
    `utc_timestamp`:
    """
    try:
        utc_timestamp = float(utc_timestamp)
    except ValueError:
        return "Invalid value: %s" % utc_timestamp

    microseconds = int(round((utc_timestamp - int(utc_timestamp)) * 1000))

    if utc_timestamp < 1:
        # microseconds = int(utc_timestamp * 1000)
        return "%dms" % microseconds

    minutes, seconds = divmod(utc_timestamp, 60)
    if not minutes:
        duration = "%d" % seconds
        if microseconds:
            duration += ".%03d" % microseconds
        duration += "s"

        return duration

    hours, minutes = divmod(minutes, 60)
    if not hours:
        duration = "%02d:%02d" % (minutes, seconds)
        if microseconds:
            duration += ".%03d" % microseconds
        return duration

    td = datetime.timedelta(seconds=utc_timestamp)
    return str(td)


@app.template_filter()
def add_whitespace_id(_id: str) -> str:
    r"""Adds white spaces each 8 characters to `_id` to improve readability.
    `_id`: 24 characaters long ObjectID assigned to MongoDB objects
    """
    try:
        _id = str(_id)
    except ValueError:
        return _id

    chunks = [_id[8 * i : 8 * (i + 1)] for i in range(len(_id) // 8)]
    return " ".join(chunks)


# @app.route('/dump')
# def dump():
# html to include stylesheets
# {% if dump_results %}
#       <style type="text/css">{{ stylesheet_content | safe}}</style>
# {% endif %}
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", default="27017")

    args = parser.parse_args()
    host = args.host
    port = args.port
    # FIXME only for development
    # the following lines are meant for testing and development
    # the real server should be launched differently
    app_thread = threading.Thread(target=app.run)
    # TODO create URL dynamically
    url = "localhost:5000"
    browser_thread = threading.Thread(target=webbrowser.open, args=(url,))
    app_thread.start()
    browser_thread.start()
