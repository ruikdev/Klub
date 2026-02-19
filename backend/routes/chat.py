from flask import Blueprint, jsonify, request
import os
import json
from groq import Groq
from utils import build_devoir_context, get_devoirs_with_details, get_notes, decode_base64_content

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

chat_bp = Blueprint('chat', __name__, url_prefix='/api')


# ─────────────────────────────────────────────
# Outils pour le chat global
# ─────────────────────────────────────────────

def tool_get_cours(matiere: str = None) -> dict:
    """Retourne les cours disponibles, filtrés par matière si précisé."""
    cours_dir = "cours"
    result = {}

    if not os.path.exists(cours_dir):
        return {"error": "Dossier cours introuvable"}

    for m in os.listdir(cours_dir):
        matiere_path = os.path.join(cours_dir, m)
        if not os.path.isdir(matiere_path):
            continue
        if matiere and matiere.lower() not in m.lower():
            continue
        result[m] = []
        for fichier in os.listdir(matiere_path):
            if not fichier.endswith(".md"):
                continue
            fichier_path = os.path.join(matiere_path, fichier)
            try:
                with open(fichier_path, "r", encoding="utf-8") as f:
                    contenu = f.read()
                result[m].append({
                    "nom": os.path.splitext(fichier)[0],
                    "contenu": contenu
                })
            except Exception as e:
                result[m].append({"nom": os.path.splitext(fichier)[0], "erreur": str(e)})

    return {"cours": result}


def tool_get_devoirs() -> dict:
    """Retourne tous les devoirs à venir."""
    devoirs, error = get_devoirs_with_details()
    if error:
        return {"error": error}
    # Simplifier les données pour ne pas surcharger le contexte
    simplified = {}
    for date, data in devoirs.items():
        simplified[date] = []
        for devoir in data.get("devoirs", []):
            entry = {
                "id": devoir.get("idDevoir"),
                "matiere": devoir.get("matiere"),
                "donneLe": devoir.get("donneLe"),
                "interrogation": devoir.get("interrogation", False),
            }
            # Chercher le contenu dans les détails
            details = data.get("details")
            if details and "matieres" in details:
                for mat in details["matieres"]:
                    if str(mat.get("id")) == str(devoir.get("idDevoir")) and "aFaire" in mat:
                        contenu = decode_base64_content(mat["aFaire"].get("contenu", ""))
                        if contenu:
                            entry["contenu"] = contenu
            simplified[date].append(entry)
    return {"devoirs": simplified}


def tool_get_notes() -> dict:
    """Retourne les notes de l'élève."""
    notes_data, error = get_notes()
    if error:
        return {"error": error}
    # Simplifier : ne garder que les champs utiles
    notes_list = notes_data.get("notes", [])
    simplified = []
    for note in notes_list:
        simplified.append({
            "matiere": note.get("libelleMatiere"),
            "devoir": note.get("devoir"),
            "note": note.get("valeur"),
            "sur": note.get("noteSur"),
            "coef": note.get("coef"),
            "date": note.get("date"),
            "periode": note.get("codePeriode"),
        })
    return {"notes": simplified}


GLOBAL_TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "get_cours",
            "description": (
                "Retourne le contenu des cours disponibles (fichiers Markdown). "
                "Utilise cet outil quand l'élève pose une question sur un cours, une matière, ou veut réviser un chapitre."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "matiere": {
                        "type": "string",
                        "description": "Filtre par matière (ex: 'mathematique', 'francais', 'histoire'). Optionnel — si absent, retourne tous les cours."
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_devoirs",
            "description": (
                "Retourne la liste des devoirs à faire avec leur contenu et date de rendu. "
                "Utilise cet outil quand l'élève demande ce qu'il a à faire, ses devoirs, ou veut de l'aide sur un devoir."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_notes",
            "description": (
                "Retourne toutes les notes de l'élève avec les matières, moyennes et dates. "
                "Utilise cet outil quand l'élève pose une question sur ses notes, ses résultats ou sa moyenne."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]


def execute_global_tool(name: str, arguments: str) -> str:
    try:
        args = json.loads(arguments) if arguments else {}
    except Exception:
        args = {}

    if name == "get_cours":
        result = tool_get_cours(**args)
    elif name == "get_devoirs":
        result = tool_get_devoirs()
    elif name == "get_notes":
        result = tool_get_notes()
    else:
        result = {"error": f"Outil inconnu : {name}"}

    return json.dumps(result, ensure_ascii=False)

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




@chat_bp.route('/cours/chat', methods=['POST'])
def requests_ia_cours():
    """Route d'aide pédagogique avec IA"""
    data = request.get_json(force=True, silent=True)
    
    if data is None:
        return jsonify(error="JSON invalide ou vide"), 400
    
    cours = data.get("cours")
    question = data.get("question")

    if not question or not cours:
        return jsonify(error="Question ou cours manquante ou vide"), 400

    system_prompt = (
        "Tu es 'Klub AI', un assistant pédagogique expert et bienveillant. "
        "Ton but est d'aider les élèves à comprendre leurs cours et devoirs. "
        "Instructions : "
        "1. Sois pédagogique : n'envoie pas juste la réponse, explique la démarche. "
        "2. Sois concis mais complet. "
        "3. Utilise le Markdown (gras, listes, blocs de code) pour rendre la réponse lisible. "
        "4. Si la question est floue ou manque d'informations, fais des hypothèses raisonnables et explique plusieurs cas possibles au lieu de demander des précisions. "
        "5. Utilise le cours fourni pour répondre à la question."
        "6. Si tu as un doute sur une information, fais-le remarquer à l'élève et encourage-le à vérifier. "
        "7. Reste toujours positif et encourageant, même si la question est basique ou si l'élève fait une erreur. "
        "8. Ta réponse doit être adaptée au niveau d'un élève de collège ou lycée, en fonction du contexte fourni. "
        "9. IMPORTANT : Ta réponse doit clore la conversation. Ne pose JAMAIS de question à l'élève car il ne pourra pas te répondre directement. Fournis toujours une réponse complète et autonome."
        "10. CRITIQUE : Réponds UNIQUEMENT en utilisant les informations du cours fourni. "
        "Si l'information n'est PAS dans le cours, réponds EXACTEMENT : "
        "'⚠️ Cette information ne figure pas dans le cours fourni. Je ne peux pas répondre sans risque d'erreur.' "
        "Ne fais JAMAIS d'hypothèses ou d'explications générales si elles ne sont pas dans le cours."
    )

    prompt_utilisateur = f"{cours}\n\nL'élève pose la question suivante : {question}"

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt_utilisateur},
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.4,
            max_tokens=1024,
        )

        reponse = chat_completion.choices[0].message.content
        return jsonify(response=reponse), 200

    except Exception as e:
        print(f"Erreur Groq cours: {e}")
        return jsonify(error="Erreur lors de la génération de la réponse"), 500


# ─────────────────────────────────────────────
# Route Chat Global avec outils (cours, devoirs, notes)
# ─────────────────────────────────────────────

@chat_bp.route('/chat/global', methods=['POST'])
def chat_global():
    """Chat IA général avec accès aux cours, devoirs et notes via tool calling."""
    data = request.get_json(force=True, silent=True)

    if data is None:
        return jsonify(error="JSON invalide ou vide"), 400

    messages_input = data.get("messages", [])
    question = data.get("question", "").strip()

    if not question and not messages_input:
        return jsonify(error="Question manquante"), 400

    system_prompt = (
        "Tu es 'Klub AI', un assistant scolaire intelligent et bienveillant. "
        "Tu as accès à des outils pour consulter les cours, les devoirs et les notes de l'élève. "
        "Comportement attendu :\n"
        "1. Utilise toujours les outils disponibles avant de répondre si la question concerne des cours, des devoirs ou des notes.\n"
        "2. Pour les questions sur un cours ou une matière, utilise get_cours avec la matière concernée.\n"
        "3. Pour les devoirs, utilise get_devoirs.\n"
        "4. Pour les notes ou moyennes, utilise get_notes.\n"
        "5. Sois pédagogique : explique la démarche, pas juste la réponse.\n"
        "6. Utilise le Markdown (gras, listes, formules) pour rendre ta réponse lisible.\n"
        "7. Adapte ton niveau à un élève de collège ou lycée.\n"
        "8. Reste positif et encourageant.\n"
        "9. Tu peux maintenir une conversation : tiens compte de l'historique des messages précédents."
    )

    # Construire l'historique de messages
    messages = [{"role": "system", "content": system_prompt}]

    # Ajouter l'historique de conversation si fourni
    for msg in messages_input:
        role = msg.get("role")
        content = msg.get("content", "")
        if role in ("user", "assistant") and content:
            messages.append({"role": role, "content": content})

    # Ajouter la question courante si pas déjà dans l'historique
    if question:
        messages.append({"role": "user", "content": question})

    try:
        # Boucle tool calling (même principe que test_chatbot.py)
        max_iterations = 5
        iteration = 0

        while iteration < max_iterations:
            iteration += 1

            response = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=messages,
                tools=GLOBAL_TOOLS_SCHEMA,
                tool_choice="auto",
                max_completion_tokens=4096,
                temperature=0.5,
            )

            choice = response.choices[0]
            message = choice.message

            # L'IA veut utiliser un ou plusieurs outils
            if choice.finish_reason == "tool_calls":
                messages.append(message)

                for tool_call in message.tool_calls:
                    name = tool_call.function.name
                    args = tool_call.function.arguments
                    print(f"[chat/global] Outil appelé : {name}({args})")

                    result = execute_global_tool(name, args)
                    print(f"[chat/global] Résultat : {result[:200]}...")

                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result
                    })
                # Reboucler pour que l'IA formule sa réponse finale

            else:
                # Réponse finale de l'IA
                return jsonify(response=message.content), 200

        return jsonify(error="Trop d'itérations de tool calling"), 500

    except Exception as e:
        print(f"Erreur Groq chat/global: {e}")
        return jsonify(error="Erreur lors de la génération de la réponse"), 500
