from flask import Flask, jsonify, session, request, send_from_directory
from dotenv import load_dotenv
from routes import register_blueprints
import os
from routes.auth import limiter

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'dist', 'klub')

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-change-me')
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
limiter.init_app(app)

PUBLIC_ROUTES = {'/api/auth/login', '/api/health'}

@app.before_request
def check_auth():
    """Vérifie l'authentification avant chaque requête protégée"""
    if request.method == 'OPTIONS':
        return None
    if not request.path.startswith('/api/'):
        return None
    if request.path in PUBLIC_ROUTES:
        return None
    if not session.get('authenticated'):
        return jsonify(error="Non autorisé"), 401

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify(status="ok"), 200

register_blueprints(app)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    file_path = os.path.join(FRONTEND_DIR, path)
    if path and os.path.isfile(file_path):
        return send_from_directory(FRONTEND_DIR, path)
    return send_from_directory(FRONTEND_DIR, 'index.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
