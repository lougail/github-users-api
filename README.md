# GitHub Users API

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.68+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Coverage](https://img.shields.io/badge/coverage-80%25-brightgreen.svg)
![GitHub last commit](https://img.shields.io/github/last-commit/lougail/github-users-api)

> API REST donnant accès à une base de données filtrée d'utilisateurs GitHub, avec fonctionnalités de recherche et d'authentification.

## 📑 Table des Matières

1. [Quick Start](#-quick-start)
2. [Installation Détaillée](#-installation-détaillée)
3. [Extraction des Données](#-extraction-des-données)
4. [Structure des Données](#-structure-des-données)
5. [Critères de Filtrage](#-critères-de-filtrage)
6. [Documentation API](#-documentation-api)
7. [Sécurité](#-sécurité)
8. [Architecture](#️-architecture)
9. [Performance](#-performance)
10. [Guide de Dépannage](#-guide-de-dépannage)
11. [Contribution](#-contribution)
12. [License](#-license)

## ⚡ Quick Start

```bash
# Cloner le projet
git clone <votre-repo>
cd github-users-api

# Installer les dépendances
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt

# Configurer l'environnement
copy .env.example .env
# Ajouter votre token GitHub dans .env

# Extraire et filtrer les données
python extract_users.py
python filtered_users.py

# Lancer l'API
uvicorn api.main:app --reload
```

## 📸 Captures d'écran

### Interface de Documentation (Swagger UI)
![Interface Swagger](docs/images/swagger-ui.png)

### Exemple de Réponse API
![Réponse API](docs/images/api-response.png)

## 💿 Installation Détaillée

### Prérequis
- Python 3.8+
- Token GitHub avec permissions `read:user`
- ~5Go d'espace disque
- Connexion Internet stable

### Configuration
1. Créer l'environnement virtuel
2. Installer les dépendances
3. Configurer le fichier `.env`

## 📥 Extraction des Données

### Étape 1 : Extraction initiale
```bash
# Configuration du token dans .env
GITHUB_TOKEN=votre_token_github

# Lancer l'extraction
python extract_users.py
```

### Étape 2 : Filtrage
```bash
python filtered_users.py
```

### Métriques d'extraction
- Batch size : 100 utilisateurs/requête
- Délai entre requêtes : 1 seconde
- Limite : 3000 utilisateurs maximum

## 📊 Structure des Données

### Format utilisateur
```json
{
    "login": "string",      // Nom d'utilisateur GitHub
    "id": "integer",        // ID unique
    "created_at": "string", // Format ISO 8601
    "avatar_url": "string", // URL de l'avatar
    "bio": "string"         // Biographie
}
```

### Stockage
- Données brutes : `data/users.json`
- Données filtrées : `data/filtered_users.json`

## 🎯 Critères de Filtrage

| Critère | Description |
|---------|-------------|
| Date de création | Comptes créés après 01/01/2000 |
| Bio | Doit être non vide |
| Avatar | Doit avoir une URL valide |
| Doublons | Suppression basée sur l'ID |

### Processus de filtrage
1. Extraction depuis l'API GitHub (`extract_users.py`)
2. Application des filtres (`filtered_users.py`)
3. Stockage dans `data/filtered_users.json`

## 📖 Documentation API

### Endpoints

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/users/` | Liste tous les utilisateurs |
| GET | `/users/{login}` | Détails d'un utilisateur |
| GET | `/users/search?q={terme}` | Recherche d'utilisateurs |

### Exemple de Réponse
```json
{
    "login": "pythondev",
    "id": 123456,
    "created_at": "2011-09-03T15:26:22Z",
    "avatar_url": "https://avatars.githubusercontent.com/u/123456?v=4",
    "bio": "Python developer and open source contributor"
}
```

## 🔒 Sécurité

### Authentification
- Type : Basic Auth
- Username : `admin`
- Password : `admin123`

### Exemple de Requête
```bash
curl -X GET "http://127.0.0.1:8000/users/" -u admin:admin123 -H "Accept: application/json"
```

## ⚙️ Architecture

```
api/
├── __init__.py
├── main.py          # FastAPI app
├── models.py        # Modèles de données
├── routes.py        # Endpoints
└── security.py      # Authentification
```

## 📊 Performance

- Extraction optimisée : 100 utilisateurs par requête
- Mise en cache des données filtrées
- Temps de réponse API < 100ms
- Gestion du rate limiting GitHub
- Délai automatique entre requêtes

## 🔧 Guide de Dépannage

### Erreurs Communes

1. **Authentification échouée**
```json
{"detail": "Authentification échouée"}
```
➡️ Solution : Vérifier les credentials (admin/admin123)

2. **Rate Limiting**
```json
{"message": "API rate limit exceeded"}
```
➡️ Solution : Attendre ou utiliser un nouveau token

## 🤝 Contribution

1. Fork le projet
2. Créer une branche (`git checkout -b feature/amelioration`)
3. Commit (`git commit -am 'Ajout fonctionnalité'`)
4. Push (`git push origin feature/amelioration`)
5. Créer une Pull Request

## 📄 License

MIT License - voir [LICENSE](LICENSE)