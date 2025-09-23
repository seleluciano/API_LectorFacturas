#!/usr/bin/env python3
"""
Script para iniciar Jupyter Lab con la API de procesamiento de imágenes
"""

import os
import sys
import subprocess
import webbrowser
import time
from pathlib import Path

def check_jupyter_installation():
    """Verificar si Jupyter está instalado"""
    try:
        import jupyter
        print("✅ Jupyter está instalado")
        return True
    except ImportError:
        print("❌ Jupyter no está instalado")
        return False

def install_jupyter():
    """Instalar Jupyter y dependencias necesarias"""
    print("📦 Instalando Jupyter y dependencias...")
    
    packages = [
        "jupyter",
        "jupyterlab", 
        "ipywidgets",
        "requests",
        "uvicorn[standard]"
    ]
    
    for package in packages:
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", package], 
                         check=True, capture_output=True)
            print(f"✅ {package} instalado")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error instalando {package}: {e}")
            return False
    
    return True

def setup_environment():
    """Configurar variables de entorno"""
    print("🔧 Configurando entorno...")
    
    # Configurar variables de entorno
    os.environ['HOST'] = '0.0.0.0'
    os.environ['PORT'] = '8080'  # Puerto diferente para evitar conflictos
    os.environ['DEBUG'] = 'True'
    os.environ['UPLOAD_DIR'] = 'temp_uploads'
    os.environ['MAX_FILE_SIZE'] = '10485760'
    os.environ['TESSERACT_PATH'] = '/usr/bin/tesseract'
    os.environ['FAST_MODE'] = 'True'
    
    # Crear directorios necesarios
    Path("temp_uploads").mkdir(exist_ok=True)
    Path("logs").mkdir(exist_ok=True)
    
    print("✅ Entorno configurado")

def config_jupyter_remote():
    """Configurar Jupyter para acceso remoto"""
    print("🌐 Configurando Jupyter para acceso remoto...")
    
    try:
        # Generar configuración si no existe
        subprocess.run([
            sys.executable, "-m", "jupyter", "lab", "--generate-config"
        ], capture_output=True)
        
        # Obtener ruta del archivo de configuración
        home = Path.home()
        config_file = home / ".jupyter" / "jupyter_lab_config.py"
        
        # Configuración para acceso remoto
        config_content = """
# Configuración para acceso remoto
c.ServerApp.ip = '0.0.0.0'
c.ServerApp.port = 8889
c.ServerApp.open_browser = False
c.ServerApp.allow_root = True
c.ServerApp.token = ''
c.ServerApp.password = ''
c.ServerApp.disable_check_xsrf = True
"""
        
        # Escribir configuración
        with open(config_file, 'a') as f:
            f.write(config_content)
        
        print("✅ Jupyter configurado para acceso remoto")
        
    except Exception as e:
        print(f"⚠️ Error configurando Jupyter: {e}")
        print("💡 Se usará configuración por defecto")

def start_jupyter_lab():
    """Iniciar Jupyter Lab"""
    print("🚀 Iniciando Jupyter Lab...")
    
    try:
        # Configurar Jupyter para acceso remoto
        config_jupyter_remote()
        
        # Iniciar Jupyter Lab
        process = subprocess.Popen([
            sys.executable, "-m", "jupyter", "lab",
            "--ip=0.0.0.0",
            "--port=8889",
            "--no-browser",
            "--allow-root"
        ])
        
        print("✅ Jupyter Lab iniciado")
        print("🌐 Accede desde tu máquina local a:")
        print("   http://IP_DEL_SERVIDOR:8889")
        print("📝 Abre el notebook: api_jupyter.ipynb")
        print("🛑 Presiona Ctrl+C para detener")
        
        # Esperar a que el proceso termine
        process.wait()
        
    except KeyboardInterrupt:
        print("\n🛑 Deteniendo Jupyter Lab...")
        process.terminate()
    except Exception as e:
        print(f"❌ Error iniciando Jupyter Lab: {e}")

def main():
    """Función principal"""
    print("=" * 60)
    print("🚀 INICIADOR DE JUPYTER PARA API DE PROCESAMIENTO DE IMÁGENES")
    print("=" * 60)
    
    # Verificar instalación de Jupyter
    if not check_jupyter_installation():
        print("💡 Instalando Jupyter...")
        if not install_jupyter():
            print("❌ No se pudo instalar Jupyter")
            sys.exit(1)
    
    # Configurar entorno
    setup_environment()
    
    # Iniciar Jupyter Lab
    start_jupyter_lab()

if __name__ == "__main__":
    main()
