"""
Script d'exemple pour utiliser EcoleDirecte
Première utilisation : vous devrez obtenir vos codes cn/cv
Ensuite : sauvegardez-les dans ecole_direct_config.json
"""

from ecole_direct_login import EcoleDirecteAPI
import json
import os
import base64
from datetime import datetime, timedelta

# Fichier de configuration
CONFIG_FILE = "ecole_direct_config.json"

def load_config():
    """Charger la configuration sauvegardée"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"✗ Erreur: Le fichier {CONFIG_FILE} est vide ou mal formé.")
            return {}
    return {}

def save_config(config):
    """Sauvegarder la configuration"""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)
    print(f"✓ Configuration sauvegardée dans {CONFIG_FILE}")

def main():
    print("╔════════════════════════════════════════╗")
    print("║    Mon Script EcoleDirecte             ║")
    print("╚════════════════════════════════════════╝\n")
    
    # Charger la config
    config = load_config()
    
    # Demander les identifiants si pas sauvegardés
    if not config.get('identifiant'):
        print("Première utilisation - Configuration du compte\n")
        config['identifiant'] = input("Identifiant EcoleDirecte: ")
        config['motdepasse'] = input("Mot de passe: ")
        save_config(config)
        print()
    
    # Créer l'API
    api = EcoleDirecteAPI()
    
    # Se connecter
    identifiant = config['identifiant']
    motdepasse = config['motdepasse']
    cn = config.get('cn')
    cv = config.get('cv')
    
    print(f"Connexion en tant que {identifiant}...")
    
    # Si pas de codes cn/cv, il faudra faire le QCM manuellement
    # Pour l'instant, on utilise ceux de votre HAR
    if not cn or not cv:
        print("\n⚠ Codes cn/cv manquants!")
        print("Pour obtenir ces codes, vous devez :")
        print("1. Vous connecter sur www.ecoledirecte.com avec Chrome")
        print("2. Ouvrir les DevTools (F12) > onglet Network")
        print("3. Vous connecter et chercher la requête 'login.awp' POST qui réussit")
        print("4. Dans l'onglet Payload, copier les valeurs 'cn' et 'cv'\n")
        
        cn = input("Entrez le code cn: ")
        cv = input("Entrez le code cv: ")
        
        # Sauvegarder
        config['cn'] = cn
        config['cv'] = cv
        save_config(config)
    
    # Connexion
    if api.login(identifiant, motdepasse, cn, cv):
        print("\n" + "="*60)
        print("✓ CONNECTÉ AVEC SUCCÈS!")
        print("="*60)
        
        # Menu d'options
        while True:
            print("\n╔════════════════════════════════════════╗")
            print("║           QUE VOULEZ-VOUS FAIRE ?      ║")
            print("╠════════════════════════════════════════╣")
            print("║  1. Voir mes notes                     ║")
            print("║  2. Voir mon emploi du temps           ║")
            print("║  3. Voir mes devoirs                   ║")
            print("║  4. Afficher mes informations          ║")
            print("║  5. Quitter                            ║")
            print("╚════════════════════════════════════════╝")
            
            choix = input("\nVotre choix (1-5): ")
            
            if choix == "1":
                print("\n" + "="*60)
                print("📚 MES NOTES")
                print("="*60)
                notes_data = api.get_notes()
                if notes_data:
                    notes = notes_data.get('notes', [])
                    if notes:
                        print(f"\nVous avez {len(notes)} notes:\n")
                        for note in notes[-10:]:  # Les 10 dernières
                            print(f"  • {note['libelleMatiere']}")
                            print(f"    {note['devoir']}")
                            print(f"    Note: {note['valeur']}/{note['noteSur']} (Coef: {note['coef']})")
                            print(f"    Date: {note['date']}")
                            print()
                    else:
                        print("Aucune note disponible")
            
            elif choix == "2":
                print("\n" + "="*60)
                print("📅 MON EMPLOI DU TEMPS")
                print("="*60)
                
                print("\nQuel jour voulez-vous consulter ?")
                print("1. Aujourd'hui")
                print("2. Demain")
                print("3. Après-demain")
                print("4. Choisir une date spécifique")
                
                choix_date = input("\nVotre choix (1-4): ")
                
                date_choisie = None
                if choix_date == "1":
                    date_choisie = datetime.now()
                elif choix_date == "2":
                    date_choisie = datetime.now() + timedelta(days=1)
                elif choix_date == "3":
                    date_choisie = datetime.now() + timedelta(days=2)
                elif choix_date == "4":
                    date_str = input("Entrez la date (YYYY-MM-DD): ")
                    try:
                        date_choisie = datetime.strptime(date_str, "%Y-%m-%d")
                    except:
                        print("❌ Format de date invalide")
                        continue
                else:
                    print("❌ Choix invalide")
                    continue
                
                date_str = date_choisie.strftime("%Y-%m-%d")
                jour_semaine = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"][date_choisie.weekday()]
                date_fr = date_choisie.strftime("%d/%m/%Y")
                
                print(f"\nEmploi du temps pour {jour_semaine} {date_fr}:\n")
                
                edt = api.get_emploi_du_temps_jour(date_str)
                if edt:
                    for cours in edt:
                        heure_debut = cours['start_date'].split()[1]
                        heure_fin = cours['end_date'].split()[1]
                        print(f"  {heure_debut} - {heure_fin} | {cours['matiere']}")
                        print(f"    Prof: {cours['prof']} | Salle: {cours['salle']}")
                        if cours['isAnnule']:
                            print("    ⚠ COURS ANNULÉ")
                        print()
                else:
                    print("Pas de cours ce jour-là")
            
            elif choix == "3":
                print("\n" + "="*60)
                print("📝 MES DEVOIRS À FAIRE")
                print("="*60)
                
                devoirs_data = api.get_devoirs()
                if devoirs_data:
                    # Compter le total de devoirs
                    total_devoirs = sum(len(devoirs) for devoirs in devoirs_data.values())
                    
                    if total_devoirs > 0:
                        print(f"\nVous avez {total_devoirs} devoirs à faire:\n")
                        
                        # Afficher les devoirs par date
                        for date, devoirs in sorted(devoirs_data.items()):
                            if devoirs:
                                # Formater la date
                                date_obj = datetime.strptime(date, "%Y-%m-%d")
                                date_fr = date_obj.strftime("%d/%m/%Y")
                                jour_semaine = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"][date_obj.weekday()]
                                
                                print(f"─── {jour_semaine} {date_fr} ───")
                                for devoir in devoirs:
                                    status = "✓" if devoir.get('effectue') else "○"
                                    interro = " ⚠ INTERRO" if devoir.get('interrogation') else ""
                                    print(f"  {status} {devoir['matiere']}{interro}")
                                    print(f"    Donné le: {devoir['donneLe']}")
                                    
                                    # Option pour voir les détails d'un devoir
                                    voir_details = input(f"    Voir les détails? (o/n): ")
                                    if voir_details.lower() == 'o':
                                        details = api.get_devoirs_pour_date(date)
                                        if details and 'matieres' in details:
                                            for matiere in details['matieres']:
                                                if matiere.get('id') == devoir.get('idDevoir'):
                                                    if 'aFaire' in matiere and matiere['aFaire'].get('contenu'):
                                                        # Décoder le contenu base64
                                                        try:
                                                            contenu = base64.b64decode(matiere['aFaire']['contenu']).decode('utf-8')
                                                            # Enlever les balises HTML basiques
                                                            contenu = contenu.replace('<p>', '').replace('</p>', '\n').replace('<br>', '\n')
                                                            print(f"\n    📋 Contenu du devoir:")
                                                            print(f"    {contenu}")
                                                        except:
                                                            print(f"    Impossible de décoder le contenu")
                                                    
                                                    if 'aFaire' in matiere and matiere['aFaire'].get('documents'):
                                                        print(f"    📎 Pièces jointes: {len(matiere['aFaire']['documents'])}")
                                    print()
                    else:
                        print("\n🎉 Aucun devoir à faire!")
                else:
                    print("\nImpossible de récupérer les devoirs")
            
            elif choix == "4":
                print("\n" + "="*60)
                print("👤 MES INFORMATIONS")
                print("="*60)
                acc = api.account_data
                print(f"\nNom: {acc['prenom']} {acc['nom']}")
                print(f"Classe: {acc['profile']['classe']['libelle']}")
                print(f"Établissement: {acc['nomEtablissement']}")
                print(f"Email: {acc['email']}")
                print(f"Dernière connexion: {acc['lastConnexion']}")
            
            elif choix == "5":
                print("\n👋 Au revoir!")
                break
            
            else:
                print("\n❌ Choix invalide")
    
    else:
        print("\n❌ Échec de la connexion")
        print("Vérifiez vos identifiants et codes cn/cv")

if __name__ == "__main__":
    main()
