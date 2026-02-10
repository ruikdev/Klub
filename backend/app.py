from flask import Flask, jsonify

app = Flask(__name__)

app.config.update(
    SECRET_KEY="dev-secret",
    JSONIFY_PRETTYPRINT_REGULAR=False
)

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify(status="ok"), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
