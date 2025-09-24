#!/usr/bin/env python3
"""
Script para iniciar el servidor de desarrollo
"""

import uvicorn
import os
import sys
import logging

# Añadir el directorio actual al PATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from main import app

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Función principal para iniciar el servidor"""
    
    # Configuración del servidor
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8080))
    debug = os.getenv("DEBUG", "False").lower() == "true"
    log_level = os.getenv("LOG_LEVEL", "info").lower()
    workers = int(os.getenv("WORKERS", 1))
    
    logger.info("Iniciando servidor de desarrollo...")
    logger.info(f"   Host: {host}")
    logger.info(f"   Puerto: {port}")
    logger.info(f"   Debug: {debug}")
    logger.info(f"   Documentacion: http://{host}:{port}/docs")
    logger.info("=" * 50)
    
    try:
        # Configurar Uvicorn
        config = uvicorn.Config(
            "main:app",
            host=host,
            port=port,
            reload=debug,
            log_level=log_level,
            workers=workers if not debug else 1
        )
        
        server = uvicorn.Server(config)
        server.run()
        
    except Exception as e:
        logger.error(f"Error iniciando servidor: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("🛑 Servidor detenido por el usuario")
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        sys.exit(1)
