#!/usr/bin/env python
import argparse
import configparser
import datetime
import threading
import time
import webbrowser
from typing import List, Tuple

import pytz

import flask_wtf
import pymongo
import wtforms
from bson.objectid import ObjectId
from flask import Flask, render_template, request
from javus.settings import STATIC_DIR
from javus.utils import MongoConnection

app = Flask(__name__)
# NOTE: this web app is meant to be run locally, therefore we are not
# worried about SECRET_KEY not being secret
app.config["SECRET_KEY"] = "this-is-very-secret-and-should-be-fixed"

# FIXME load from config file
db_config = {
    "database": "javacard-analysis",
    "host": "localhost",
    "port": "27017",
}


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


marks = Marks()


def load_config():
    config = configparser.ConfigParser()
    config.read()


def get_stylesheet_content():
    # FIXME this approach is quite naive and does not handle fonts
    with open(STATIC_DIR / "css" / "stylesheet.css") as f:
        stylesheet = f.read()

    return stylesheet


def get_analysis_choices() -> List[Tuple[str, str]]:
    with MongoConnection(**db_config) as con:
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


def get_card_atr_choices() -> List[Tuple[str, str]]:
    with MongoConnection(**db_config) as con:
        records = con.col.find(projection=["card"])

    choices = []
    for record in records:
        try:
            atr = record["card"]["atr"]
        except KeyError:
            continue

        if isinstance(atr, list):
            # FIXME remove on fresh database, where 'atr's are string
            atr = " ".join(["{:02X}".format(byte) for byte in atr])

        label = atr
        choices.append((atr, label))
    choices = list(set(choices))
    choices.sort(key=lambda x: x[1])

    return choices


def get_attack_choices() -> List[Tuple[str, str]]:
    """
    Probably quite slow and ineffient method of getting all the attacks.
    """
    with MongoConnection(**db_config) as con:
        runs = con.col.find(projection=["analysis-results"])

    attacks = []
    for run in runs:
        try:
            attacks.extend(list(run["analysis-results"].keys()))
        except (AttributeError, KeyError):
            continue

    attacks = sorted(set(attacks))
    choices = [(a, a) for a in attacks]

    return choices


# @app.route("/attack/<id>/stage/<stage_index>", methods=["GET"])
@app.route("/get_stage_data/<analysis_id>/<attack_name>/<stage_index>/<stage_name>")
def get_stage_data(analysis_id, attack_name, stage_index, stage_name):
    with MongoConnection(**db_config) as con:
        analysis = con.col.find_one({"_id": ObjectId(analysis_id)})

    stage = analysis["analysis-results"][attack_name]["results"][int(stage_index)]
    sdk_version = analysis["analysis-results"][attack_name]["sdk_version"]
    # return jsonify(stage)
    return render_template(
        "stage.j2", stage=stage, attack_name=attack_name, sdk_version=sdk_version
    )


@app.route("/", methods=["GET", "POST"])
def index():
    form = MainForm()
    form.run.analysis.choices = get_analysis_choices()
    form.card.atr.choices = get_card_atr_choices()
    form.attack.attack_name.choices = get_attack_choices()

    if request.method == "POST":
        # handle run form
        return form_handler_template(form=form)
    else:
        with MongoConnection(**db_config) as con:
            analysis = con.col.find_one(sort=[("start-time", pymongo.DESCENDING)])

    return render_template("base.j2", analysis=analysis, form=form, marks=marks)


def form_handler_template(form):
    """
    Return the correct bases on which form was filled in
    """
    items = list(request.form.keys())
    if "run-submit" in items:
        return run_form_template(form)
    elif "attack-submit" in items:
        return attack_form_template(form)
    elif "card-submit" in items:
        return card_form_template(form)


def run_form_template(form):
    attack_id = request.form["run-analysis"]
    with MongoConnection(**db_config) as con:
        run = con.col.find_one({"_id": ObjectId(attack_id)})

    return render_template("runs.j2", analysis=run, form=form, marks=marks)


def attack_form_template(form):
    name = request.form["attack-attack_name"].strip()
    with MongoConnection(**db_config) as con:
        field = "analysis-results.%s" % name
        sieve = {
            "analysis-results.%s" % name: {"$exists": True},
            "card": {"$exists": True},
        }

        runs = con.col.find(sieve, projection=[field, "card"])

    return render_template("attacks.j2", form=form, runs=runs, marks=marks)


def card_form_template(form):
    """
    Render all attacks for given ATR, which does not equal given card.
    This could be potentially misleading in the results.
    """
    atr = request.form["card-atr"]
    with MongoConnection(**db_config) as con:
        card = con.col.find_one({"card.atr": atr}, projection=["card"])

    with MongoConnection(**db_config) as con:
        runs = con.col.find({"card.atr": atr})

    return render_template("atr-body.j2", form=form, card=card, runs=runs, marks=marks)


class AnalysisResultForm(flask_wtf.FlaskForm):
    analysis = wtforms.SelectField(u"Run")
    submit = wtforms.SubmitField("Show")


class CardSelectForm(flask_wtf.FlaskForm):
    atr = wtforms.SelectField(u"ATR")
    submit = wtforms.SubmitField("Show")


class AttackSelectForm(flask_wtf.FlaskForm):
    attack_name = wtforms.SelectField(u"Attack")
    submit = wtforms.SubmitField("Show")


class MainForm(flask_wtf.FlaskForm):
    run = wtforms.FormField(AnalysisResultForm)
    card = wtforms.FormField(CardSelectForm)
    attack = wtforms.FormField(AttackSelectForm)


@app.template_filter()
def as_datetime(utc_timestamp: str, dt_format: str = "%H:%M:%S %d/%m/%Y") -> str:
    r"""
    `utc_timestamp`: assumed to be UTC timestamp, that will be displayed
    """
    try:
        float(utc_timestamp)
    except:
        return "-"
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
    except:
        return "-"

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


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", default="5000")

    args = parser.parse_args()

    web_kwargs = {
        "host": args.host,
        "port": args.port,
    }
    # FIXME only for development
    # the following lines are meant for testing and development
    # the real server should be launched differently
    app_thread = threading.Thread(target=app.run, args=[], kwargs=web_kwargs)
    # TODO create URL dynamically
    url = "localhost:5000"
    browser_thread = threading.Thread(target=webbrowser.open, args=(url,))
    app_thread.start()
    browser_thread.start()
