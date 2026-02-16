"""
Api EcoleDirecte - Connexion et récupération de données depuis EcoleDirecte
- Permet de se connecter à EcoleDirecte en gérant l'authentification
"""



import requests
import json
import base64
from urllib.parse import quote

class EcoleDirecteAPI:
    def __init__(self):
        self.base_url = "https://api.ecoledirecte.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
        })
        self.token = None
        self.account_data = None
        
    def login(self, identifiant, motdepasse, cn=None, cv=None):
        """Se connecter à EcoleDirecte"""
        print("Connexion à EcoleDirecte...")
        
        # Étape 1: Récupérer le cookie GTK
        gtk_url = f"{self.base_url}/v3/login.awp?gtk=1&v=4.88.0"
        gtk_response = self.session.get(gtk_url)
        
        if 'GTK' in self.session.cookies:
            gtk_token = self.session.cookies['GTK']
            self.session.headers['X-Gtk'] = gtk_token
            print(f"Cookie GTK récupéré")
        
        # Étape 2: Tentative de connexion
        login_url = f"{self.base_url}/v3/login.awp?v=4.88.0"
        login_data = {
            "identifiant": identifiant,
            "motdepasse": motdepasse,
            "isReLogin": False,
            "uuid": ""
        }
        
        # Ajouter cn/cv si fournis (pour éviter le QCM)
        if cn and cv:
            login_data["cn"] = cn
            login_data["cv"] = cv
            login_data["fa"] = [{"cn": cn, "cv": cv, "uniq": True}]
        
        # Encoder les données au format form-urlencoded
        encoded_data = f"data={json.dumps(login_data)}"
        
        response = self.session.post(
            login_url,
            data=encoded_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        
        result = response.json()
        
        # Vérifier le code de réponse
        if result['code'] == 200:
            self.token = result['token']
            self.account_data = result['data']['accounts'][0]
            self.session.headers['X-Token'] = self.token
            print(f"✓ Connexion réussie!")
            print(f"  Utilisateur: {self.account_data['prenom']} {self.account_data['nom']}")
            print(f"  Type de compte: {self.account_data['typeCompte']}")
            print(f"  Établissement: {self.account_data['nomEtablissement']}")
            return True
            
        elif result['code'] == 250:
            print("⚠ Authentification double facteur requise (QCM)")
            # Sauvegarder le token de la première tentative
            if result.get('token'):
                self.token = result['token']
                self.session.headers['X-Token'] = self.token
            return self._handle_double_auth(identifiant, motdepasse)
            
        elif result['code'] == 505:
            print(f"✗ Erreur de connexion: {result['message']}")
            return False
            
        else:
            print(f"✗ Erreur {result['code']}: {result.get('message', 'Erreur inconnue')}")
            return False
    
    def _handle_double_auth(self, identifiant, motdepasse):
        """Gérer l'authentification double facteur (QCM)"""
        print("\nRécupération du QCM...")
        
        # Récupérer le QCM (utiliser verbe=get dans l'URL)
        qcm_url = f"{self.base_url}/v3/connexion/doubleauth.awp?verbe=get"
        qcm_response = self.session.post(
            qcm_url,
            data="data={}",
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        
        qcm_result = qcm_response.json()
        
        if qcm_result['code'] != 200:
            print(f"✗ Erreur lors de la récupération du QCM: {qcm_result.get('message')}")
            return False
        
        # Décoder la question et les propositions
        question = base64.b64decode(qcm_result['data']['question']).decode('utf-8')
        propositions = [
            base64.b64decode(prop).decode('utf-8')
            for prop in qcm_result['data']['propositions']
        ]
        
        # Afficher le QCM
        print(f"\nQuestion: {question}")
        for i, prop in enumerate(propositions):
            print(f"  {i+1}. {prop}")
        
        # Demander la réponse à l'utilisateur
        while True:
            try:
                choix = int(input("\nChoisissez votre réponse (numéro): ")) - 1
                if 0 <= choix < len(propositions):
                    break
                print("Numéro invalide, réessayez.")
            except ValueError:
                print("Veuillez entrer un numéro valide.")
        
        # Envoyer la réponse encodée en base64
        reponse_encodee = qcm_result['data']['propositions'][choix]
        answer_data = {"choix": reponse_encodee}
        
        answer_response = self.session.post(
            qcm_url,
            data=f"data={json.dumps(answer_data)}",
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        
        answer_result = answer_response.json()
        
        if answer_result['code'] != 200:
            print(f"✗ Réponse incorrecte ou erreur")
            return False
        
        # Récupérer cn et cv
        cn = answer_result['data']['cn']
        cv = answer_result['data']['cv']
        
        print(f"\n⚠ IMPORTANT: Sauvegardez ces codes pour éviter le QCM à l'avenir!")
        print(f"cn: {cn}")
        print(f"cv: {cv}")
        
        # Refaire la connexion avec cn et cv
        print("\nReconnexion avec les codes de vérification...")
        login_url = f"{self.base_url}/v3/login.awp?v=4.88.0"
        login_data = {
            "identifiant": identifiant,
            "motdepasse": motdepasse,
            "cn": cn,
            "cv": cv,
            "isReLogin": False,
            "uuid": "",
            "fa": [{"cn": cn, "cv": cv, "uniq": True}]
        }
        
        response = self.session.post(
            login_url,
            data=f"data={json.dumps(login_data)}",
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        
        result = response.json()
        
        if result['code'] == 200:
            self.token = result['token']
            self.account_data = result['data']['accounts'][0]
            self.session.headers['X-Token'] = self.token
            print(f"✓ Connexion réussie après QCM!")
            print(f"  Utilisateur: {self.account_data['prenom']} {self.account_data['nom']}")
            return True
        else:
            print(f"✗ Erreur après QCM: {result.get('message')}")
            return False
    
    def get_emploi_du_temps(self, date_debut, date_fin):
        """Récupérer l'emploi du temps"""
        if not self.token or not self.account_data:
            print("✗ Vous devez d'abord vous connecter")
            return None
        
        eleve_id = self.account_data['id']
        url = f"{self.base_url}/v3/E/{eleve_id}/emploidutemps.awp?verbe=get"
        
        data = {
            "dateDebut": date_debut,
            "dateFin": date_fin,
            "avecTrous": False
        }
        
        response = self.session.post(
            url,
            data=f"data={json.dumps(data)}",
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        
        result = response.json()
        if result['code'] == 200:
            return result['data']
        return None
    
    def get_emploi_du_temps_jour(self, date=None):
        """
        Récupérer l'emploi du temps pour un jour spécifique
        Args:
            date (str): Date au format YYYY-MM-DD ou None pour aujourd'hui
        """
        from datetime import datetime
        
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        return self.get_emploi_du_temps(date, date)
    
    def get_notes(self):
        """Récupérer les notes"""
        if not self.token or not self.account_data:
            print("✗ Vous devez d'abord vous connecter")
            return None
        
        eleve_id = self.account_data['id']
        url = f"{self.base_url}/v3/eleves/{eleve_id}/notes.awp?verbe=get"
        
        data = {"anneeScolaire": ""}
        
        response = self.session.post(
            url,
            data=f"data={json.dumps(data)}",
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        
        result = response.json()
        if result['code'] == 200:
            return result['data']
        return None
    
    def get_devoirs(self):
        """Récupérer tous les devoirs à faire (à partir d'aujourd'hui)"""
        if not self.token or not self.account_data:
            print("✗ Vous devez d'abord vous connecter")
            return None
        
        eleve_id = self.account_data['id']
        url = f"{self.base_url}/v3/Eleves/{eleve_id}/cahierdetexte.awp?verbe=get"
        
        response = self.session.post(
            url,
            data="data={}",
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        
        result = response.json()
        if result['code'] == 200:
            return result['data']
        return None
    
    def get_devoirs_pour_date(self, date):
        """
        Récupérer les devoirs détaillés pour une date spécifique
        Args:
            date (str): Date au format YYYY-MM-DD
        """
        if not self.token or not self.account_data:
            print("✗ Vous devez d'abord vous connecter")
            return None
        
        eleve_id = self.account_data['id']
        url = f"{self.base_url}/v3/Eleves/{eleve_id}/cahierdetexte/{date}.awp?verbe=get"
        
        response = self.session.post(
            url,
            data="data={}",
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        
        result = response.json()
        if result['code'] == 200:
            return result['data']
        return None
    
    def marquer_devoir_fait(self, id_devoir, fait=True):
        """
        Marquer un devoir comme fait ou non fait
        Args:
            id_devoir (int): ID du devoir
            fait (bool): True pour marquer fait, False pour marquer non fait
        """
        if not self.token or not self.account_data:
            print("✗ Vous devez d'abord vous connecter")
            return None
        
        eleve_id = self.account_data['id']
        url = f"{self.base_url}/v3/Eleves/{eleve_id}/cahierdetexte.awp?verbe=put"
        
        data = {
            "idDevoirsEffectues": [id_devoir] if fait else [],
            "idDevoirsNonEffectues": [] if fait else [id_devoir]
        }
        
        response = self.session.post(
            url,
            data=f"data={json.dumps(data)}",
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        
        result = response.json()
        if result['code'] == 200:
            return True
        return False


