#!/usr/bin/env python3
"""
Configuración simple para el servidor
"""

import os
import sys
from pathlib import Path

def setup_server():
    """Configurar el servidor para producción"""
    
    print("🔧 Configurando servidor...")
    
    # Crear directorios necesarios
    directories = [
        "temp_uploads",
        "logs",
        "ssl"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Directorio creado: {directory}")
    
    # Configurar variables de entorno
    env_vars = {
        'HOST': '0.0.0.0',
        'PORT': '8080',
        'DEBUG': 'False',
        'UPLOAD_DIR': 'temp_uploads',
        'MAX_FILE_SIZE': '10485760',
        'TESSERACT_PATH': '/usr/bin/tesseract',
        'FAST_MODE': 'True',
        'LOG_LEVEL': 'info'
    }
    
    # Crear archivo .env
    with open('.env', 'w') as f:
        f.write("# Configuración del servidor\n")
        for key, value in env_vars.items():
            f.write(f"{key}={value}\n")
    
    print("✅ Archivo .env creado")
    
    # Verificar dependencias
    try:
        import fastapi
        import uvicorn
        import jupyter
        print("✅ Dependencias principales OK")
    except ImportError as e:
        print(f"❌ Dependencia faltante: {e}")
        return False
    
    # Verificar Tesseract
    try:
        import subprocess
        result = subprocess.run(['tesseract', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Tesseract OK")
        else:
            print("⚠️ Tesseract no encontrado")
    except Exception as e:
        print(f"⚠️ Error verificando Tesseract: {e}")
    
    print("\n🚀 Servidor configurado correctamente!")
    print("💡 Para iniciar:")
    print("   - Jupyter: python start_jupyter.py")
    print("   - API directa: python start_server.py")
    
    return True

if __name__ == "__main__":
    setup_server()
