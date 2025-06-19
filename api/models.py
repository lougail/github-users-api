"""
Module définissant les modèles de données pour l'API GitHub Users.

Ce module contient les classes de configuration et les modèles Pydantic
pour la validation et la sérialisation des données utilisateur GitHub.
"""

from datetime import datetime
from pydantic import BaseModel, HttpUrl, Field, validator
from typing import Optional, Dict, Any, ClassVar, Type, Union

class UserConfig:
    """Classe de configuration pour les valeurs par défaut et contraintes du modèle User.
    
    Cette classe centralise toutes les valeurs de configuration utilisées dans le modèle User.
    
    Attributes :
        MIN_LOGIN_LENGTH (int): Longueur minimale du login utilisateur
        MIN_ID_VALUE (int): Valeur minimale autorisée pour l'ID
        DEFAULT_SCHEMA_TITLE (str): Titre par défaut du schéma OpenAPI
        DEFAULT_SCHEMA_DESC (str): Description par défaut du schéma OpenAPI
        EXAMPLE_USER (Dict[str, Any]): Exemple d'utilisateur pour la documentation
    """
    MIN_LOGIN_LENGTH: ClassVar[int] = 1
    MIN_ID_VALUE: ClassVar[int] = 0
    DEFAULT_SCHEMA_TITLE: ClassVar[str] = "GitHub User"
    DEFAULT_SCHEMA_DESC: ClassVar[str] = "A GitHub user with basic profile information"
    
    EXAMPLE_USER: ClassVar[Dict[str, Any]] = {
        "login": "mojombo",
        "id": 1,
        "created_at": "2007-10-20T05:24:19Z",
        "avatar_url": "https://avatars.githubusercontent.com/u/1?v=4",
        "bio": "GitHub co-founder"
    }

class User(BaseModel):
    """Représentation du modèle utilisateur GitHub.

    Cette classe implémente le modèle de données pour les utilisateurs GitHub avec validation
    et sérialisation via Pydantic.

    Attributes :
        login (str): Nom d'utilisateur GitHub
        id (int): Identifiant unique de l'utilisateur
        created_at (datetime): Date de création du compte
        avatar_url (HttpUrl): URL de l'avatar de l'utilisateur
        bio (Optional[str]): Biographie de l'utilisateur
    """
    login: str = Field(
        ...,
        description="The user's GitHub login",
        min_length=UserConfig.MIN_LOGIN_LENGTH,
        example=UserConfig.EXAMPLE_USER["login"]
    )
    
    id: int = Field(
        ...,
        description="The user's unique identifier",
        gt=UserConfig.MIN_ID_VALUE,
        example=UserConfig.EXAMPLE_USER["id"]
    )
    
    created_at: datetime = Field(
        ...,
        description="Account creation timestamp",
        example=UserConfig.EXAMPLE_USER["created_at"]
    )
    
    avatar_url: HttpUrl = Field(
        ...,
        description="URL to user's avatar image",
        example=UserConfig.EXAMPLE_USER["avatar_url"]
    )
    
    bio: Optional[str] = Field(
        None,
        description="User's biography",
        example=UserConfig.EXAMPLE_USER["bio"]
    )

    @validator('created_at', pre=True)
    def parse_datetime(cls, value: Union[str, datetime]) -> datetime:
        """Analyse la date depuis une chaîne si nécessaire.

        Args:
            value (Union[str, datetime]): Date à parser ou datetime existante

        Returns:
            datetime: Date parsée avec fuseau horaire
        """
        if isinstance(value, str):
            return datetime.fromisoformat(value.replace('Z', '+00:00'))
        return value

    @validator('created_at')
    def validate_created_at(cls: Type['User'], v: datetime) -> datetime:
        """Valide que la date de création n'est pas dans le futur.
        
        Args:
            v (datetime): Date à valider
            
        Returns:
            datetime: Date validée
            
        Raises:
            ValueError: Si la date est dans le futur
        """
        now = datetime.now(v.tzinfo)
        if v > now:
            raise ValueError("Creation date cannot be in the future")
        return v

    class Config:
        """Configuration du modèle Pydantic.

        Configure la sérialisation et la documentation du modèle.
        """
        json_schema_extra = {
            "example": UserConfig.EXAMPLE_USER
        }
        
        schema_extra = {
            "title": UserConfig.DEFAULT_SCHEMA_TITLE,
            "description": UserConfig.DEFAULT_SCHEMA_DESC
        }
        
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        arbitrary_types_allowed = True