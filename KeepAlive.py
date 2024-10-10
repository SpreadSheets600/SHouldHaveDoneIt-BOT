import logging
from flask import Flask
from threading import Thread

logger = logging.getLogger("werkzeug")
logger.setLevel(logging.ERROR)

logger2 = logging.getLogger()
logger2.setLevel(logging.ERROR)

app = Flask("")


@app.route("/")
def home():
    return """
    <html>
    <head><title>Bot Status</title></head>
    <body>
        <h1>Bot is Online</h1>
        <iframe src="https://SpreadSheets600.me" width="100%" height="500px"></iframe>
    </body>
    </html>
    """


def run():
    app.run(host="0.0.0.0", port=8080)


def KeepAlive():
    t = Thread(target=run)
    t.start()
