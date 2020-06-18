from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired

import configparser
import threading
import webbrowser
import pymongo
from typing import List, Tuple
from bson.objectid import ObjectId

from flask import Flask, render_template
from flask import request
import pytz
import datetime

from jsec.utils import MongoConnection
from jsec.settings import STATIC_DIR

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
    def circle(self) -> str:
        return '<span class="circle">%s</span>' % self.circle_sign

    @property
    def legend(self):
        items = {
            "tick": {"message": "stage successful", "html": self.tick,},
            "cross": {"message": "stage failed", "html": self.cross,},
            "circle": {"message": "stage skipped", "html": self.circle,},
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


def create_attack_choices() -> List[Tuple[str, str]]:
    name = "javacard-analysis"
    host = "localhost"
    port = "27017"
    with MongoConnection(database=name, host=host, port=port) as con:
        all_attack_ids = con.col.find(
            projection=["_id"], sort=[("start-time", pymongo.DESCENDING)]
        )

    choices = [(str(x["_id"]), str(i + 1)) for i, x in enumerate(all_attack_ids)]
    return choices


# @app.route("/attack/<id>/stage/<stage_index>", methods=["GET"])
@app.route("/get_stage_data/<analysis_id>/<attack_name>/<stage_index>/<stage_name>")
def get_stage_data(analysis_id, attack_name, stage_index, stage_name):
    with MongoConnection(database=name, host=host, port=port) as con:
        attack = con.col.find_one({"_id": ObjectId(analysis_id)})

    stage = attack["analysis-results"][attack_name][int(stage_index)]
    # return jsonify(stage)
    return render_template("stage.html", stage=stage)


@app.route("/", methods=["GET", "POST"])
def index():
    # FIXME add stage viewer
    if request.method == "POST":
        attack_id = request.form["attack"]
        with MongoConnection(database=name, host=host, port=port) as con:
            # FIXME rename attack to analysis
            attack = con.col.find_one({"_id": ObjectId(attack_id)})
    else:
        with MongoConnection(database=name, host=host, port=port) as con:
            attack = con.col.find_one(sort=[("start-time", pymongo.DESCENDING)])
            # FIXME get only ids?

    form = AnalysisResultForm()
    form.attack.choices = create_attack_choices()

    # with open("analysis-results.html", "w") as f:
    #     template = render_template(
    #         "index.html",
    #         results=last_attack,
    #         marks=Marks(),
    #         dump_results=True,
    #         stylesheet_content=get_stylesheet_content(),
    #     )
    #     f.write(template)

    return render_template("index.html", results=attack, form=form, marks=Marks())


class AnalysisResultForm(FlaskForm):
    submit = SubmitField("Show")
    attack = SelectField(u"Attack id")


@app.template_filter()
def as_datetime(utc_timestamp: str, dt_format: str = "%H:%M:%S %d/%m/%Y") -> str:
    r"""
    `timestamp`: assumed to be UTC timestamp, that will be displayed
    """
    # FIXME this might still not work for daylight saving time, but is good enough for now
    dt = datetime.datetime.fromtimestamp(float(utc_timestamp))
    dt.replace(tzinfo=pytz.utc)
    return dt.astimezone().strftime(dt_format)


if __name__ == "__main__":
    # FIXME only for development
    # the following lines are meant for testing and development
    # the real server should be launched differently
    app_thread = threading.Thread(target=app.run)
    # TODO create URL dynamically
    url = "localhost:5000"
    browser_thread = threading.Thread(target=webbrowser.open, args=(url,))
    app_thread.start()
    browser_thread.start()
