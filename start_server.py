"""
Script para iniciar el servidor de desarrollo
"""
import uvicorn
import sys
import os
from pathlib import Path

# Agregar el directorio actual al path para importaciones
sys.path.append(str(Path(__file__).parent))

from config import settings

def main():
    """Iniciar el servidor de desarrollo"""
    print("Iniciando servidor de desarrollo...")
    print(f"   Host: {settings.HOST}")
    print(f"   Puerto: {settings.PORT}")
    print(f"   Debug: {settings.DEBUG}")
    print(f"   Documentacion: http://{settings.HOST}:{settings.PORT}/docs")
    print("\n" + "="*50)
    
    try:
        uvicorn.run(
            "main:app",
            host=settings.HOST,
            port=settings.PORT,
            reload=settings.DEBUG,
            log_level="info",
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n\nServidor detenido por el usuario")
    except Exception as e:
        print(f"\nError iniciando servidor: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
