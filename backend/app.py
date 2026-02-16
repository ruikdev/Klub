from flask import Flask, jsonify, request
from ecole_direct_login import EcoleDirecteAPI
import sys
import json
import os
from datetime import datetime

app = Flask(__name__)

# Fichier de configuration
CONFIG_FILE = "ecole_direct_config.json"

def load_config():
    """Charger la configuration sauvegardée"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return None
    return None

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify(status="ok"), 200

@app.route("/api/devoirs", methods=["GET"])
def devoirs():
    config = load_config()
    if not config:
        return jsonify(error="Configuration non trouvée"), 500
    
    api = EcoleDirecteAPI()
    
    identifiant = config.get('identifiant')
    motdepasse = config.get('motdepasse')
    cn = config.get('cn')
    cv = config.get('cv')
    
    if not identifiant or not motdepasse or not cn or not cv:
        return jsonify(error="Identifiants manquants dans la configuration"), 500
    
    if not api.login(identifiant, motdepasse, cn, cv):
        return jsonify(error="Échec de la connexion"), 401
    
    devoirs_data = api.get_devoirs()
    
    if devoirs_data is None:
        return jsonify(error="Impossible de récupérer les devoirs"), 500
    
    return jsonify(devoirs_data), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
