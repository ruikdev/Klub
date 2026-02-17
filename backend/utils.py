import json
import os
import base64
from ecole_direct_login import EcoleDirecteAPI

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


def get_api_instance():
    """Créer une instance de l'API EcoleDirecte et se connecter"""
    config = load_config()
    if not config:
        return None, "Configuration non trouvée"
    
    api = EcoleDirecteAPI()
    identifiant = config.get('identifiant')
    motdepasse = config.get('motdepasse')
    cn = config.get('cn')
    cv = config.get('cv')
    
    if not identifiant or not motdepasse or not cn or not cv:
        return None, "Identifiants manquants dans la configuration"
    
    if not api.login(identifiant, motdepasse, cn, cv):
        return None, "Échec de la connexion au service EcoleDirecte"
    
    return api, None


def decode_base64_content(contenu_encode):
    """Décoder un contenu base64"""
    try:
        if contenu_encode:
            return base64.b64decode(contenu_encode).decode('utf-8')
    except:
        pass
    return None


def get_devoirs_with_details():
    """Récupérer tous les devoirs avec leurs détails"""
    api, error = get_api_instance()
    if error:
        return None, error
    
    devoirs_data = api.get_devoirs()
    if devoirs_data is None:
        return None, "Impossible de récupérer les devoirs"
    
    devoirs_avec_details = {}
    for date, devoirs_list in devoirs_data.items():
        details = api.get_devoirs_pour_date(date)
        
        # Décoder les contenus base64 dans les détails
        if details and 'matieres' in details:
            for matiere in details['matieres']:
                if 'aFaire' in matiere and matiere['aFaire'].get('contenu'):
                    contenu_decode = decode_base64_content(matiere['aFaire']['contenu'])
                    matiere['aFaire']['contenu_decode'] = contenu_decode
        
        devoirs_avec_details[date] = {
            "devoirs": devoirs_list,
            "details": details
        }
    
    return devoirs_avec_details, None


def find_devoir_by_id(id_devoir):
    """Trouver un devoir par son ID et retourner ses infos + détails"""
    api, error = get_api_instance()
    if error:
        return None, None, error
    
    devoirs_data = api.get_devoirs()
    if devoirs_data is None:
        return None, None, "Impossible de récupérer les devoirs"
    
    # Chercher le devoir correspondant à l'ID
    devoir_trouve = None
    date_devoir = None
    
    for date, devoirs_list in devoirs_data.items():
        for devoir in devoirs_list:
            # idDevoir peut être int ou string selon l'API
            if str(devoir.get('idDevoir')) == str(id_devoir):
                devoir_trouve = devoir
                date_devoir = date
                break
        if devoir_trouve:
            break
    
    if not devoir_trouve:
        return None, None, f"Aucun devoir trouvé pour l'id {id_devoir}"
    
    # Récupérer les détails du devoir
    details = api.get_devoirs_pour_date(date_devoir)
    
    return devoir_trouve, details, None


def build_devoir_context(id_devoir):
    """Construire le contexte d'un devoir pour l'IA"""
    devoir_trouve, details, error = find_devoir_by_id(id_devoir)
    if error:
        return None, error
    
    contexte_devoir = f"\n\n**INFORMATIONS DU DEVOIR :**\n"
    contexte_devoir += f"- Matière : {devoir_trouve.get('matiere', 'N/A')}\n"
    contexte_devoir += f"- Pour le : {id_devoir}\n"  # La date était stockée dans date_devoir, adapter si besoin
    contexte_devoir += f"- Donné le : {devoir_trouve.get('donneLe', 'N/A')}\n"
    
    if devoir_trouve.get('interrogation'):
        contexte_devoir += "- ⚠️ INTERROGATION\n"
    
    # Ajouter le contenu du devoir s'il existe
    if details and 'matieres' in details:
        for matiere in details['matieres']:
            if str(matiere.get('id')) == str(id_devoir) and 'aFaire' in matiere:
                contenu_encode = matiere['aFaire'].get('contenu', '')
                contenu_decode = decode_base64_content(contenu_encode)
                if contenu_decode:
                    contexte_devoir += f"- Contenu du devoir : {contenu_decode}\n"
    
    return contexte_devoir, None

def get_notes():
    """Récupérer toutes les notes avec leurs détails"""
    api, error = get_api_instance()
    if error:
        return None, error
    
    notes_data = api.get_notes()
    if notes_data is None:
        return None, "Impossible de récupérer les notes"
    
    return notes_data, None


def get_notes_last_trimester():
    """Récupérer les notes du dernier trimestre uniquement"""
    api, error = get_api_instance()
    if error:
        return None, error
    
    notes_data = api.get_notes()
    if notes_data is None:
        return None, "Impossible de récupérer les notes"
    
    # Filtrer pour garder uniquement les notes du dernier trimestre
    if 'notes' not in notes_data or not notes_data['notes']:
        return notes_data, None
    
    # Trouver le dernier code de période (le plus récent)
    periodes_trouvees = set()
    for note in notes_data['notes']:
        if 'codePeriode' in note:
            periodes_trouvees.add(note['codePeriode'])
    
    if not periodes_trouvees:
        return notes_data, None
    
    # Trier les périodes pour trouver la plus récente
    # Format: A001 (1er trim), A002 (2ème trim), A003 (3ème trim)
    periodes_valides = sorted([p for p in periodes_trouvees if p.startswith('A0')], reverse=True)
    
    if not periodes_valides:
        return notes_data, None
    
    derniere_periode = periodes_valides[0]
    
    # Filtrer les notes pour garder uniquement celles du dernier trimestre
    notes_filtrees = [note for note in notes_data['notes'] if note.get('codePeriode') == derniere_periode]
    
    # Créer une copie des données avec les notes filtrées
    notes_data_filtrees = notes_data.copy()
    notes_data_filtrees['notes'] = notes_filtrees
    
    # Filtrer aussi la section LSUN si elle existe
    if 'LSUN' in notes_data:
        lsun_filtree = {}
        for periode, matieres in notes_data['LSUN'].items():
            # Vérifier si cette période correspond au dernier trimestre
            if periode == derniere_periode:
                lsun_filtree[periode] = matieres
        if lsun_filtree:
            notes_data_filtrees['LSUN'] = lsun_filtree
    
    return notes_data_filtrees, None
