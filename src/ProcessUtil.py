import os
import re
import urllib.request
from flask import Flask, render_template, url_for, flash, redirect, request
from forms import KeywordForm
from werkzeug.utils import secure_filename

# Contoh prefix function
# abcdkonabcd
# 0 0 0 0 0 0 0 1 2 3 4

ALLOWED_EXTENSIONS = set(['txt'])

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
