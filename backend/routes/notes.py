from flask import Blueprint, jsonify, request
from utils import get_notes, get_notes_last_trimester
from groq import Groq
import os

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

notes_bp = Blueprint('notes', __name__, url_prefix='/api')

@notes_bp.route('/notes', methods=['GET'])
def notes():
    """Récupérer tous les notes avec leurs détails"""
    notes_data, error = get_notes()
    
    if error:
        return jsonify(error=error), 500
    
    return jsonify(notes_data), 200


@notes_bp.route('/notes/commentaire', methods=['GET'])
def commentaire():
    """Générer une appréciation des notes du dernier trimestre avec l'IA"""
    notes_data, error = get_notes_last_trimester()
    
    if error:
        return jsonify(error=error), 500
    
    # Préparer le contexte des notes pour l'IA
    notes_list = notes_data.get('notes', [])
    
    if not notes_list:
        return jsonify(error="Aucune note disponible pour générer une appréciation"), 404
    
    # Grouper les notes par matière et calculer les moyennes
    matieres_data = {}
    for note in notes_list:
        matiere = note.get('libelleMatiere', 'Inconnue')
        if matiere not in matieres_data:
            matieres_data[matiere] = {
                'notes': [],
                'total_points': 0,
                'total_coef': 0
            }
        
        valeur = note.get('valeur', '0').replace(',', '.')
        try:
            valeur_num = float(valeur)
            note_sur = float(note.get('noteSur', '20'))
            coef = float(note.get('coef', '1'))
            
            # Convertir sur 20
            note_sur_20 = (valeur_num / note_sur) * 20
            
            matieres_data[matiere]['notes'].append({
                'devoir': note.get('devoir', ''),
                'note': valeur,
                'sur': note.get('noteSur', '20'),
                'date': note.get('date', '')
            })
            matieres_data[matiere]['total_points'] += note_sur_20 * coef
            matieres_data[matiere]['total_coef'] += coef
        except:
            continue
    
    # Construire le contexte pour l'IA
    contexte = "Voici les notes de l'élève pour le trimestre en cours :\n\n"
    
    for matiere, data in matieres_data.items():
        if data['total_coef'] > 0:
            moyenne = data['total_points'] / data['total_coef']
            contexte += f"**{matiere}** - Moyenne: {moyenne:.2f}/20\n"
            contexte += f"  Nombre de notes: {len(data['notes'])}\n"
            for n in data['notes'][:3]:  # Limiter à 3 notes par matière
                contexte += f"  - {n['devoir']}: {n['note']}/{n['sur']}\n"
            contexte += "\n"
    
    system_prompt = (
        "Tu es un professeur principal qui rédige l'appréciation générale pour le bulletin scolaire d'un élève. "
        "INSTRUCTIONS PRÉCISES : "
        "1. COMMENCE par identifier les matières où l'élève a les meilleures moyennes (au-dessus de 12/20) et félicite-le explicitement pour ces résultats. "
        "2. ENSUITE, mentionne les matières où il y a des difficultés (en-dessous de 10/20) sans dramatiser. "
        "3. TERMINE par un conseil d'action concret et personnalisé selon son profil (ex: 'intensifier les révisions en mathématiques', 'continuer sur cette lancée', 'ne pas se décourager'). "
        "4. STRUCTURE obligatoire : 3 phrases maximum - Points forts / Points d'amélioration / Conseil. "
        "5. TON professionnel et bienveillant. N'utilise JAMAIS les notes chiffrées exactes, utilise des expressions comme 'résultats satisfaisants', 'très bons résultats', 'quelques difficultés', 'des fragilités'. "
        "6. Varie le vocabulaire : 'persévérance', 'travail régulier', 'efforts', 'investissement', 'rigueur', 'sérieux'."
        "7. Prends en compte les dernières notes du trimestre pour formuler ton appréciation, en mettant l'accent sur les tendances récentes plutôt que sur les notes isolées."
    )
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": contexte}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.6,
            max_tokens=300
        )
        
        appreciation = chat_completion.choices[0].message.content
        
        return jsonify({
            "appreciation": appreciation,
            "notes_analysees": len(notes_list),
            "matieres": list(matieres_data.keys())
        }), 200
        
    except Exception as e:
        return jsonify(error=f"Erreur lors de la génération de l'appréciation: {str(e)}"), 500