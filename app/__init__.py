from flask import Flask
from flask_bootstrap import Bootstrap

app = Flask(__name__)
bootstrap = Bootstrap(app)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'you-will-never-guess'

from app import routes


