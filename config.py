import os
basedir=os.path.abspath(os.path.dirname(__file__))

class Config(object):
    DEBUG=False
    CSRF_enabled=True
    SECRET_KEY="Asw23f5g7nd39b"
    SQLALCHEMY_DATABASE_URI= "postgresql://localhost/arpandb"

    # postgresql://localhost/arpandb