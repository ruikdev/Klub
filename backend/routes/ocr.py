import base64
import io
import json
import os
import time
from flask import Blueprint, jsonify, request
from groq import Groq
from PIL import Image
from routes.cours import save_cours

ocr_bp = Blueprint('ocr', __name__, url_prefix='/api')

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

MAX_SIZE = (1920, 1920)   # résolution max
MAX_BYTES = 3 * 1024 * 1024  # 3 Mo max par image

def compress_image(image_bytes: bytes, mime_type: str) -> tuple[bytes, str]:
    """Redimensionne et compresse une image pour respecter la limite Groq."""
    img = Image.open(io.BytesIO(image_bytes))

    img.thumbnail(MAX_SIZE, Image.LANCZOS)

    quality = 90
    while True:
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=quality, optimize=True)
        data = buf.getvalue()
        if len(data) <= MAX_BYTES or quality <= 30:
            break
        quality -= 10

    return data, "image/jpeg"

def ocr_images_from_bytes(images: list[tuple[bytes, str]], model="meta-llama/llama-4-scout-17b-16e-instruct"):
    """
    Effectue l'OCR sur une ou plusieurs pages d'un même cours.
    images : liste de tuples (image_bytes, mime_type)
    Retourne un dict { texte, matiere, nom_cours }
    """
    # Construire le contenu : une entrée image par page
    content = []
    n = len(images)
    if n > 1:
        subject = f"ces {n} images qui sont les pages d'un même cours scolaire"
    else:
        subject = "cette image de cours scolaire"

    intro = (
        f"Analyse {subject}."
        " Réponds UNIQUEMENT avec un objet JSON valide, sans markdown, sans explication, avec exactement ces 3 champs :\n"
        "- \"texte\" : le texte extrait de toutes les pages, dans l'ordre, au format markdown\n"
        "- \"matiere\" : la matière parmi ces valeurs exactes uniquement : francais, mathematique, histoire, musique, physique-chimie, svt\n"
        "- \"nom_cours\" : le nom du cours ou du chapitre identifié\n"
        "Exemple : {\"texte\": \"...\", \"matiere\": \"mathematique\", \"nom_cours\": \"Les vecteurs\"}"
    )
    content.append({"type": "text", "text": intro})

    for i, (image_bytes, mime_type) in enumerate(images):
        b64 = base64.b64encode(image_bytes).decode('utf-8')
        if n > 1:
            content.append({"type": "text", "text": f"Page {i + 1} :"})
        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:{mime_type};base64,{b64}"}
        })

    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": content}],
        model=model,
        temperature=0.1,
        max_tokens=4000
    )

    raw = chat_completion.choices[0].message.content.strip()
    # Supprimer les blocs markdown éventuels (```json ... ```)
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[-1]
        raw = raw.rsplit("```", 1)[0].strip()
    return json.loads(raw)




@ocr_bp.route('/ocr', methods=['POST'])
def ocr():
    files = request.files.getlist("images")
    if not files:
        return jsonify({"error": "Aucune image fournie (champ 'images' attendu)"}), 400

    images = [compress_image(f.read(), f.content_type) for f in files]

    try:
        result = ocr_images_from_bytes(images)

        matiere = result.get("matiere", "").strip()
        nom = result.get("nom_cours", "").strip()

        MATIERES_VALIDES = {"francais", "mathematique", "histoire", "musique", "physique-chimie", "svt", "espagnol"}
        if not matiere or matiere not in MATIERES_VALIDES:
            matiere = "autre"
        if not nom:
            nom = f"cours_{int(time.time())}"

        saved = save_cours(
            matiere=matiere,
            nom=nom,
            contenu=result.get("texte", "")
        )
        result["matiere"] = matiere
        result["nom_cours"] = nom
        result["fichier"] = saved["nom"]

        return jsonify(result)
    except json.JSONDecodeError:
        return jsonify({"error": "Réponse IA invalide (JSON malformé)"}), 500
    except FileExistsError as e:
        return jsonify({"error": str(e)}), 409
    except Exception as e:
        return jsonify({"error": f"Erreur inattendue : {str(e)}"}), 500
