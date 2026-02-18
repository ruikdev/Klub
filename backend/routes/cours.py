from flask import Blueprint, jsonify, request
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

@cours_bp.route("/cours", methods=["POST"])
def ajouterCours():
    """Ajouter un nouveau cours markdown. Body JSON: { matiere, nom, contenu }"""
    data = request.get_json()
    if not data:
        return jsonify(error="Corps JSON manquant"), 400

    matiere = data.get("matiere", "").strip()
    nom = data.get("nom", "").strip()
    contenu = data.get("contenu", "").strip()

    if not matiere or not nom:
        return jsonify(error="Les champs 'matiere' et 'nom' sont obligatoires"), 400

    # Sécuriser les noms pour éviter les path traversal
    matiere = os.path.basename(matiere)
    nom = os.path.basename(nom)

    matiere_path = os.path.join("cours", matiere)
    os.makedirs(matiere_path, exist_ok=True)

    # Ajouter l'extension .md si absente
    fichier = nom if nom.endswith(".md") else f"{nom}.md"
    fichier_path = os.path.join(matiere_path, fichier)

    if os.path.exists(fichier_path):
        return jsonify(error=f"Le cours '{fichier}' existe déjà dans '{matiere}'"), 409

    try:
        with open(fichier_path, "w", encoding="utf-8") as f:
            f.write(contenu)
        return jsonify(message="Cours ajouté avec succès", matiere=matiere, nom=fichier), 201
    except Exception as e:
        return jsonify(error=str(e)), 500

@cours_bp.route('/cours/<matiere>/<nom>', methods=['DELETE'])
def deleteCours(matiere, nom):
    """Supprimer un cours markdown. URL: /api/cours/<matiere>/<nom>"""
    matiere = os.path.basename(matiere)
    nom = os.path.basename(nom)

    fichier = nom if nom.endswith(".md") else f"{nom}.md"
    fichier_path = os.path.join("cours", matiere, fichier)

    if not os.path.exists(fichier_path):
        return jsonify(error=f"Le cours '{fichier}' est introuvable dans '{matiere}'"), 404

    try:
        os.remove(fichier_path)
        return jsonify(message=f"Cours '{fichier}' supprimé avec succès"), 200
    except Exception as e:
        return jsonify(error=str(e)), 500
