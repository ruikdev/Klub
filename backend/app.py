from flask import Flask, jsonify, request
from ecole_direct_login import EcoleDirecteAPI
import sys
import json
import os
import base64
from datetime import datetime
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

app = Flask(__name__)

# Fichier de configuration
CONFIG_FILE = "ecole_direct_config.json"

def load_config():
    """Charger la configuration sauvegardée"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return None
    return None

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify(status="ok"), 200

@app.route("/api/devoirs", methods=["GET"])
def devoirs():
    config = load_config()
    if not config:
        return jsonify(error="Configuration non trouvée"), 500
    
    api = EcoleDirecteAPI()
    
    identifiant = config.get('identifiant')
    motdepasse = config.get('motdepasse')
    cn = config.get('cn')
    cv = config.get('cv')
    
    if not identifiant or not motdepasse or not cn or not cv:
        return jsonify(error="Identifiants manquants dans la configuration"), 500
    
    if not api.login(identifiant, motdepasse, cn, cv):
        return jsonify(error="Échec de la connexion"), 401
    
    devoirs_data = api.get_devoirs()
    
    if devoirs_data is None:
        return jsonify(error="Impossible de récupérer les devoirs"), 500
    
    devoirs_avec_details = {}
    for date, devoirs_list in devoirs_data.items():
        details = api.get_devoirs_pour_date(date)
        
        # Décoder les contenus base64 dans les détails
        if details and 'matieres' in details:
            for matiere in details['matieres']:
                if 'aFaire' in matiere and matiere['aFaire'].get('contenu'):
                    try:
                        contenu_decode = base64.b64decode(matiere['aFaire']['contenu']).decode('utf-8')
                        matiere['aFaire']['contenu_decode'] = contenu_decode
                    except:
                        matiere['aFaire']['contenu_decode'] = None
        
        devoirs_avec_details[date] = {
            "devoirs": devoirs_list,
            "details": details
        }
    
    return jsonify(devoirs_avec_details), 200

@app.route("/api/chat", methods=["POST"])
def requests_ia():
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
        config = load_config()
        if config:
            api = EcoleDirecteAPI()
            identifiant = config.get('identifiant')
            motdepasse = config.get('motdepasse')
            cn = config.get('cn')
            cv = config.get('cv')
            
            if api.login(identifiant, motdepasse, cn, cv):
                devoirs_data = api.get_devoirs()
                
                # Chercher le devoir correspondant à l'ID
                devoir_trouve = None
                date_devoir = None
                
                for date, devoirs_list in devoirs_data.items():
                    for devoir in devoirs_list:
                        if devoir.get('idDevoir') == id_devoir:
                            devoir_trouve = devoir
                            date_devoir = date
                            break
                    if devoir_trouve:
                        break
                
                if devoir_trouve:
                    # Récupérer les détails du devoir
                    details = api.get_devoirs_pour_date(date_devoir)
                    
                    contexte_devoir = f"\n\n**INFORMATIONS DU DEVOIR :**\n"
                    contexte_devoir += f"- Matière : {devoir_trouve.get('matiere', 'N/A')}\n"
                    contexte_devoir += f"- Pour le : {date_devoir}\n"
                    contexte_devoir += f"- Donné le : {devoir_trouve.get('donneLe', 'N/A')}\n"
                    
                    if devoir_trouve.get('interrogation'):
                        contexte_devoir += "- ⚠️ INTERROGATION\n"
                    
                    # Ajouter le contenu du devoir s'il existe
                    if details and 'matieres' in details:
                        for matiere in details['matieres']:
                            if matiere.get('id') == id_devoir and 'aFaire' in matiere:
                                try:
                                    contenu_encode = matiere['aFaire'].get('contenu', '')
                                    if contenu_encode:
                                        contenu_decode = base64.b64decode(contenu_encode).decode('utf-8')
                                        contexte_devoir += f"- Contenu du devoir : {contenu_decode}\n"
                                except:
                                    pass

    system_prompt = (
        "Tu es 'Klub AI', un assistant pédagogique expert et bienveillant. "
        "Ton but est d'aider les élèves à comprendre leurs cours et devoirs. "
        "Instructions : "
        "1. Sois pédagogique : n'envoie pas juste la réponse, explique la démarche. "
        "2. Sois concis mais complet. "
        "3. Utilise le Markdown (gras, listes, blocs de code) pour rendre la réponse lisible. "
        "4. Si la question est floue, demande des précisions. "
        "5. Si un contexte de devoir est fourni, utilise-le pour personnaliser ta réponse."
    )

    prompt_utilisateur = f"{contexte_devoir}\n\nL'élève pose la question suivante : {question}"

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt_utilisateur},
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            max_tokens=1024,
        )
        
        reponse = chat_completion.choices[0].message.content
        return jsonify(response=reponse), 200

    except Exception as e:
        print(f"Erreur Groq: {e}")
        return jsonify(error="Erreur lors de la génération de la réponse"), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
