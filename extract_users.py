"""
Module d'extraction des données utilisateurs depuis l'API GitHub.

Ce module fournit les outils nécessaires pour extraire, transformer
et sauvegarder les données des utilisateurs GitHub via leur API REST.
"""

from typing import Dict, List, Optional, Tuple, ClassVar, Any
from datetime import datetime
import requests
import json
import os
import logging
from dotenv import load_dotenv
from time import sleep
from pathlib import Path

class GitHubConfig:
    """Configuration pour l'interaction avec l'API GitHub.

    Cette classe centralise les paramètres de configuration pour
    l'interaction avec l'API GitHub.

    Attributes:
        BASE_URL (str): URL de base de l'API GitHub pour les utilisateurs
        API_VERSION (str): Version de l'API GitHub utilisée
        DEFAULT_MAX_USERS (int): Nombre maximum d'utilisateurs par défaut
        BATCH_SIZE (int): Taille du lot d'utilisateurs à extraire par requête
        RATE_LIMIT_THRESHOLD (int): Seuil de la limite de taux avant pause
    """
    BASE_URL: ClassVar[str] = "https://api.github.com/users"
    API_VERSION: ClassVar[str] = "application/vnd.github.v3+json"
    DEFAULT_MAX_USERS: ClassVar[int] = 3000
    BATCH_SIZE: ClassVar[int] = 100
    RATE_LIMIT_THRESHOLD: ClassVar[int] = 10

class GitHubUserExtractor:
    """Extracteur de données utilisateurs GitHub.
    
    Cette classe gère l'extraction et la sauvegarde des données
    utilisateurs via l'API GitHub.
    
    Attributes:
        token (str): Token d'authentification GitHub
        headers (Dict[str, str]): En-têtes HTTP pour les requêtes
        logger (logging.Logger): Logger pour la classe
    """
    
    def __init__(self) -> None:
        """Initialise l'extracteur avec la configuration nécessaire."""
        load_dotenv()
        self.token: str = os.getenv("GITHUB_TOKEN", "")
        self.headers: Dict[str, str] = {
            "Accept": GitHubConfig.API_VERSION,
            "Authorization": f"token {self.token}"
        }
        self.logger: logging.Logger = logging.getLogger(__name__)

    def extract_users(self, max_users: int = GitHubConfig.DEFAULT_MAX_USERS) -> List[Dict[str, Any]]:
        """Extrait les données de plusieurs utilisateurs GitHub.
        
        Args:
            max_users: Nombre maximum d'utilisateurs à extraire
            
        Returns:
            Liste des informations utilisateurs extraites
            
        Raises:
            requests.RequestException: Si erreur lors des requêtes API
        """
        users: List[Dict[str, Any]] = []
        since_id: int = 0
        
        print(f"Démarrage de l'extraction de {max_users} utilisateurs...")
        
        while len(users) < max_users:
            try:
                print(f"Requête API pour {GitHubConfig.BATCH_SIZE} utilisateurs depuis ID {since_id}")
                response = requests.get(
                    f"{GitHubConfig.BASE_URL}?since={since_id}&per_page={GitHubConfig.BATCH_SIZE}",
                    headers=self.headers
                )
                response.raise_for_status()
                
                batch = response.json()
                if not batch:
                    break
                    
                users_batch, since_id = self._process_batch(batch, users, max_users)
                users.extend(users_batch)
                
                if len(users) % GitHubConfig.BATCH_SIZE == 0:
                    print(f"Progression: {len(users)}/{max_users} utilisateurs extraits")
                    
                self._handle_rate_limiting(response)
                sleep(1)
                
            except requests.RequestException as e:
                self.logger.error(f"Erreur durant l'extraction: {e}")
                break
        
        print(f"Extraction terminée. {len(users)} utilisateurs extraits.")
        return users[:max_users]

    def _process_batch(
        self, 
        batch: List[Dict[str, Any]], 
        users: List[Dict[str, Any]], 
        max_users: int
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Traite un lot d'utilisateurs et récupère leurs détails.
        
        Args:
            batch: Lot brut d'utilisateurs depuis l'API
            users: Liste actuelle des utilisateurs traités
            max_users: Nombre maximum d'utilisateurs à traiter
            
        Returns:
            Tuple contenant la liste mise à jour et le dernier ID
        """
        users_batch: List[Dict[str, Any]] = []
        
        for user in batch:
            if len(users) + len(users_batch) >= max_users:
                break
                
            detailed_user = self.get_single_user(user["login"])
            if detailed_user:
                user_data = {
                    "login": detailed_user["login"],
                    "id": detailed_user["id"],
                    "created_at": detailed_user["created_at"],
                    "avatar_url": detailed_user["avatar_url"],
                    "bio": detailed_user.get("bio")
                }
                users_batch.append(user_data)
        
        since_id = batch[-1]["id"] if batch else 0
        return users_batch, since_id

    def get_single_user(self, login: str) -> Optional[Dict[str, Any]]:
        """Récupère les informations détaillées d'un utilisateur.
        
        Args:
            login: Nom d'utilisateur GitHub
            
        Returns:
            Données détaillées de l'utilisateur ou None si erreur
        """
        try:
            response = requests.get(
                f"{GitHubConfig.BASE_URL}/{login}",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            self.logger.error(f"Erreur lors de la récupération de l'utilisateur {login}: {e}")
            return None

    def _handle_rate_limiting(self, response: requests.Response) -> None:
        """Gère les limites de taux de l'API GitHub.
        
        Args:
            response: Réponse de l'API à analyser
        """
        remaining = int(response.headers.get('X-RateLimit-Remaining', 0))
        reset_time = int(response.headers.get('X-RateLimit-Reset', 0))
        
        if remaining < 10:
            wait_time = max(reset_time - datetime.now().timestamp(), 0)
            print(f"Limite de taux proche, attente de {wait_time:.0f} secondes...")
            sleep(wait_time)

    def save_users(self, users: List[Dict[str, Any]], filepath: str) -> None:
        """Sauvegarde les données utilisateurs dans un fichier JSON.
        
        Args:
            users: Liste des utilisateurs à sauvegarder
            filepath: Chemin du fichier de destination
        """
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(users, f, indent=2, ensure_ascii=False)
        print(f"Données sauvegardées dans {filepath}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    extractor = GitHubUserExtractor()
    users = extractor.extract_users(max_users=GitHubConfig.DEFAULT_MAX_USERS)
    extractor.save_users(users, "data/users.json")