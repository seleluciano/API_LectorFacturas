#!/usr/bin/env python3
"""
Script para probar el envío de PDF convertido a imagen a la API externa
"""
import sys
import os
import time
sys.path.append('.')
from fastapi.testclient import TestClient
from main import app

def test_pdf_to_image_send():
    """Probar el envío de PDF convertido a imagen"""
    try:
        # Crear cliente de prueba
        client = TestClient(app)
        
        # Verificar que el archivo PDF existe
        pdf_path = "factura_2.pdf"
        if not os.path.exists(pdf_path):
            print(f"Error: Archivo {pdf_path} no encontrado")
            return False
        
        file_size = os.path.getsize(pdf_path)
        print(f"=== PRUEBA DE ENVÍO PDF CONVERTIDO A IMAGEN ===")
        print(f"Archivo: {pdf_path}")
        print(f"Tamaño: {file_size} bytes ({file_size/1024:.1f} KB)")
        
        # Medir tiempo de procesamiento
        start_time = time.time()
        
        # Probar endpoint de envío a API externa
        print("\nEnviando petición a /process-and-send-factura...")
        with open(pdf_path, "rb") as f:
            files = {"file": (pdf_path, f, "application/pdf")}
            response = client.post("/process-and-send-factura", files=files)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        print(f"Tiempo total: {processing_time:.2f} segundos")
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n=== RESULTADO ===")
            print(f"Status: {data.get('status')}")
            print(f"Message: {data.get('message')}")
            
            # Mostrar procesamiento local
            procesamiento_local = data.get('procesamiento_local', {})
            if procesamiento_local:
                print(f"\n=== PROCESAMIENTO LOCAL ===")
                print(f"Filename: {procesamiento_local.get('filename')}")
                print(f"File size: {procesamiento_local.get('file_size')}")
                print(f"Processing time: {procesamiento_local.get('processing_time'):.2f}s")
                print(f"Confidence: {procesamiento_local.get('confidence', 0):.2f}")
                
                # Mostrar campos extraídos
                extracted_fields = procesamiento_local.get('extracted_fields', {})
                if extracted_fields:
                    print(f"Campos extraídos: {len(extracted_fields)}")
                    print("\n=== CAMPOS PRINCIPALES ===")
                    important_fields = ['razon_social_vendedor', 'cuit_vendedor', 'importe_total', 'fecha_emision']
                    for field in important_fields:
                        if field in extracted_fields:
                            print(f"  {field}: {extracted_fields[field]}")
                else:
                    print("⚠️  No se extrajeron campos")
            
            # Mostrar respuesta de la API externa
            respuesta_externa = data.get('respuesta_api_externa', {})
            if respuesta_externa:
                print(f"\n=== RESPUESTA API EXTERNA ===")
                print(f"Respuesta: {respuesta_externa}")
                
                # Verificar si hay error
                if 'error' in respuesta_externa:
                    print(f"❌ Error en API externa: {respuesta_externa['error']}")
                    return False
                else:
                    print("✅ API externa respondió correctamente")
                    return True
            else:
                print("⚠️  No hay respuesta de la API externa")
                return False
        else:
            print(f"❌ Error en la petición: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Error en la prueba: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_pdf_to_image_send()
    if success:
        print("\n🎉 Prueba exitosa!")
    else:
        print("\n💥 Prueba falló!")
