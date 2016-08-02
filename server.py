#!/usr/bin/env python3

from os import path
from shutil import rmtree
from tempfile import mkdtemp
from threading import Thread
from time import sleep
import subprocess

from flask import (Flask, render_template, request,
    redirect, url_for, send_from_directory)
from werkzeug import secure_filename

#settings
ALLOWED_EXTENSIONS = set(["docx", "doc", "xls", "xlsm", "xlsx", "odt", "ods"])
FILE_TIMEOUT = 600

class TimeSet(set):
    """Starts a thread for each item"""
    def add(self, item, timeout):
        set.add(self, item)
        thread = Thread(target=timeout_set_remove, args=(self, item, timeout))
        thread.start()

def timeout_set_remove(_set, item, timeout):
    """Removes item after timeout"""
    sleep(timeout)
    print("Deleting " + str(item))
    rmtree(str(item))
    _set.remove(item)

def allowed_file(filename):
    """Checks if file with filename is allowed"""
    return "." in filename and filename.rsplit(".", 1)[1] in ALLOWED_EXTENSIONS

app = Flask(__name__)
app.config["PROPAGATE_EXCEPTIONS"] = True
app.config["FILE_TIMEOUT"] = FILE_TIMEOUT
app.file_timeouts = TimeSet() # manages uploaded file timeouts

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files["file"]
        if file and allowed_file(file.filename):
            # saving file to temporary dir
            filename = secure_filename(file.filename)
            tmp_dir = mkdtemp()
            file.save(path.join(tmp_dir, filename))
            # adding delayed delete to tmp dir
            app.file_timeouts.add(tmp_dir, app.config["FILE_TIMEOUT"])
            new_filename = filename.rsplit(".", 1)[0] + ".pdf"
            # converting  file
            call = ["unoconv", "-f", "pdf",
                "-o", path.join(tmp_dir, new_filename),
                    path.join(tmp_dir, filename)]
            subprocess.check_call(call)
            #redirecting to new file
            return redirect(url_for("download", filename=new_filename,
                dirname=path.basename(tmp_dir)))
    # if any error occurs or in case of a GET request render start page
    return render_template("index.html",
            extensions=", ".join(ALLOWED_EXTENSIONS))

@app.route("/download/?file=<filename>&dir=<dirname>", methods=["GET"])
def download(filename, dirname):
    full_dir = path.join("/tmp", dirname)
    return send_from_directory(full_dir, filename, as_attachment=True)

if __name__ == "__main__":
    app.debug = True
    app.run()
