from flask import Flask
app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'you-will-never-guess'
# app._static_folder = 'app/static/'
from app import routes