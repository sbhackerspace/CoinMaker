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
    <title>Upload New Coin</title>
    <h1>Upload New Coin</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><b>Front Image:</b><input type=file name=front>
      <p><b>Back Image:</b><input type=file name=back>
         <input type=submit value=Upload>
    </form>
    <p>"""
    if filename:
      page += '<img src="' + '/static/img/' + filename + 'Front.png"'
      page += ' alt="front">'
      page += '<img src="' + '/static/img/' + filename + 'Middle.png"'
      page += ' alt="middle">'
      page += '<img src="' + '/static/img/' + filename + 'Back.png"'
      page += ' alt="">'


    page += '</p>'
    return page

################################################################################
def uploadFile(file):
  if file and allowed_file(file.filename):
    filename = os.path.join(
      app.config['UPLOAD_FOLDER'], secure_filename(file.filename))
    file.save(filename)
    return filename


################################################################################
@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        front = request.files['front']
        back = request.files['back']
        frontFileName = uploadFile(front)
        backFileName = uploadFile(back)

        if frontFileName and backFileName:
          Arguments = \
          {'-d': [], '-n': 0, '-o': [], '-s': []}
          Arguments['FRONTIMAGEFILENAME'] = frontFileName
          Arguments['BACKIMAGEFILENAME'] = backFileName

          try:
            CurrentTime = CoinMaker.MakeCoin(Arguments)
          except Exception as exception:
            return str(exception)

          return GetPage(CurrentTime)
    return GetPage()

################################################################################
################################################################################
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)
