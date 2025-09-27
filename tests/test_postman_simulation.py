#!/usr/bin/env python3
"""
Script para simular el flujo de Postman y verificar la corrección
"""
import sys
import os
sys.path.append('.')
from fastapi.testclient import TestClient
from main import app
import tempfile
import shutil

def test_postman_simulation():
    """Simular el flujo de Postman con el PDF"""
    try:
        # Crear cliente de prueba
        client = TestClient(app)
        
        # Verificar que el archivo PDF existe
        pdf_path = "factura_2.pdf"
        if not os.path.exists(pdf_path):
            print(f"Error: Archivo {pdf_path} no encontrado")
            return False
        
        print(f"Probando con archivo: {pdf_path}")
        print(f"Tamaño del archivo: {os.path.getsize(pdf_path)} bytes")
        
        # Simular la petición de Postman
        with open(pdf_path, "rb") as f:
            files = {"files": (pdf_path, f, "application/pdf")}
            
            print("Enviando petición a /process-multiple-images...")
            response = client.post("/process-multiple-images", files=files)
        
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("\n=== RESULTADO ===")
            print(f"Success: {data.get('success')}")
            print(f"Total files: {data.get('total_files')}")
            print(f"Successful files: {data.get('successful_files')}")
            print(f"Failed files: {data.get('failed_files')}")
            print(f"Invoice files: {data.get('invoice_files')}")
            print(f"Text files: {data.get('text_files')}")
            print(f"Total invoices: {data.get('total_invoices')}")
            
            # Analizar el primer resultado
            if data.get('results'):
                result = data['results'][0]
                print(f"\n=== PRIMER ARCHIVO ===")
                print(f"File index: {result.get('file_index')}")
                print(f"Filename: {result.get('filename')}")
                print(f"Type: {result.get('type')}")
                print(f"Success: {result.get('success')}")
                print(f"File size: {result.get('file_size')}")
                print(f"Content type: {result.get('content_type')}")
                print(f"Processing time: {result.get('processing_time')}")
                print(f"Raw text length: {len(result.get('raw_text', ''))}")
                print(f"Text blocks: {len(result.get('text_blocks', []))}")
                print(f"Tables: {len(result.get('tables', []))}")
                print(f"Figures: {len(result.get('figures', []))}")
                
                # Mostrar muestra del texto extraído
                raw_text = result.get('raw_text', '')
                if raw_text:
                    print(f"\n=== MUESTRA DE TEXTO ===")
                    print(raw_text[:300] + "..." if len(raw_text) > 300 else raw_text)
                else:
                    print("\n=== PROBLEMA: TEXTO VACÍO ===")
                    print("El archivo se procesó pero no se extrajo texto")
                
                # Verificar metadata
                metadata = result.get('metadata', {})
                if metadata:
                    print(f"\n=== METADATA ===")
                    for key, value in metadata.items():
                        print(f"{key}: {value}")
                
                # Verificar si se detectó como factura
                if result.get('type') == 'invoice':
                    print("\n✅ ÉXITO: Se detectó como factura")
                    return True
                elif result.get('type') == 'general_text' and raw_text:
                    print("\n⚠️  ADVERTENCIA: Se detectó como texto general pero con contenido")
                    return True
                else:
                    print("\n❌ ERROR: No se detectó contenido")
                    return False
            else:
                print("\n❌ ERROR: No hay resultados")
                return False
        else:
            print(f"Error en la petición: {response.text}")
            return False
            
    except Exception as e:
        print(f"Error en la prueba: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_postman_simulation()
    if success:
        print("\n🎉 Prueba exitosa!")
    else:
        print("\n💥 Prueba falló!")
