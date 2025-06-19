"""
Module de sécurité pour l'API GitHub Users.

Ce module gère l'authentification Basic Auth et la validation des credentials.
Il fournit une interface cohérente pour la sécurisation des endpoints de l'API.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import Dict, Optional, Type, ClassVar, NoReturn
import os
from dotenv import load_dotenv
import logging
import secrets

class SecurityConfig:
    """Configuration settings for security features.
    
    Cette classe centralise toutes les constantes de configuration
    liées à la sécurité de l'API.
    
    Attributes:
        DEFAULT_USER (str): Nom d'utilisateur par défaut si non défini dans .env
        DEFAULT_PASS (str): Mot de passe par défaut si non défini dans .env
        AUTH_SCHEME (str): Nom du schéma d'authentification
        AUTH_DESC (str): Description de la méthode d'authentification
    """
    DEFAULT_USER: ClassVar[str] = "admin"
    DEFAULT_PASS: ClassVar[str] = "admin123"
    AUTH_SCHEME: ClassVar[str] = "Basic Auth"
    AUTH_DESC: ClassVar[str] = "Authentification basique avec nom d'utilisateur et mot de passe"

class AuthenticationManager:
    """Gère la logique d'authentification et la gestion des utilisateurs.
    
    Cette classe centralise toutes les opérations liées à l'authentification.
    """
    
    def __init__(self) -> None:
        """Initialise le gestionnaire d'authentification."""
        self.logger: logging.Logger = logging.getLogger(__name__)
        self._load_environment()
        self.security = HTTPBasic(
            scheme_name=SecurityConfig.AUTH_SCHEME,
            description=SecurityConfig.AUTH_DESC
        )
        
    def _load_environment(self) -> None:
        """Charge les variables d'environnement pour l'authentification."""
        load_dotenv()
        self.valid_users: Dict[str, str] = {
            os.getenv("BASIC_AUTH_USER", SecurityConfig.DEFAULT_USER): 
            os.getenv("BASIC_AUTH_PASS", SecurityConfig.DEFAULT_PASS)
        }
        
    def authenticate(self, credentials: HTTPBasicCredentials) -> str:
        """
        Authentifie l'utilisateur avec les identifiants fournis.

        Args:
            credentials (HTTPBasicCredentials): Identifiants de l'utilisateur

        Returns:
            str: Nom d'utilisateur si l'authentification réussit

        Raises:
            HTTPException: Si l'authentification échoue
        """
        try:
            is_valid = secrets.compare_digest(
                self.valid_users.get(credentials.username, ""),
                credentials.password
            )
            
            if not is_valid:
                self.logger.warning(f"Tentative d'authentification échouée pour l'utilisateur: {credentials.username}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Identifiants invalides",
                    headers={"WWW-Authenticate": "Basic"},
                )
                
            self.logger.info(f"Authentification réussie pour l'utilisateur: {credentials.username}")
            return credentials.username
            
        except Exception as e:
            self.logger.error(f"Erreur d'authentification: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentification échouée",
                headers={"WWW-Authenticate": "Basic"},
            )

# Create singleton instance
auth_manager = AuthenticationManager()

async def get_current_user(
    credentials: HTTPBasicCredentials = Depends(auth_manager.security)
) -> str:
    """
    Récupère l'utilisateur actuellement authentifié.
    
    Args:
        credentials (HTTPBasicCredentials): Identifiants de l'utilisateur depuis la requête
        
    Returns:
        str: Nom d'utilisateur authentifié
    """
    return auth_manager.authenticate(credentials)

# Exports
__all__ = ['auth_manager', 'get_current_user']