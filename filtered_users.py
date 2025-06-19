"""
Module de filtrage des données utilisateurs GitHub.

Ce module implémente le traitement et le nettoyage des données brutes
des utilisateurs GitHub, incluant la déduplication et le filtrage selon
des critères spécifiques.
"""

from typing import List, Dict, Any, ClassVar
from datetime import datetime
import json
import logging
from pathlib import Path

class FilterConfig:
    """Configuration des critères de filtrage.
    
    Cette classe centralise les paramètres utilisés pour filtrer
    les données utilisateurs.
    
    Attributes:
        MIN_DATE (str): Date minimale de création de compte
        DATE_FORMAT (str): Format pour l'analyse des dates
        REQUIRED_FIELDS (List[str]): Champs obligatoires dans les données
    """
    MIN_DATE: ClassVar[str] = "2000-01-01"
    DATE_FORMAT: ClassVar[str] = "%Y-%m-%d"
    REQUIRED_FIELDS: ClassVar[List[str]] = ["bio", "avatar_url"]

class UserFilter:
    """Gestionnaire de filtrage des données utilisateurs.
    
    Cette classe implémente une chaîne de traitement pour les données
    utilisateurs GitHub, incluant la déduplication et le filtrage selon
    des critères spécifiques.
    
    Attributes:
        input_file (Path): Chemin vers le fichier JSON source
        output_file (Path): Chemin pour sauvegarder les données filtrées
        stats (Dict[str, int]): Statistiques du processus de filtrage
        logger (logging.Logger): Instance de logger pour la classe
    """
    
    def __init__(self, input_file: str, output_file: str) -> None:
        """
        Initialise le filtre avec les chemins des fichiers.
        
        Args:
            input_file: Chemin du fichier JSON source
            output_file: Chemin du fichier de destination
        """
        self.input_file: Path = Path(input_file)
        self.output_file: Path = Path(output_file)
        self.stats: Dict[str, int] = {
            "total": 0,
            "duplicates": 0,
            "filtered": 0
        }
        self.logger: logging.Logger = logging.getLogger(__name__)

    def load_users(self) -> List[Dict[str, Any]]:
        """
        Charge les utilisateurs depuis le fichier JSON.
        
        Returns:
            Liste des dictionnaires d'utilisateurs
            
        Raises:
            FileNotFoundError: Si le fichier source n'existe pas
            json.JSONDecodeError: Si le JSON est invalide
        """
        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            self.logger.error(f"Error loading users: {e}")
            raise

    def remove_duplicates(self, users: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Supprime les utilisateurs en double basé sur leur ID.
        
        Args:
            users: Liste des utilisateurs à dédupliquer
            
        Returns:
            Liste des utilisateurs sans doublons
        """
        unique_users: Dict[int, Dict[str, Any]] = {}
        for user in users:
            unique_users[user['id']] = user
        
        self.stats["duplicates"] = len(users) - len(unique_users)
        return list(unique_users.values())

    def filter_users(self, users: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Applique les critères de filtrage aux utilisateurs.
        
        Args:
            users: Liste des utilisateurs à filtrer
            
        Returns:
            Liste des utilisateurs filtrés selon les critères
        """
        min_date = datetime.strptime(FilterConfig.MIN_DATE, FilterConfig.DATE_FORMAT)
        filtered: List[Dict[str, Any]] = []
        
        for user in users:
            if (all(user.get(field) for field in FilterConfig.REQUIRED_FIELDS) and 
                datetime.strptime(user['created_at'][:10], FilterConfig.DATE_FORMAT) >= min_date):
                filtered.append(user)
        
        self.stats["filtered"] = len(filtered)
        return filtered

    def process(self) -> None:
        """
        Exécute la chaîne complète de traitement des données.
        
        Cette méthode orchestre le processus complet de filtrage:
        1. Chargement des utilisateurs
        2. Suppression des doublons
        3. Application des filtres
        4. Sauvegarde des résultats
        5. Affichage des statistiques
        
        Raises:
            FileNotFoundError: Si les fichiers sont inaccessibles
            json.JSONDecodeError: Si le traitement JSON échoue
        """
        # Load
        users = self.load_users()
        self.stats["total"] = len(users)
        self.logger.info(f"Loaded {len(users)} users")
        
        # Process
        users = self.remove_duplicates(users)
        users = self.filter_users(users)
        
        # Save
        try:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(users, f, indent=2)
        except IOError as e:
            self.logger.error(f"Error saving filtered users: {e}")
            raise
            
        # Print stats
        print(f"\nUtilisateurs chargés : {self.stats['total']}")
        print(f"Doublons supprimés : {self.stats['duplicates']}")
        print(f"Utilisateurs filtrés : {self.stats['filtered']}")

if __name__ == "__main__":
    # Configuration des chemins de fichiers
    input_file = "data/users.json"
    output_file = "data/filtered_users.json"
    
    try:
        # Création et exécution du filtre
        filter = UserFilter(input_file, output_file)
        filter.process()
        print("Filtrage terminé avec succès!")
    except Exception as e:
        print(f"Une erreur est survenue: {e}")