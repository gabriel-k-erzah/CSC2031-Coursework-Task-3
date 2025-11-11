from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
import logging, time

db = SQLAlchemy()

def create_app():

    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    #file logger
    handler = logging.FileHandler("app.log")
    handler.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s %(levelname)s: %(message)s")
    fmt.converter = time.gmtime
    handler.setFormatter(fmt)
    app.logger.setLevel(logging.INFO)
    app.logger.addHandler(handler)


    from .routes import main
    app.register_blueprint(main)

    return app