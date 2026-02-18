from flask import Blueprint, jsonify
import os

cours_bp = Blueprint('cours', __name__, url_prefix='/api')

@cours_bp.route('/cours', methods=['GET'])
def get_cours():
    """Récupérer tous les cours markdown organisés par matière"""
    cours_dir = "cours"
    result = {}

    if not os.path.exists(cours_dir):
        return jsonify(error="Dossier cours introuvable"), 404

    for matiere in os.listdir(cours_dir):
        matiere_path = os.path.join(cours_dir, matiere)
        if not os.path.isdir(matiere_path):
            continue

        result[matiere] = []

        for fichier in os.listdir(matiere_path):
            if not fichier.endswith(".md"):
                continue

            fichier_path = os.path.join(matiere_path, fichier)
            try:
                with open(fichier_path, "r", encoding="utf-8") as f:
                    contenu = f.read()
                result[matiere].append({
                    "nom": os.path.splitext(fichier)[0],
                    "fichier": fichier,
                    "contenu": contenu
                })
            except Exception as e:
                result[matiere].append({
                    "nom": os.path.splitext(fichier)[0],
                    "fichier": fichier,
                    "erreur": str(e)
                })

    return jsonify(cours=result), 200
