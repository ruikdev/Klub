from flask import Blueprint, jsonify, request, session
import os

authentification_bp = Blueprint('authentification', __name__, url_prefix='/api')


@authentification_bp.route('/login', methods=['POST'])
def login():
    """Authentification avec le code d'accès"""
    data = request.get_json()
    if not data or not data.get('code'):
        return jsonify(error="Code requis"), 400

    if data.get('code') == os.environ.get('ACCESS_CODE'):
        session['authenticated'] = True
        return jsonify(message="Connecté"), 200

    return jsonify(error="Code incorrect"), 401


@authentification_bp.route('/logout', methods=['POST'])
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

