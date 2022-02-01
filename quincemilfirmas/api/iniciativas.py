from flask import Blueprint, request, jsonify
from quincemilfirmas.db import get_admitidas, get_siguientes
from flask_cors import CORS
from datetime import datetime


iniciativas_api_v1 = Blueprint(
    'iniciativas_api_v1', 'iniciativas_api_v1', url_prefix='/api/v1/iniciativas')

CORS(iniciativas_api_v1)

@iniciativas_api_v1.route('/admitidas', methods=['GET'])
def api_get_admitidas():
    try:
        (admitidas, total_num_entries) = get_admitidas()
        response = {
            "admitidas": admitidas,
            "filters": {},
            "total_results": total_num_entries,
        }
    except:
        response = get_admitidas()

    return jsonify(response)

@iniciativas_api_v1.route('/siguientes', methods=['GET'])
def api_get_siguientes():
    try:
        (siguientes, total_num_entries) = get_siguientes()
        response = {
            "siguientes": siguientes,
            "filters": {},
            "total_results": total_num_entries,
        }
    except:
        response = get_admitidas()

    return jsonify(response)