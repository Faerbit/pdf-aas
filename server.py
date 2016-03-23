#!/usr/bin/env python3

from os import path
from shutil import rmtree
from tempfile import mkdtemp
from threading import Thread
from time import sleep

from flask import (Flask, render_template, request, 
    redirect, url_for, send_from_directory)
from werkzeug import secure_filename

#settings
ALLOWED_EXTENSIONS = set(["docx", "doc", "xls", "xlsm", "odt", "ods"])
FILE_TIMEOUT = 30

class TimeSet(set):
    def add(self, item, timeout):
        set.add(self, item)
        thread = Thread(target=timeout_set_remove, args=(self, item, timeout))
        thread.start()

def timeout_set_remove(_set, item, timeout):
    sleep(timeout)
    print("Deleting " + str(item))
    rmtree(str(item))
    _set.remove(item)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1] in ALLOWED_EXTENSIONS

app = Flask(__name__)
app.config["FILE_TIMEOUT"] = FILE_TIMEOUT
app.file_timeouts = TimeSet()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files["file"]
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            tmp_dir = mkdtemp()
            file.save(path.join(tmp_dir, filename))
            app.file_timeouts.add(tmp_dir, app.config["FILE_TIMEOUT"])
            return redirect(url_for("download", filename=filename, dirname=path.basename(tmp_dir)))
    return render_template("index.html", extensions=", ".join(ALLOWED_EXTENSIONS))

@app.route("/download/?file=<filename>&dir=<dirname>", methods=["GET"])
def download(filename, dirname):
    full_dir = path.join("/tmp", dirname)
    return send_from_directory(full_dir, filename, as_attachment=True)

if __name__ == "__main__":
    app.debug = True
    app.run(host="192.168.1.167")
