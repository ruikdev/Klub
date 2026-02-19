from flask import Blueprint, jsonify, request
import os

# le chat ia pour les cours se trouve dans chat.py

cours_bp = Blueprint('cours', __name__, url_prefix='/api')

# Chemin absolu vers le dossier cours/, relatif à ce fichier
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COURS_DIR = os.path.join(BASE_DIR, "cours")

@cours_bp.route('/cours', methods=['GET'])
def get_cours():
    """Récupérer tous les cours markdown organisés par matière"""
    result = {}

    if not os.path.exists(COURS_DIR):
        return jsonify(error="Dossier cours introuvable"), 404

    for matiere in os.listdir(COURS_DIR):
        matiere_path = os.path.join(COURS_DIR, matiere)
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

def save_cours(matiere: str, nom: str, contenu: str):
    """Sauvegarde un cours markdown sur le disque. Lève une exception en cas d'erreur."""
    matiere = os.path.basename(matiere.strip())
    nom = os.path.basename(nom.strip())

    if not matiere or not nom:
        raise ValueError("Les champs 'matiere' et 'nom' sont obligatoires")

    matiere_path = os.path.join(COURS_DIR, matiere)
    os.makedirs(matiere_path, exist_ok=True)

    fichier = nom if nom.endswith(".md") else f"{nom}.md"
    fichier_path = os.path.join(matiere_path, fichier)

    if os.path.exists(fichier_path):
        raise FileExistsError(f"Le cours '{fichier}' existe déjà dans '{matiere}'")

    with open(fichier_path, "w", encoding="utf-8") as f:
        f.write(contenu)

    return {"matiere": matiere, "nom": fichier}


@cours_bp.route("/cours", methods=["POST"])
def ajouterCours():
    """Ajouter un nouveau cours markdown. Body JSON: { matiere, nom, contenu }"""
    data = request.get_json()
    if not data:
        return jsonify(error="Corps JSON manquant"), 400

    try:
        saved = save_cours(
            matiere=data.get("matiere", ""),
            nom=data.get("nom", ""),
            contenu=data.get("contenu", "").strip()
        )
        return jsonify(message="Cours ajouté avec succès", **saved), 201
    except (ValueError, FileExistsError) as e:
        return jsonify(error=str(e)), 409
    except Exception as e:
        return jsonify(error=str(e)), 500

@cours_bp.route('/cours/<matiere>/<nom>', methods=['DELETE'])
def deleteCours(matiere, nom):
    """Supprimer un cours markdown. URL: /api/cours/<matiere>/<nom>"""
    matiere = os.path.basename(matiere)
    nom = os.path.basename(nom)

    fichier = nom if nom.endswith(".md") else f"{nom}.md"
    fichier_path = os.path.join(COURS_DIR, matiere, fichier)

    if not os.path.exists(fichier_path):
        return jsonify(error=f"Le cours '{fichier}' est introuvable dans '{matiere}'"), 404

    try:
        os.remove(fichier_path)
        return jsonify(message=f"Cours '{fichier}' supprimé avec succès"), 200
    except Exception as e:
        return jsonify(error=str(e)), 500
