import os

class Config(object):
    DEBUG = True
    
    SECRET_KEY = os.urandom(32)

    basedir = os.path.abspath(os.path.dirname(__file__))

    SQLALCHEMY_DATABASE_URI = 'postgres://felipegontijo@localhost:5432/fyyur'
    SQLALCHEMY_TRACK_MODIFICATIONS = False