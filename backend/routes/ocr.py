import base64
import json
import os
from flask import Blueprint, jsonify, request
from groq import Groq
from routes.cours import save_cours

ocr_bp = Blueprint('ocr', __name__, url_prefix='/api')

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def ocr_image_from_bytes(image_bytes, mime_type="image/jpeg", model="meta-llama/llama-4-scout-17b-16e-instruct"):
    """Effectue l'OCR sur des bytes d'image."""
    base64_image = base64.b64encode(image_bytes).decode('utf-8')
    
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "Analyse cette image de cours scolaire et réponds UNIQUEMENT avec un objet JSON valide, sans markdown, sans explication, avec exactement ces 3 champs :\n"
                            "- \"texte\" : le texte extrait de l'image au format markdown\n"
                            "- \"matiere\" : la matière parmi ces valeurs exactes uniquement : francais, mathematique, histoire, musique, physique-chimie, svt\n"
                            "- \"nom_cours\" : le nom du cours ou du chapitre identifié\n"
                            "Exemple : {\"texte\": \"...\", \"matiere\": \"mathematique\", \"nom_cours\": \"Les vecteurs\"}"
                        )
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:{mime_type};base64,{base64_image}"}
                    }
                ]
            }
        ],
        model=model,
        temperature=0.1,
        max_tokens=2000
    )
    
    raw = chat_completion.choices[0].message.content
    return json.loads(raw)




@ocr_bp.route('/ocr', methods=['POST'])
def ocr():
    if "image" not in request.files:
        return jsonify({"error": "Aucune image fournie"}), 400
    
    file = request.files["image"]
    image_bytes = file.read()
    mime_type = file.content_type
    
    try:
        result = ocr_image_from_bytes(image_bytes, mime_type)

        saved = save_cours(
            matiere=result.get("matiere", ""),
            nom=result.get("nom_cours", ""),
            contenu=result.get("texte", "")
        )
        result["fichier"] = saved["nom"]

        return jsonify(result)
    except json.JSONDecodeError:
        return jsonify({"error": "Réponse IA invalide (JSON malformé)"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500
