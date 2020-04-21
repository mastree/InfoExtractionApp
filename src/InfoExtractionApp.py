import os
import urllib.request
from flask import Flask, render_template, url_for, flash, redirect, request
from forms import KeywordForm
from werkzeug.utils import secure_filename

from ProcessUtil import *
from PatternMatching import *

UPLOAD_FOLDER = os.path.dirname(__file__) + "\\..\\temp"

app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

'''
Keyword: terkonfirmasi positif
Hasil ekstraksi informasi:
Jumlah: 421; Waktu: Sabtu, 11 Apr 2020 20:07 WIB
421 Orang di Jabar Terkonfirmasi Positif COVID-19.
'''

# DUMMY
posts = []

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
                teks_path = os.path.join(app.config['UPLOAD_FOLDER'], "input.txt")
                keyword_path = os.path.join(app.config['UPLOAD_FOLDER'], "keyword.txt")
                file.save(teks_path)
                kfile = open(keyword_path, 'w')
                kfile.write(form.keyword.data)
                kfile.close()

                algoPilihan = request.form['algo']
                print(algoPilihan)

                teks = ''
                pattern = ''
                with open(teks_path, 'r') as fileContent:
                    teks = fileContent.read()
                with open(keyword_path, 'r') as fileContent:
                    pattern = fileContent.read()
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
    app.run(debug=True)
