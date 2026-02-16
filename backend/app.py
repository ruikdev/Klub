from flask import Flask, jsonify
from dotenv import load_dotenv
from routes import register_blueprints

load_dotenv()

app = Flask(__name__)

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify(status="ok"), 200

register_blueprints(app)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
