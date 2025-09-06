"""
Script para instalar las dependencias necesarias para scikit-image
"""
import subprocess
import sys
import os

def install_package(package):
    """Instalar un paquete usando pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ {package} instalado correctamente")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error instalando {package}: {e}")
        return False

def main():
    """Instalar todas las dependencias"""
    print("🚀 Instalando dependencias para scikit-image...")
    print("=" * 50)
    
    # Dependencias principales
    packages = [
        "scikit-image==0.24.0",
        "scipy==1.16.1",
        "numpy==2.2.6",
        "Pillow==11.3.0"
    ]
    
    # Dependencias opcionales para mejor rendimiento
    optional_packages = [
        "opencv-python-headless",  # Versión sin GUI para mejor rendimiento
        "imageio",  # Para más formatos de imagen
        "matplotlib"  # Para visualización (opcional)
    ]
    
    print("📦 Instalando dependencias principales...")
    success_count = 0
    for package in packages:
        if install_package(package):
            success_count += 1
    
    print(f"\n📊 Resultado: {success_count}/{len(packages)} paquetes instalados")
    
    if success_count == len(packages):
        print("\n✅ Todas las dependencias principales instaladas correctamente")
        
        # Preguntar sobre dependencias opcionales
        print("\n🔧 Dependencias opcionales disponibles:")
        for package in optional_packages:
            print(f"   - {package}")
        
        response = input("\n¿Instalar dependencias opcionales? (y/n): ").lower().strip()
        if response in ['y', 'yes', 'sí', 'si']:
            print("\n📦 Instalando dependencias opcionales...")
            for package in optional_packages:
                install_package(package)
    else:
        print("\n❌ Algunas dependencias no se pudieron instalar")
        print("   Verifica tu conexión a internet y permisos de instalación")
    
    print("\n🎯 Próximos pasos:")
    print("   1. Ejecuta: python start_server.py")
    print("   2. Visita: http://localhost:8000/docs")
    print("   3. Prueba la API con una imagen o PDF")

if __name__ == "__main__":
    main()
