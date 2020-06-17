import configparser
import threading
import webbrowser
import pymongo

from flask import Flask, render_template

from jsec.utils import MongoConnection
from jsec.settings import STATIC_DIR

app = Flask(__name__)


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


@app.route("/")
def index():
    # FIXME add stage viewer
    # FIXME load from config file
    name = "javacard-analysis"
    host = "localhost"
    port = "27017"

    with MongoConnection(database=name, host=host, port=port) as con:
        last_attack = con.col.find_one(sort=[("start-time", pymongo.DESCENDING)])

    with open("analysis-results.html", "w") as f:
        template = render_template(
            "index.html",
            results=last_attack,
            marks=Marks(),
            dump_results=True,
            stylesheet_content=get_stylesheet_content(),
        )
        f.write(template)
    return render_template("index.html", results=last_attack, marks=Marks())


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
