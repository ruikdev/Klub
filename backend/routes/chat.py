from flask import Blueprint, jsonify, request
import os
from groq import Groq
from utils import build_devoir_context

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

chat_bp = Blueprint('chat', __name__, url_prefix='/api')

@chat_bp.route('/chat_devoirs', methods=['POST'])
def requests_ia():
    """Route d'aide pédagogique avec IA"""
    data = request.get_json(force=True, silent=True)
    
    if data is None:
        return jsonify(error="JSON invalide ou vide"), 400
    
    id_devoir = data.get("id")    
    question = data.get("question", "").strip()

    if not question:
        return jsonify(error="Question manquante ou vide"), 400

    # Récupérer les informations du devoir si un ID est fourni
    contexte_devoir = ""
    if id_devoir:
        contexte, error = build_devoir_context(id_devoir)
        if error:
            return jsonify(error=error), 404
        contexte_devoir = contexte

    system_prompt = (
        "Tu es 'Klub AI', un assistant pédagogique expert et bienveillant. "
        "Ton but est d'aider les élèves à comprendre leurs cours et devoirs. "
        "Instructions : "
        "1. Sois pédagogique : n'envoie pas juste la réponse, explique la démarche. "
        "2. Sois concis mais complet. "
        "3. Utilise le Markdown (gras, listes, blocs de code) pour rendre la réponse lisible. "
        "4. Si la question est floue ou manque d'informations, fais des hypothèses raisonnables et explique plusieurs cas possibles au lieu de demander des précisions. "
        "5. Si un contexte de devoir est fourni, utilise-le pour personnaliser ta réponse. "
        "6. Si tu as un doute sur une information, fais-le remarquer à l'élève et encourage-le à vérifier. "
        "7. Reste toujours positif et encourageant, même si la question est basique ou si l'élève fait une erreur. "
        "8. Ta réponse doit être adaptée au niveau d'un élève de collège ou lycée, en fonction du contexte fourni. "
        "9. IMPORTANT : Ta réponse doit clore la conversation. Ne pose JAMAIS de question à l'élève car il ne pourra pas te répondre directement. Fournis toujours une réponse complète et autonome."
    )

    prompt_utilisateur = f"{contexte_devoir}\n\nL'élève pose la question suivante : {question}"

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt_utilisateur},
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.6,
            max_tokens=1024,
        )
        
        reponse = chat_completion.choices[0].message.content
        return jsonify(response=reponse), 200

    except Exception as e:
        print(f"Erreur Groq: {e}")
        return jsonify(error="Erreur lors de la génération de la réponse"), 500
