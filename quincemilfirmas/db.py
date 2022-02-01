import bson

from flask import current_app, g
from werkzeug.local import LocalProxy
from flask_pymongo import PyMongo

from pymongo.errors import DuplicateKeyError, OperationFailure
from bson.objectid import ObjectId
from bson.errors import InvalidId


def get_db():
    """
    Configuration method to return db instance
    """
    db = getattr(g, "_database", None)

    if db is None:

        db = g._database = PyMongo(current_app).db
    return db

# Use LocalProxy to read the global db instance with just `db`
db = LocalProxy(get_db)

def get_admitidas():
    try:
        admitidas = db.admitidas.find({}, {"_id": 0}).sort("apoyo", -1)
        total_admitidas = db.admitidas.count_documents({})
        return (list(admitidas), total_admitidas)
    except Exception as e:
        return e

def get_siguientes():
    try:
        siguentes = db.siguientes.find({}, {"_id": 0}).sort("apoyo", -1)
        total_siguentes = db.siguientes.count_documents({})
        return (list(siguentes), total_siguentes)
    except Exception as e:
        return e
