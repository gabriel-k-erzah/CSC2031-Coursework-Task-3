import os
BASEDIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = 'devkey123'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASEDIR, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True
    TESTING = True