"""
Script de prueba para la API de procesamiento de imágenes
"""
import requests
import json
import os
from pathlib import Path

# Configuración
API_BASE_URL = "http://localhost:8000"
TEST_IMAGE_PATH = "test_image.jpg"  # Cambiar por la ruta de una imagen de prueba
TEST_PDF_PATH = "test_document.pdf"  # Cambiar por la ruta de un PDF de prueba

def test_health_endpoint():
    """Probar el endpoint de salud"""
    print("Probando endpoint de salud...")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            print("OK - Endpoint de salud funcionando correctamente")
            print(f"   Respuesta: {response.json()}")
        else:
            print(f"ERROR - Error en endpoint de salud: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("ERROR - No se puede conectar a la API. Esta ejecutandose?")
        return False
    except Exception as e:
        print(f"ERROR - Error inesperado: {str(e)}")
        return False
    return True

def test_root_endpoint():
    """Probar el endpoint raíz"""
    print("\nProbando endpoint raiz...")
    try:
        response = requests.get(f"{API_BASE_URL}/")
        if response.status_code == 200:
            print("OK - Endpoint raiz funcionando correctamente")
            print(f"   Respuesta: {response.json()}")
        else:
            print(f"ERROR - Error en endpoint raiz: {response.status_code}")
    except Exception as e:
        print(f"ERROR - Error inesperado: {str(e)}")
    return True

def test_process_image_endpoint():
    """Probar el endpoint de procesamiento de imágenes"""
    print("\n Probando endpoint de procesamiento de imágenes...")
    
    # Verificar si existe una imagen de prueba
    if not os.path.exists(TEST_IMAGE_PATH):
        print(f"WARNING  No se encontró imagen de prueba en: {TEST_IMAGE_PATH}")
        print("   Crea una imagen de prueba o cambia TEST_IMAGE_PATH en el script")
        return False
    
    try:
        with open(TEST_IMAGE_PATH, 'rb') as f:
            files = {'file': (TEST_IMAGE_PATH, f, 'image/jpeg')}
            response = requests.post(f"{API_BASE_URL}/process-image", files=files)
        
        if response.status_code == 200:
            print("OK Endpoint de procesamiento funcionando correctamente")
            result = response.json()
            print(f"   Archivo procesado: {result.get('filename', 'N/A')}")
            print(f"   Tiempo de procesamiento: {result.get('processing_time', 'N/A')}s")
            print(f"   Estado: {result.get('status', 'N/A')}")
            print(f"   Bloques de texto: {len(result.get('text_blocks', []))}")
            print(f"   Tablas: {len(result.get('tables', []))}")
            print(f"   Figuras: {len(result.get('figures', []))}")
        else:
            print(f"ERROR Error en endpoint de procesamiento: {response.status_code}")
            print(f"   Respuesta: {response.text}")
    except Exception as e:
        print(f"ERROR Error inesperado: {str(e)}")
    return True

def test_process_pdf_endpoint():
    """Probar el endpoint de procesamiento de PDFs"""
    print("\n Probando endpoint de procesamiento de PDFs...")
    
    # Verificar si existe un PDF de prueba
    if not os.path.exists(TEST_PDF_PATH):
        print(f"WARNING  No se encontró PDF de prueba en: {TEST_PDF_PATH}")
        print("   Crea un PDF de prueba o cambia TEST_PDF_PATH en el script")
        return False
    
    try:
        with open(TEST_PDF_PATH, 'rb') as f:
            files = {'file': (TEST_PDF_PATH, f, 'application/pdf')}
            response = requests.post(f"{API_BASE_URL}/process-image", files=files)
        
        if response.status_code == 200:
            print("OK Endpoint de procesamiento de PDF funcionando correctamente")
            result = response.json()
            print(f"   Archivo procesado: {result.get('filename', 'N/A')}")
            print(f"   Tiempo de procesamiento: {result.get('processing_time', 'N/A')}s")
            print(f"   Estado: {result.get('status', 'N/A')}")
            print(f"   Es PDF: {result.get('metadata', {}).get('is_pdf', False)}")
            print(f"   Bloques de texto: {len(result.get('text_blocks', []))}")
            print(f"   Tablas: {len(result.get('tables', []))}")
            print(f"   Figuras: {len(result.get('figures', []))}")
        else:
            print(f"ERROR Error en endpoint de procesamiento de PDF: {response.status_code}")
            print(f"   Respuesta: {response.text}")
    except Exception as e:
        print(f"ERROR Error inesperado: {str(e)}")
    return True

def test_invalid_file():
    """Probar con un archivo inválido"""
    print("\n Probando con archivo inválido...")
    try:
        # Crear un archivo de texto temporal
        with open("test.txt", "w") as f:
            f.write("Este es un archivo de texto, no una imagen")
        
        with open("test.txt", 'rb') as f:
            files = {'file': ("test.txt", f, 'text/plain')}
            response = requests.post(f"{API_BASE_URL}/process-image", files=files)
        
        if response.status_code == 400:
            print("OK Validación de archivo funcionando correctamente")
            print(f"   Respuesta: {response.json()}")
        else:
            print(f"ERROR Error inesperado en validación: {response.status_code}")
        
        # Limpiar archivo temporal
        os.remove("test.txt")
    except Exception as e:
        print(f"ERROR Error inesperado: {str(e)}")
    return True

def main():
    """Función principal de prueba"""
    print(" Iniciando pruebas de la API de procesamiento de imágenes con scikit-image\n")
    
    # Probar endpoints básicos
    if not test_health_endpoint():
        print("\nERROR Las pruebas no pueden continuar. Verifica que la API esté ejecutándose.")
        return
    
    test_root_endpoint() 
    test_invalid_file()
    test_process_image_endpoint()
    test_process_pdf_endpoint()
    
    print("\nOK Pruebas completadas!")
    print("\n Para probar manualmente:")
    print(f"   1. Visita: {API_BASE_URL}/docs")
    print(f"   2. Usa el endpoint POST /process-image")
    print(f"   3. Sube una imagen (.jpg, .jpeg, .png) o PDF y ve el resultado")

if __name__ == "__main__":
    main()
