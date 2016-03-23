#!/usr/bin/env python3

from flask import Flask, render_template

#settings

ALLOWED_EXTENSIONS = set(["docx", "doc", "xls", "xlsm"])


app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html", extensions=", ".join(ALLOWED_EXTENSIONS))

if __name__ == "__main__":
    app.debug = True
    app.run(host="192.168.1.167")
