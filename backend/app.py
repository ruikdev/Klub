from flask import Flask, jsonify, session, request
from dotenv import load_dotenv
from routes import register_blueprints
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-change-me')
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

PUBLIC_ROUTES = {'/api/auth/login', '/api/health'}

@app.before_request
def check_auth():
    """Vérifie l'authentification avant chaque requête protégée"""
    if request.method == 'OPTIONS':
        return None
    if request.path in PUBLIC_ROUTES:
        return None
    if not session.get('authenticated'):
        return jsonify(error="Non autorisé"), 401

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify(status="ok"), 200

register_blueprints(app)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
