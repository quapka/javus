import configparser
import threading
import webbrowser
import pymongo

from flask import Flask, render_template

from jsec.utils import MongoConnection

app = Flask(__name__)


def load_config():
    config = configparser.ConfigParser()
    config.read()


@app.route("/")
@app.route("/analysis/<id>")
def index():
    # FIXME load from config file
    name = "javacard-analysis"
    host = "localhost"
    port = "27017"

    with MongoConnection(database=name, host=host, port=port) as con:
        last_attack = con.col.find_one(sort=[("start-time", pymongo.DESCENDING)])

    return render_template("index.html", results=last_attack)


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
