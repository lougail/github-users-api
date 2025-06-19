"""
Module de routage pour l'API GitHub Users.

Ce module gère les routes de l'API, le repository de données,
et la logique métier pour l'accès aux utilisateurs GitHub.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Dict, Any, Optional
from pathlib import Path
import json
import logging
from datetime import datetime, timezone
from .models import User
from .security import get_current_user

class RouterConfig:
    """Configuration pour les endpoints du router.
    
    Attributes:
        SEARCH_MIN_LENGTH (int): Longueur minimale pour les termes de recherche
        DEFAULT_LIMIT (int): Limite par défaut pour les résultats paginés
    """
    SEARCH_MIN_LENGTH: int = 3
    DEFAULT_LIMIT: int = 10

class UserRepository:
    """Repository pour la gestion des données utilisateur.
    
    Cette classe gère le chargement, la transformation et la recherche
    des données utilisateur stockées au format JSON.
    
    Attributes:
        filepath (Path): Chemin vers le fichier JSON des utilisateurs
    """
    
    def __init__(self) -> None:
        """Initialise le repository avec le chemin du fichier de données."""
        self.filepath: Path = Path("data/filtered_users.json")

    def _transform_dates(self, users: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transforme les dates string en objets datetime.
        
        Args:
            users: Liste des utilisateurs avec dates au format string
            
        Returns:
            Liste des utilisateurs avec dates au format datetime
        """
        for user in users:
            created_at = user['created_at']
            if isinstance(created_at, str):
                if created_at.endswith('Z'):
                    created_at = created_at[:-1]
                dt = datetime.fromisoformat(created_at)
                user['created_at'] = dt.replace(tzinfo=timezone.utc)
        return users

    def load_all(self) -> List[Dict[str, Any]]:
        """Charge tous les utilisateurs depuis le fichier JSON.
        
        Returns:
            Liste de tous les utilisateurs avec dates transformées
            
        Raises:
            IOError: Si le fichier ne peut pas être lu
            json.JSONDecodeError: Si le JSON est invalide
        """
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                users = json.load(f)
                return self._transform_dates(users)
        except (IOError, json.JSONDecodeError) as e:
            logger.error(f"Error loading users: {e}")
            return []

    def search(self, query: str) -> List[Dict[str, Any]]:
        """Recherche des utilisateurs par terme.
        
        Args:
            query: Terme de recherche
            
        Returns:
            Liste des utilisateurs correspondant au terme
        """
        users = self.load_all()
        query_lower = query.lower()
        return [
            user for user in users
            if query_lower in user.get("login", "").lower() or
            (user.get("bio") and query_lower in user.get("bio", "").lower())
        ]

    def get_user_by_login(self, login: str) -> Optional[Dict[str, Any]]:
        """Récupère un utilisateur par son login.
        
        Args:
            login: Login GitHub de l'utilisateur
            
        Returns:
            Données de l'utilisateur ou None si non trouvé
        """
        users = self.load_all()
        return next((user for user in users if user["login"] == login), None)

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create router and repository instances
router = APIRouter()
user_repository = UserRepository()

@router.get(
    "/",
    response_model=List[User],
    summary="Récupérer tous les utilisateurs",
    response_description="Liste de tous les utilisateurs GitHub",
    tags=["users"]
)
async def get_users(
    current_user: str = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """
    ## Description
    Retourne la liste complète des utilisateurs GitHub présents dans la base de données.

    ## Paramètres
    - **current_user** (*str*, dépendance) : Utilisateur authentifié (injecté automatiquement).

    ## Exemples
    **Requête :**
    ```
    GET /users/
    ```
    **Réponse :**
    ```json
    [
        {
            "login": "defunkt",
            "id": 1,
            "created_at": "2011-01-25T18:44:36Z",
            "avatar_url": "https://github.com/images/error/defunkt_happy.gif",
            "bio": "I am the defunkt"
        }
    ]
    ```

    ## Codes d'erreur
    - **401 Unauthorized** : Authentification requise ou échouée.
    - **500 Internal Server Error** : Erreur interne du serveur.
    """
    return user_repository.load_all()

@router.get(
    "/search",
    response_model=List[User],
    summary="Rechercher des utilisateurs",
    response_description="Liste des utilisateurs correspondant à la recherche",
    tags=["users"]
)
async def search_users(
    q: str = Query(..., description="Terme de recherche", min_length=RouterConfig.SEARCH_MIN_LENGTH),
    current_user: str = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """
    ## Description
    Recherche des utilisateurs dont le login ou la biographie contient le terme spécifié.

    ## Paramètres
    - **q** (*str*, requis) : Terme de recherche (au moins {RouterConfig.SEARCH_MIN_LENGTH} caractères).
    - **current_user** (*str*, dépendance) : Utilisateur authentifié (injecté automatiquement).

    ## Exemples
    **Requête :**
    ```
    GET /users/search?q=defunkt
    ```
    **Réponse :**
    ```json
    [
        {
            "id": 1,
            "login": "defunkt",
            "bio": "Mascotte de GitHub"
        }
    ]
    ```

    ## Codes d'erreur
    - **400 Bad Request** : Terme de recherche trop court.
    - **401 Unauthorized** : Authentification requise ou échouée.
    - **500 Internal Server Error** : Erreur interne du serveur.
    """
    _ = current_user
    logger.debug(f"Starting search with query: '{q}'")
    try:
        matches = user_repository.search(q)
        logger.info(f"Found {len(matches)} matches for query: '{q}'")
        return matches
    except Exception as e:
        logger.error(f"Search error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get(
    "/{login}",
    response_model=User,
    summary="Récupérer un utilisateur par login",
    response_description="Détails d'un utilisateur",
    tags=["users"]
)
async def get_user_by_login(
    login: str,
    current_user: str = Depends(get_current_user)
) -> User:
    """
    ## Description
    Récupère les informations détaillées d'un utilisateur spécifique à partir de son login GitHub.

    ## Paramètres
    - **login** (*str*, path) : Login de l'utilisateur à rechercher.
    - **current_user** (*str*, dépendance) : Utilisateur authentifié (injecté automatiquement).

    ## Exemples
    **Requête :**
    ```
    GET /users/defunkt
    ```
    **Réponse (succès) :**
    ```json
    {
        "login": "defunkt",
        "id": 1,
        "created_at": "2011-01-25T18:44:36Z",
        "avatar_url": "https://github.com/images/error/defunkt_happy.gif",
        "bio": "I am the defunkt"
    }
    ```
    **Réponse (erreur) :**
    ```json
    {
        "detail": "User defunkt not found"
    }
    ```

    ## Codes d'erreur
    - **401 Unauthorized** : Authentification requise ou échouée.
    - **404 Not Found** : Aucun utilisateur trouvé avec ce login.
    - **500 Internal Server Error** : Erreur interne du serveur.
    """
    user = user_repository.get_user_by_login(login)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {login} not found"
        )
    return User(**user)