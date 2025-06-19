"""
Point d'entrée principal de l'API GitHub Users.

Ce module configure l'application FastAPI, met en place le middleware CORS,
et définit les routes principales de l'API.
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from .routes import router
import logging
from typing import Dict, Optional, Type, List, Any

class APIConfig:
    """Configuration pour l'API et la documentation Swagger/OpenAPI.
    
    Attributes:
        TITLE (str): Titre de l'API affiché dans la documentation
        DESCRIPTION (str): Description de l'API
        VERSION (str): Version actuelle de l'API
        TAGS_METADATA (List[Dict[str, str]]): Métadonnées pour la documentation OpenAPI
    """
    TITLE: str = "GitHub Users API"
    DESCRIPTION: str = "API for accessing filtered GitHub user data"
    VERSION: str = "1.0.0"
    TAGS_METADATA: List[Dict[str, str]] = [
        {
            "name": "users",
            "description": "Operations with GitHub users"
        },
        {
            "name": "health",
            "description": "API health check"
        }
    ]

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger: logging.Logger = logging.getLogger(__name__)

# Create FastAPI instance with simplified OpenAPI config
app: FastAPI = FastAPI(
    title=APIConfig.TITLE,
    description=APIConfig.DESCRIPTION,
    version=APIConfig.VERSION,
    openapi_url="/api/v1/openapi.json",
    docs_url="/docs"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include router
app.include_router(
    router,
    prefix="/users",
    tags=["users"]
)

@app.get("/", tags=["health"])
async def root() -> Dict[str, str]:
    """
    Endpoint de vérification de l'état de l'API.
    
    Returns:
        Dict[str, str]: Dictionnaire contenant le statut et la version de l'API
        
    Example:
        >>> GET /
        >>> {"status": "healthy", "version": "1.0.0"}
    """
    return {"status": "healthy", "version": APIConfig.VERSION}