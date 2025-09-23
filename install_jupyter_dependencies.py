#!/usr/bin/env python3
"""
Script para instalar dependencias necesarias para Jupyter
"""

import subprocess
import sys
import os

def install_package(package):
    """Instalar un paquete usando pip"""
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", package], 
                      check=True, capture_output=True)
        print(f"✅ {package} instalado correctamente")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error instalando {package}: {e}")
        return False

def main():
    """Instalar todas las dependencias necesarias"""
    print("📦 Instalando dependencias para Jupyter...")
    
    # Dependencias principales
    packages = [
        "jupyter",
        "jupyterlab",
        "ipywidgets",
        "requests",
        "uvicorn[standard]",
        "fastapi",
        "python-multipart",
        "layoutparser",
        "pytesseract",
        "Pillow",
        "numpy",
        "pandas",
        "python-dotenv",
        "pdf2image",
        "scikit-image",
        "scipy"
    ]
    
    # Dependencias opcionales para mejor experiencia
    optional_packages = [
        "matplotlib",
        "seaborn",
        "plotly",
        "ipython",
        "notebook"
    ]
    
    print("🔧 Instalando dependencias principales...")
    for package in packages:
        install_package(package)
    
    print("\n🎨 Instalando dependencias opcionales...")
    for package in optional_packages:
        install_package(package)
    
    print("\n✅ Instalación completada!")
    print("🚀 Ahora puedes ejecutar: python start_jupyter.py")

if __name__ == "__main__":
    main()
