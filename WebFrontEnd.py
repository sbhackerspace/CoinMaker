#!/usr/bin/python
import os
import CoinMaker
from flask import Flask, request, redirect, url_for
from werkzeug import secure_filename

uploadFolder = 'static'
ALLOWED_EXTENSIONS = set(['jpg','bmp','png'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = uploadFolder

################################################################################
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

################################################################################
def GetPage(filename = None):
    page = """
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    <p>"""
    if filename:
      page += '<img src="' + '/static/img/' + filename + 'Front.png"'
      page += ' alt="front">'
      page += '<img src="' + '/static/img/' + filename + 'Middle.png"'
      page += ' alt="front">'
      page += '<img src="' + '/static/img/' + filename + 'Back.png"'
      page += ' alt="front">'


    page += '</p>'
    return page

################################################################################
@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = \
              os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename))
            file.save(filename)
            Arguments = \
              {'-d': [], '-n': 0, '-o': [], '-s': [],'IMAGEFILENAME': filename}

            CurrentTime = CoinMaker.MakeCoin(Arguments)
            return GetPage(CurrentTime)
    else:
      return GetPage()

################################################################################
################################################################################
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)
