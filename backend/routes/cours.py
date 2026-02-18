from flask import Blueprint, jsonify
import os

cours_bp = Blueprint('cours', __name__, url_prefix='/api')

@cours_bp.route('/cours', methods=['GET'])
def get_cours():
    with open("cours/test.md", "r", encoding="utf-8") as f:
        contenu = f.read()
    return jsonify(contenu=contenu), 200
