import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    DEBUG = False
    CSRF_enabled = True
    SECRET_KEY = "Asw23f5g7nd39b"
    # SQLALCHEMY_DATABASE_URI = "postgresql://localhost:5432/arpan"

    # for Adit's laptop
    SQLALCHEMY_DATABASE_URI= "postgresql://postgres:adot2004@localhost/arpandb"
    MAIL_USERNAME = "adit.ganapathy@outlook.com"
    MAIL_PASSWORD = "Monkeygeorge"
    MAIL_SERVER='smtp.office365.com'
    MAIL_PORT= 587
    MAIL_USE_SSL= False
    MAIL_USE_TLS = True
    # postgresql://localhost/arpandb
