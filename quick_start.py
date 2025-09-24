#!/usr/bin/env python3
"""
Inicio rápido de la API sin Jupyter
"""

import os
import sys
import uvicorn
from pathlib import Path

def quick_start():
    """Iniciar la API directamente"""
    print("🚀 INICIO RÁPIDO - API DE PROCESAMIENTO DE IMÁGENES")
    print("=" * 60)
    
    # Configurar variables de entorno
    os.environ['HOST'] = '0.0.0.0'
    os.environ['PORT'] = '8080'
    os.environ['DEBUG'] = 'True'
    os.environ['UPLOAD_DIR'] = 'temp_uploads'
    os.environ['MAX_FILE_SIZE'] = '10485760'
    os.environ['TESSERACT_PATH'] = '/usr/bin/tesseract'
    os.environ['FAST_MODE'] = 'True'
    
    # Crear directorios
    Path("temp_uploads").mkdir(exist_ok=True)
    
    print("✅ Configuración completada")
    print("🌐 API disponible en:")
    print("   http://10.10.0.101:8080")
    print("📚 Documentación: http://10.10.0.101:8080/docs")
    print("🔍 Health Check: http://10.10.0.101:8080/health")
    print("\n🛑 Presiona Ctrl+C para detener")
    print("=" * 60)
    
    try:
        # Importar y ejecutar la API
        from main import app
        uvicorn.run(app, host="0.0.0.0", port=8080, log_level="info")
    except KeyboardInterrupt:
        print("\n\n🛑 API detenida")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    quick_start()
