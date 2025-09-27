#!/usr/bin/env python3
"""
Script para diagnosticar el problema con el procesamiento de PDFs
"""
import sys
import os
sys.path.append('.')
from fastapi.testclient import TestClient
from main import app
import tempfile
import shutil

def debug_pdf_issue():
    """Diagnosticar el problema con el procesamiento de PDFs"""
    try:
        # Crear cliente de prueba
        client = TestClient(app)
        
        # Verificar que el archivo PDF existe
        pdf_path = "factura_2.pdf"
        if not os.path.exists(pdf_path):
            print(f"Error: Archivo {pdf_path} no encontrado")
            return False
        
        print(f"=== DIAGNÓSTICO DEL PROBLEMA ===")
        print(f"Archivo: {pdf_path}")
        print(f"Tamaño: {os.path.getsize(pdf_path)} bytes")
        
        # 1. Probar endpoint de múltiples imágenes
        print("\n1. Probando /process-multiple-images...")
        with open(pdf_path, "rb") as f:
            files = {"files": (pdf_path, f, "application/pdf")}
            response = client.post("/process-multiple-images", files=files)
        
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Success: {data.get('success')}")
            print(f"Total files: {data.get('total_files')}")
            print(f"Invoice files: {data.get('invoice_files')}")
            print(f"Text files: {data.get('text_files')}")
            print(f"Total invoices: {data.get('total_invoices')}")
            
            # Analizar el resultado
            if data.get('results'):
                result = data['results'][0]
                print(f"\n=== ANÁLISIS DETALLADO ===")
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
                
                # Verificar metadata
                metadata = result.get('metadata', {})
                print(f"\n=== METADATA ===")
                for key, value in metadata.items():
                    print(f"{key}: {value}")
                
                # Verificar si hay texto extraído
                raw_text = result.get('raw_text', '')
                if raw_text:
                    print(f"\n=== MUESTRA DE TEXTO ===")
                    print(raw_text[:300] + "..." if len(raw_text) > 300 else raw_text)
                else:
                    print("\n=== PROBLEMA: TEXTO VACÍO ===")
                    print("El archivo se procesó pero no se extrajo texto")
                    
                    # Verificar si hay bloques de texto
                    text_blocks = result.get('text_blocks', [])
                    if text_blocks:
                        print(f"Pero hay {len(text_blocks)} bloques de texto:")
                        for i, block in enumerate(text_blocks[:3]):  # Mostrar solo los primeros 3
                            print(f"  Bloque {i+1}: {block.get('text', '')[:100]}...")
                    else:
                        print("No hay bloques de texto tampoco")
                
                # Verificar si se detectó como factura
                if result.get('type') == 'invoice':
                    print("\n✅ Se detectó como factura")
                    return True
                elif result.get('type') == 'general_text':
                    print("\n⚠️  Se detectó como texto general")
                    if raw_text:
                        print("Pero tiene contenido de texto")
                        return True
                    else:
                        print("Y no tiene contenido de texto")
                        return False
                else:
                    print(f"\n❌ Tipo desconocido: {result.get('type')}")
                    return False
            else:
                print("\n❌ No hay resultados")
                return False
        else:
            print(f"Error en la petición: {response.text}")
            return False
            
    except Exception as e:
        print(f"Error en el diagnóstico: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = debug_pdf_issue()
    if success:
        print("\n✅ Diagnóstico exitoso!")
    else:
        print("\n❌ Problema detectado!")
