from flask import Flask, render_template
from flask.json import JSONEncoder
from flask_cors import CORS

import os
import urllib.request, json
from bson import json_util, ObjectId
from datetime import datetime, timedelta
from .db import get_admitidas, get_siguientes


from quincemilfirmas.api.iniciativas import iniciativas_api_v1

class MongoJsonEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        if isinstance(obj, ObjectId):
            return str(obj)
        return json_util.default(obj, json_util.CANONICAL_JSON_OPTIONS)

def create_app():
    APP_DIR = os.path.abspath(os.path.dirname(__file__))
    STATIC_FOLDER = os.path.join(APP_DIR, 'static')
    TEMPLATE_FOLDER = os.path.join(APP_DIR, 'templates')

    app = Flask(
                 __name__,
                 static_folder=STATIC_FOLDER,
                 template_folder=TEMPLATE_FOLDER
               )
    CORS(app)
    app.json_encoder = MongoJsonEncoder
    app.register_blueprint(iniciativas_api_v1)

    @app.route('/iniciativas')
    def rootpage():
        with open(os.path.abspath(os.path.join("updated.txt")), 'r') as f:
            last_update = f.readline()
        (admitidas, count) = get_admitidas()
        (siguientes, count_s) = get_siguientes()
        return render_template('index.html', admitidas=admitidas, siguientes=siguientes, last_update=last_update)
    
    return app
