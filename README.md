# Klub

**Tes cours, tes docs et ton IA au même endroit.**

Klub est une plateforme éducative intelligente qui permet aux élèves de consulter leurs devoirs depuis EcoleDirecte et d'obtenir une assistance pédagogique personnalisée grâce à l'intelligence artificielle.

## 📋 Table des matières

- [Fonctionnalités](#-fonctionnalités)
- [Architecture](#-architecture)
- [Prérequis](#-prérequis)
- [Installation](#-installation)
- [Configuration](#️-configuration)
- [Utilisation](#-utilisation)
- [Structure du projet](#-structure-du-projet)
- [API Documentation](#-api-documentation)
- [Développement](#-développement)
- [Contribution](#-contribution)
- [Licence](#-licence)

## ✨ Fonctionnalités

- **Synchronisation EcoleDirecte** : Récupération automatique des devoirs depuis votre compte EcoleDirecte
- **Assistant IA pédagogique** : Obtenez de l'aide pour comprendre vos devoirs avec Klub AI, propulsé par Groq
- **Interface moderne** : Application Angular responsive avec Tailwind CSS
- **API REST** : Backend Flask robuste pour la gestion des données
- **Déploiement facile** : Configuration Docker Compose pour un démarrage rapide

## 🏗️ Architecture

Le projet est composé de deux services principaux :

- **Frontend** : Application Angular 17 avec SSR (Server-Side Rendering)
- **Backend** : API Flask Python pour l'intégration EcoleDirecte et l'IA

```
┌─────────────────┐         ┌──────────────────┐
│                 │         │                  │
│  Frontend       │◄────────┤  Backend (Flask) │
│  (Angular 17)   │         │  Port 5000       │
│  Port 4200      │         │                  │
│                 │         └────────┬─────────┘
└─────────────────┘                  │
                                     │
                            ┌────────▼─────────┐
                            │                  │
                            │  EcoleDirecte    │
                            │  API             │
                            │                  │
                            └──────────────────┘
                            
                            ┌──────────────────┐
                            │                  │
                            │  Groq AI         │
                            │  (LLM)           │
                            │                  │
                            └──────────────────┘
```

## 📦 Prérequis

### Avec Docker (recommandé)
- Docker (version 20.10+)
- Docker Compose (version 2.0+)

### Sans Docker
- Python 3.11+
- Node.js 20+
- npm ou yarn

## 🚀 Installation

### Option 1 : Avec Docker Compose (recommandé)

1. **Cloner le repository**
   ```bash
   git clone https://github.com/ruikdev/Klub.git
   cd Klub
   ```

2. **Configurer les variables d'environnement** (voir section Configuration)

3. **Lancer l'application**
   ```bash
   docker-compose up -d
   ```

4. **Accéder à l'application**
   - Frontend : http://localhost:4200
   - Backend API : http://localhost:5000

### Option 2 : Installation locale

#### Backend

1. **Accéder au dossier backend**
   ```bash
   cd backend
   ```

2. **Créer un environnement virtuel**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Sur Windows: venv\Scripts\activate
   ```

3. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

4. **Lancer le serveur**
   ```bash
   python app.py
   ```

#### Frontend

1. **Accéder au dossier frontend**
   ```bash
   cd frontend
   ```

2. **Installer les dépendances**
   ```bash
   npm install
   ```

3. **Lancer le serveur de développement**
   ```bash
   npm start
   ```

## ⚙️ Configuration

### Configuration du Backend

1. **Créer un fichier `.env`** dans le dossier `backend/` :
   ```bash
   cp backend/exemple.env backend/.env
   ```

2. **Ajouter votre clé API Groq** dans `.env` :
   ```
   GROQ_API_KEY=votre_cle_api_groq_ici
   ```
   
   Obtenez une clé API gratuite sur [console.groq.com](https://console.groq.com)

3. **Configurer vos identifiants EcoleDirecte** :
   
   Créer un fichier `ecole_direct_config.json` dans `backend/` :
   ```bash
   cp backend/exemple.ecole_direct_config.json backend/ecole_direct_config.json
   ```
   
   Puis éditer le fichier avec vos identifiants :
   ```json
   {
     "identifiant": "votre_identifiant",
     "motdepasse": "votre_mot_de_passe",
     "cn": "votre_cn",
     "cv": "votre_cv"
   }
   ```

   > ⚠️ **Note** : Les valeurs `cn` et `cv` sont optionnelles mais permettent d'éviter le QCM de sécurité d'EcoleDirecte.

## 📱 Utilisation

### Récupérer vos devoirs

L'application se connecte automatiquement à EcoleDirecte et récupère vos devoirs. Ils sont disponibles dans l'interface frontend.

### Utiliser l'assistant IA

1. Sélectionnez un devoir dans l'interface
2. Posez votre question à Klub AI
3. Recevez une réponse pédagogique détaillée avec explications

L'IA prend en compte le contexte de votre devoir pour fournir une aide personnalisée.

## 📁 Structure du projet

```
Klub/
├── backend/                    # API Flask Backend
│   ├── routes/                # Routes API
│   │   ├── chat.py           # Routes pour l'IA
│   │   └── devoirs.py        # Routes pour les devoirs
│   ├── app.py                # Point d'entrée de l'application
│   ├── ecole_direct_login.py # Intégration EcoleDirecte
│   ├── utils.py              # Fonctions utilitaires
│   ├── requirements.txt      # Dépendances Python
│   ├── Dockerfile            # Configuration Docker
│   └── .env                  # Variables d'environnement (à créer)
│
├── frontend/                  # Application Angular Frontend
│   ├── src/                  # Code source
│   │   ├── app/             # Composants Angular
│   │   ├── assets/          # Ressources statiques
│   │   └── styles.css       # Styles globaux
│   ├── package.json         # Dépendances Node.js
│   ├── angular.json         # Configuration Angular
│   ├── tailwind.config.js   # Configuration Tailwind CSS
│   ├── nginx.conf           # Configuration Nginx
│   └── Dockerfile           # Configuration Docker
│
├── docker-compose.yml        # Configuration Docker Compose
├── LICENSE                   # Licence GNU GPL v3
└── README.md                # Ce fichier
```

## 📡 API Documentation

### Endpoints disponibles

#### `GET /api/health`
Vérifier le statut de l'API

**Réponse :**
```json
{
  "status": "ok"
}
```

#### `GET /api/devoirs`
Récupérer tous les devoirs avec leurs détails

**Réponse :**
```json
{
  "2024-02-15": {
    "devoirs": [...],
    "details": {...}
  },
  ...
}
```

#### `POST /api/chat`
Poser une question à l'assistant IA

**Corps de la requête :**
```json
{
  "id": "123",
  "question": "Comment résoudre cette équation ?"
}
```

**Réponse :**
```json
{
  "response": "Réponse de l'IA en Markdown..."
}
```

## 🛠️ Développement

### Technologies utilisées

**Backend :**
- Flask - Framework web Python
- Groq - API d'IA (LLM)
- Requests - Client HTTP
- Python-dotenv - Gestion des variables d'environnement

**Frontend :**
- Angular 17 - Framework JavaScript
- Tailwind CSS - Framework CSS utilitaire
- RxJS - Programmation réactive
- Marked - Parsing Markdown

### Commandes utiles

**Backend :**
```bash
# Activer l'environnement virtuel
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Lancer en mode développement
python app.py
```

**Frontend :**
```bash
# Installer les dépendances
npm install

# Lancer en mode développement
npm start

# Build de production
npm run build

# Lancer les tests
npm test
```

**Docker :**
```bash
# Lancer les conteneurs
docker-compose up -d

# Arrêter les conteneurs
docker-compose down

# Voir les logs
docker-compose logs -f

# Reconstruire les images
docker-compose build
```

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :

1. Fork le projet
2. Créer une branche pour votre fonctionnalité (`git checkout -b feature/AmazingFeature`)
3. Commit vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📄 Licence

Ce projet est sous licence GNU General Public License v3.0. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

---

**Développé avec ❤️ pour faciliter l'apprentissage des élèves**
