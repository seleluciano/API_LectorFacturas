#!/usr/bin/env python3
"""
Script para probar el flujo completo: PDF -> procesamiento -> API externa
"""
import sys
import os
sys.path.append('.')
from fastapi.testclient import TestClient
from main import app
import json

def test_complete_flow():
    """Probar el flujo completo con el endpoint de múltiples facturas"""
    try:
        # Crear cliente de prueba
        client = TestClient(app)
        
        # Verificar que el archivo PDF existe
        pdf_path = "factura_2.pdf"
        if not os.path.exists(pdf_path):
            print(f"Error: Archivo {pdf_path} no encontrado")
            return False
        
        print(f"=== PROBANDO FLUJO COMPLETO ===")
        print(f"Archivo: {pdf_path}")
        print(f"Tamaño: {os.path.getsize(pdf_path)} bytes")
        
        # 1. Probar endpoint de múltiples imágenes
        print("\n1. Probando /process-multiple-images...")
        with open(pdf_path, "rb") as f:
            files = {"files": (pdf_path, f, "application/pdf")}
            response = client.post("/process-multiple-images", files=files)
        
        if response.status_code != 200:
            print(f"❌ Error en process-multiple-images: {response.status_code}")
            print(response.text)
            return False
        
        data = response.json()
        print(f"✅ Status: {response.status_code}")
        print(f"✅ Success: {data.get('success')}")
        print(f"✅ Total files: {data.get('total_files')}")
        print(f"✅ Invoice files: {data.get('invoice_files')}")
        print(f"✅ Total invoices: {data.get('total_invoices')}")
        
        # Analizar el resultado
        if data.get('results'):
            result = data['results'][0]
            print(f"\n=== ANÁLISIS DEL RESULTADO ===")
            print(f"Type: {result.get('type')}")
            print(f"Success: {result.get('success')}")
            print(f"Processing time: {result.get('processing_time'):.2f}s")
            print(f"Raw text length: {len(result.get('raw_text', ''))}")
            
            # Verificar si se detectó como factura
            if result.get('type') == 'invoice':
                print("✅ Se detectó como factura")
                
                # Mostrar campos extraídos si están disponibles
                if 'invoices' in result:
                    invoices = result['invoices']
                    if invoices:
                        invoice = invoices[0]
                        print(f"✅ Factura procesada exitosamente")
                        print(f"✅ Confianza: {invoice.get('parsing_confidence', 0):.2f}")
                        
                        extracted_fields = invoice.get('extracted_fields', {})
                        if extracted_fields:
                            print(f"✅ Campos extraídos: {len(extracted_fields)}")
                            print("\n=== CAMPOS EXTRAÍDOS ===")
                            for key, value in extracted_fields.items():
                                print(f"  {key}: {value}")
                        else:
                            print("⚠️  No se extrajeron campos")
                else:
                    print("⚠️  No se encontraron facturas en el resultado")
            else:
                print(f"❌ No se detectó como factura (tipo: {result.get('type')})")
                return False
        
        # 2. Probar endpoint de envío a API externa
        print("\n2. Probando /process-and-send-factura...")
        with open(pdf_path, "rb") as f:
            files = {"file": (pdf_path, f, "application/pdf")}
            response = client.post("/process-and-send-factura", files=files)
        
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Envío a API externa exitoso")
            print(f"Status: {data.get('status')}")
            print(f"Message: {data.get('message')}")
            
            # Mostrar respuesta de la API externa
            external_response = data.get('respuesta_api_externa', {})
            if external_response:
                print("\n=== RESPUESTA API EXTERNA ===")
                print(json.dumps(external_response, indent=2, ensure_ascii=False))
            else:
                print("⚠️  No hay respuesta de la API externa")
        else:
            print(f"❌ Error en envío a API externa: {response.status_code}")
            print(response.text)
            return False
        
        print("\n🎉 FLUJO COMPLETO EXITOSO!")
        return True
        
    except Exception as e:
        print(f"❌ Error en la prueba: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_complete_flow()
    if success:
        print("\n✅ Todas las pruebas pasaron!")
    else:
        print("\n❌ Algunas pruebas fallaron!")
