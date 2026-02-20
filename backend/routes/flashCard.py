from flask import Blueprint, jsonify, request
import os
import json


flashCard_bp = Blueprint('flashCard', __name__, url_prefix='/api')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FLASH_CARDS_DIR = os.path.join(BASE_DIR, "flash-cards")

@flashCard_bp.route('/flash-cards', methods=['GET'])
def get_flash_cards():
    """Récupérer toutes les flash-cards JSON organisées par matière"""
    result = {}

    if not os.path.exists(FLASH_CARDS_DIR):
        return jsonify(error="Dossier flash-cards introuvable"), 404

    for matiere in os.listdir(FLASH_CARDS_DIR):
        matiere_path = os.path.join(FLASH_CARDS_DIR, matiere)
        if not os.path.isdir(matiere_path):
            continue

        result[matiere] = []

        for fichier in os.listdir(matiere_path):
            if not fichier.endswith(".json"):
                continue

            fichier_path = os.path.join(matiere_path, fichier)
            try:
                with open(fichier_path, "r", encoding="utf-8") as f:
                    cartes = json.load(f)
                result[matiere].append({
                    "nom": os.path.splitext(fichier)[0],
                    "fichier": fichier,
                    "cartes": cartes
                })
            except Exception as e:
                result[matiere].append({
                    "nom": os.path.splitext(fichier)[0],
                    "fichier": fichier,
                    "erreur": str(e)
                })

    return jsonify(flashCards=result), 200
    