import base64
import os
from flask import Blueprint, jsonify, request
from groq import Groq

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
                        "text": "Extrait tout le texte visible de cette image de manière précise et structurée. Fournis seulement le texte extrait au format markdown, sans commentaire supplémentaire."
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
    
    return chat_completion.choices[0].message.content




@ocr_bp.route('/ocr', methods=['POST'])
def ocr():
    if "image" not in request.files:
        return jsonify({"error": "Aucune image fournie"}), 400
    
    file = request.files["image"]
    image_bytes = file.read()
    mime_type = file.content_type
    
    try:
        texte = ocr_image_from_bytes(image_bytes, mime_type)
        return jsonify({"texte": texte})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
