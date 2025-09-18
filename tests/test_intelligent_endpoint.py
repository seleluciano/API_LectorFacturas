#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import os
import json

def test_intelligent_endpoints():
    """Prueba los endpoints inteligentes que detectan automáticamente facturas"""
    
    # URLs de los endpoints
    single_url = "http://localhost:8000/process-image"
    multiple_url = "http://localhost:8000/process-multiple-images"
    
    # Verificar que el servidor esté corriendo
    try:
        response = requests.get("http://localhost:8000/docs")
        if response.status_code != 200:
            print("❌ El servidor no está corriendo. Ejecuta: python main.py")
            return
    except:
        print("❌ El servidor no está corriendo. Ejecuta: python main.py")
        return
    
    print("Probando endpoints INTELIGENTES:")
    print("=" * 60)
    
    # Verificar si hay archivos de prueba en el directorio
    test_dir = "temp_uploads"
    if not os.path.exists(test_dir):
        print(f"❌ Directorio {test_dir} no existe")
        return
    
    files = [f for f in os.listdir(test_dir) if f.endswith(('.png', '.jpg', '.jpeg', '.pdf'))]
    if not files:
        print(f"❌ No se encontraron archivos de imagen/PDF en {test_dir}")
        return
    
    print(f"📁 Archivos encontrados: {files}")
    
    # PROBAR ENDPOINT DE UN ARCHIVO
    print("\n" + "="*60)
    print("🔍 PROBANDO ENDPOINT INTELIGENTE (1 archivo):")
    print("="*60)
    
    test_single_file(test_dir, files[0], single_url)
    
    # PROBAR ENDPOINT DE MÚLTIPLES ARCHIVOS
    if len(files) > 1:
        print("\n" + "="*60)
        print("🔍 PROBANDO ENDPOINT INTELIGENTE (múltiples archivos):")
        print("="*60)
        
        test_multiple_files(test_dir, files[:2], multiple_url)

def test_single_file(test_dir, filename, url):
    """Prueba el endpoint de un solo archivo"""
    file_path = os.path.join(test_dir, filename)
    
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (filename, f, 'image/jpeg')}
            response = requests.post(url, files=files)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Archivo: {filename}")
            print(f"📊 Tipo detectado: {data.get('type', 'unknown')}")
            print(f"⏱️  Tiempo: {data.get('processing_time', 0):.2f}s")
            
            if data.get('type') == 'invoice':
                print(f"📄 Facturas encontradas: {data.get('total_invoices', 0)}")
                
                for i, invoice in enumerate(data.get('invoices', []), 1):
                    fields = invoice.get('invoice_fields', {})
                    print(f"\n  📋 FACTURA {i}:")
                    print(f"    Vendedor: {fields.get('razon_social_vendedor', 'N/A')}")
                    print(f"    Comprador: {fields.get('razon_social_comprador', 'N/A')}")
                    print(f"    Total: ${fields.get('importe_total', 'N/A')}")
                    print(f"    Confianza: {invoice.get('parsing_confidence', 0):.2f}")
                    
            elif data.get('type') == 'general_text':
                text = data.get('raw_text', '')
                print(f"📝 Texto extraído: {len(text)} caracteres")
                print(f"📄 Primeros 100 caracteres: {text[:100]}...")
                
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_multiple_files(test_dir, filenames, url):
    """Prueba el endpoint de múltiples archivos"""
    
    try:
        files = []
        for filename in filenames:
            file_path = os.path.join(test_dir, filename)
            files.append(('files', (filename, open(file_path, 'rb'), 'image/jpeg')))
        
        response = requests.post(url, files=files)
        
        # Cerrar archivos
        for _, (_, file_obj, _) in files:
            file_obj.close()
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Archivos procesados: {data.get('successful_files', 0)}/{data.get('total_files', 0)}")
            print(f"📄 Archivos de facturas: {data.get('invoice_files', 0)}")
            print(f"📝 Archivos de texto: {data.get('text_files', 0)}")
            print(f"📊 Total facturas encontradas: {data.get('total_invoices', 0)}")
            print(f"⏱️  Tiempo total: {data.get('summary', {}).get('processing_time_total', 0):.2f}s")
            
            print("\n📋 DETALLES POR ARCHIVO:")
            for result in data.get('results', []):
                print(f"\n  📁 Archivo {result.get('file_index', '?')}: {result.get('filename', 'N/A')}")
                print(f"    Tipo: {result.get('type', 'unknown')}")
                print(f"    Estado: {'✅' if result.get('success') else '❌'}")
                
                if result.get('type') == 'invoice':
                    invoices = result.get('invoices', [])
                    print(f"    Facturas: {len(invoices)}")
                    
                    for i, invoice in enumerate(invoices, 1):
                        fields = invoice.get('invoice_fields', {})
                        print(f"      📄 Factura {i}: {fields.get('razon_social_vendedor', 'N/A')} - ${fields.get('importe_total', 'N/A')}")
                        
                elif result.get('type') == 'general_text':
                    text_len = len(result.get('raw_text', ''))
                    print(f"    Texto: {text_len} caracteres")
                    
                elif result.get('type') == 'error':
                    print(f"    Error: {result.get('error', 'Error desconocido')}")
            
            # Guardar resultado
            output_file = "test_intelligent_result.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Resultado guardado en: {output_file}")
                
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_intelligent_endpoints()
