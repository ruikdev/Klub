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
    
@flashCard_bp.route('/flash-cards', methods=['POST'])
def add_flash_card():
    """Ajouter une nouvelle flash-card JSON dans le dossier flash-cards"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify(error="Corps de la requête JSON requis"), 400
        
        matiere = data.get("matiere", "").strip()
        nom = data.get("nom", "").strip()
        cartes = data.get("cartes")

        if not matiere or not nom or not cartes:
            return jsonify(error="Matière, nom et cartes sont requis"), 400
        
        if not isinstance(cartes, list):
            return jsonify(error="Les cartes doivent être un tableau"), 400

        matiere_path = os.path.join(FLASH_CARDS_DIR, matiere)
        if not os.path.exists(matiere_path):
            os.makedirs(matiere_path)

        fichier_path = os.path.join(matiere_path, f"{nom}.json")
        
        with open(fichier_path, "w", encoding="utf-8") as f:
            json.dump(cartes, f, ensure_ascii=False, indent=4)
        
        return jsonify(
            message="Flash-card ajoutée avec succès",
            matiere=matiere,
            nom=nom,
            fichier=f"{nom}.json"
        ), 201
    
    except Exception as e:
        return jsonify(error=f"Erreur serveur: {str(e)}"), 500