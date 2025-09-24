"""
Configuración para la integración con API externa de facturas
"""
import os
from typing import Dict, Any

# Configuración de API externa
EXTERNAL_API_CONFIG = {
    "base_url": "http://127.0.0.1:8000",
    "endpoint": "/api/gestion/facturas/cargar-imagenes/",
    "timeout": 30,
    "retry_attempts": 3,
    "retry_delay": 1.0,
    "headers": {
        "Content-Type": "application/json",
        "User-Agent": "FacturaProcessor/1.0"
    }
}

# Configuración de autenticación
API_KEY = os.getenv("FACTURAS_API_KEY", "")

# Si hay API key, agregar a headers
if API_KEY:
    EXTERNAL_API_CONFIG["headers"]["Authorization"] = f"Bearer {API_KEY}"

# Configuración de logging
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
}

# Configuración de procesamiento de imágenes
IMAGE_PROCESSING_CONFIG = {
    "max_file_size": 10 * 1024 * 1024,  # 10MB
    "allowed_formats": ["image/jpeg", "image/png", "image/tiff", "application/pdf"],
    "ocr_language": "spa+eng",  # Español + Inglés
    "confidence_threshold": 0.7
}

# Configuración de respuesta
RESPONSE_CONFIG = {
    "include_metadata": True,
    "include_confidence_scores": True,
    "include_processing_time": True,
    "include_ocr_text": True
}

def get_config() -> Dict[str, Any]:
    """
    Obtener configuración completa
    
    Returns:
        Diccionario con toda la configuración
    """
    return {
        "external_api": EXTERNAL_API_CONFIG,
        "logging": LOGGING_CONFIG,
        "image_processing": IMAGE_PROCESSING_CONFIG,
        "response": RESPONSE_CONFIG
    }

def update_external_api_url(nueva_url: str):
    """
    Actualizar URL de la API externa
    
    Args:
        nueva_url: Nueva URL base de la API
    """
    global EXTERNAL_API_CONFIG
    EXTERNAL_API_CONFIG["base_url"] = nueva_url

def set_api_key(api_key: str):
    """
    Configurar API key para autenticación
    
    Args:
        api_key: API key para autenticación
    """
    global API_KEY, EXTERNAL_API_CONFIG
    API_KEY = api_key
    if api_key:
        EXTERNAL_API_CONFIG["headers"]["Authorization"] = f"Bearer {api_key}"
    else:
        EXTERNAL_API_CONFIG["headers"].pop("Authorization", None)
