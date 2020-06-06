import configparser
import threading
import webbrowser

from flask import Flask, render_template

from jsec.utils import MongoConnection

app = Flask(__name__)


def load_config():
    config = configparser.ConfigParser()
    config.read()


@app.route("/")
@app.route("/analysis/<id>")
def index():
    with MongoConnection():
        pass
    return render_template("index.html")


if __name__ == "__main__":
    # the following lines are meant for testing and development
    # the real server should be launched differently
    app_thread = threading.Thread(target=app.run)
    # TODO create URL dynamically
    url = "localhost:5000"
    browser_thread = threading.Thread(target=webbrowser.open, args=(url,))
    app_thread.start()
    browser_thread.start()
