import os
import urllib.request
from flask import Flask, render_template, url_for, flash, redirect, request
from forms import KeywordForm
from werkzeug.utils import secure_filename

from PatternMatching import *

app = Flask(__name__)
app.config['SECRET_KEY'] = 'QUNGQANGQINGQONG'
posts = []

ALLOWED_EXTENSIONS = set(['txt'])

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
@app.route("/home")
def home():
    form = KeywordForm()
    return render_template('home.html', title='App', form = form, posts = posts)

@app.route("/", methods=['GET', 'POST'])
@app.route("/home", methods=['GET', 'POST'])
def query():
    form = KeywordForm()

    if (request.method == 'POST'):
        print('lagi di home')

        # check if the post request has the file part
        if ('myfile' not in request.files or 'algo' not in request.form):
            flash('No file part / choosen algo', 'danger')
            return redirect(request.url)
        
        files = request.files.getlist('myfile')
        if (len(files) == 0):
            flash('No file selected for uploading', 'danger')
            return redirect(request.url)
        
        result = []
        for file in files:
            if (file and allowed_file(file.filename)):
                filename = secure_filename(file.filename)
                algoPilihan = request.form['algo']
                file = file.read()
                teks = file.decode("utf-8")
                pattern = form.keyword.data
                resFile = findKeyword(pattern, teks, algoPilihan)
                resLen = len(resFile)
                for i in range(resLen):
                    resFile[i]['filename'] = filename
                result = result + resFile
            else:
                flash('Allowed file types are .txt', 'danger')
                return redirect(request.url)

        posts = result
        flash('extraction successful', 'success')
        return render_template('home.html', title = 'App', form = form, posts = posts)

    return render_template('home.html', title='App', form = form, posts = posts)

@app.route("/about")
def about():
    return render_template('about.html', title='About')

if __name__ == '__main__':
    # app.run(debug=True)
    app.run()
