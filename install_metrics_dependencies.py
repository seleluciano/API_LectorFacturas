"""
Script para instalar dependencias adicionales para el sistema de métricas
"""
import subprocess
import sys
import os

def install_package(package):
    """Instala un paquete usando pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"[OK] {package} instalado correctamente")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Error instalando {package}: {e}")
        return False

def check_package(package):
    """Verifica si un paquete está instalado"""
    try:
        __import__(package)
        return True
    except ImportError:
        return False

def main():
    """Función principal de instalación"""
    print("Instalando dependencias para el sistema de metricas")
    print("=" * 60)
    
    # Dependencias adicionales para métricas
    additional_packages = [
        "statistics",  # Para cálculos estadísticos (viene con Python 3.4+)
    ]
    
    # Verificar dependencias existentes
    existing_packages = [
        "fastapi",
        "uvicorn", 
        "pydantic",
        "python-multipart",
        "pillow",
        "opencv-python",
        "pytesseract",
        "layoutparser",
        "scikit-image",
        "numpy",
        "pandas"
    ]
    
    print("Verificando dependencias existentes...")
    missing_packages = []
    
    for package in existing_packages:
        if check_package(package.replace("-", "_")):
            print(f"[OK] {package} - Ya instalado")
        else:
            print(f"[ERROR] {package} - No encontrado")
            missing_packages.append(package)
    
    # Instalar paquetes faltantes
    if missing_packages:
        print(f"\nInstalando {len(missing_packages)} paquetes faltantes...")
        for package in missing_packages:
            install_package(package)
    else:
        print("\n[OK] Todas las dependencias principales estan instaladas")
    
    # Verificar paquetes adicionales
    print("\nVerificando paquetes adicionales...")
    for package in additional_packages:
        if check_package(package):
            print(f"[OK] {package} - Disponible")
        else:
            print(f"[WARNING] {package} - No disponible (puede ser parte de Python estandar)")
    
    # Verificar que el sistema de métricas funcione
    print("\nProbando sistema de metricas...")
    try:
        from services.metrics_calculator import MetricsCalculator
        from services.batch_processor import BatchProcessor
        
        calculator = MetricsCalculator()
        batch_processor = BatchProcessor()
        
        print("[OK] Sistema de metricas importado correctamente")
        
        # Prueba básica
        test_fields = {'tipo_factura': 'A', 'razon_social_vendedor': 'Test'}
        confidence = calculator.calculate_confidence_score(test_fields)
        print(f"[OK] Prueba basica exitosa - Confidence Score: {confidence:.3f}")
        
    except Exception as e:
        print(f"[ERROR] Error probando sistema de metricas: {e}")
        return False
    
    print("\n[SUCCESS] Instalacion completada exitosamente")
    print("\nProximos pasos:")
    print("   1. Ejecuta: python test_metrics_system.py")
    print("   2. Ejecuta: python example_usage.py")
    print("   3. Coloca facturas en un directorio y ejecuta: python benchmark_model.py --test-dir <directorio>")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
