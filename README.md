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
3. [Documentation API](#-documentation-api)
4. [Sécurité](#-sécurité)
5. [Architecture](#️-architecture)
6. [Performance](#-performance)
7. [Guide de Dépannage](#-guide-de-dépannage)
8. [Contribution](#-contribution)

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