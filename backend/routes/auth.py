from flask import Blueprint, jsonify, request, session
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os

authentification_bp = Blueprint('authentification', __name__, url_prefix='/api')

limiter = Limiter(get_remote_address)

@authentification_bp.route('/auth/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    """Authentification avec le code d'accès"""
    data = request.get_json()
    if not data or not data.get('code'):
        return jsonify(error="Code requis"), 400

    if data.get('code') == os.environ.get('ACCESS_CODE'):
        session['authenticated'] = True
        return jsonify(message="Connecté"), 200

    return jsonify(error="Code incorrect"), 401


@authentification_bp.route('/auth/logout', methods=['POST']) #oui, la fonction n'est pas utiliée pour l'instant, mais elle pourrait être utile à l'avenir (absolument pas mdr, j'ai la flemme + pas utile)
def logout():
    """Déconnexion"""
    session.clear()
    return jsonify(message="Déconnecté"), 200


@authentification_bp.route('/auth/check', methods=['GET'])
def check():
    """Vérifie si la session est active"""
    if session.get('authenticated'):
        return jsonify(authenticated=True), 200
    return jsonify(authenticated=False), 401

