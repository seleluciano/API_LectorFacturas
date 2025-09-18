prob#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import os
import json

def test_improved_endpoint():
    """Prueba el endpoint mejorado /process-invoices-structured"""
    
    # URL del endpoint
    url = "http://localhost:8000/process-invoices-structured"
    
    # Verificar que el servidor esté corriendo
    try:
        response = requests.get("http://localhost:8000/docs")
        if response.status_code != 200:
            print("❌ El servidor no está corriendo. Ejecuta: python main.py")
            return
    except:
        print("❌ El servidor no está corriendo. Ejecuta: python main.py")
        return
    
    print("Probando endpoint mejorado /process-invoices-structured:")
    print("=" * 60)
    
    # Crear archivos de prueba (simulados)
    test_files = []
    
    # Verificar si hay archivos de prueba en el directorio
    test_dir = "temp_uploads"
    if os.path.exists(test_dir):
        files = [f for f in os.listdir(test_dir) if f.endswith(('.png', '.jpg', '.jpeg', '.pdf'))]
        if files:
            print(f"Archivos encontrados en {test_dir}: {files}")
            
            # Preparar archivos para envío
            for file_name in files:
                file_path = os.path.join(test_dir, file_name)
                if os.path.exists(file_path):
                    test_files.append(('files', (file_name, open(file_path, 'rb'), 'image/jpeg')))
        else:
            print(f"No se encontraron archivos de imagen/PDF en {test_dir}")
            print("Crea algunos archivos de prueba o usa archivos existentes")
            return
    else:
        print(f"Directorio {test_dir} no existe")
        return
    
    if not test_files:
        print("No hay archivos para probar")
        return
    
    try:
        # Enviar solicitud
        print(f"Enviando {len(test_files)} archivos al endpoint mejorado...")
        response = requests.post(url, files=test_files)
        
        # Cerrar archivos
        for _, (_, file_obj, _) in test_files:
            file_obj.close()
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Respuesta exitosa:")
            print(f"Total archivos: {data['total_files']}")
            print(f"Total facturas encontradas: {data['total_invoices']}")
            print(f"Archivos procesados: {data['summary']['files_processed']}")
            print(f"Tiempo total de procesamiento: {data['summary']['total_processing_time']:.2f}s")
            print(f"Confianza promedio: {data['summary']['average_confidence']:.2f}")
            
            print("\n" + "="*60)
            print("DETALLES DE CADA FACTURA:")
            print("="*60)
            
            for i, invoice in enumerate(data['invoices'], 1):
                print(f"\n--- FACTURA {i} ---")
                print(f"Archivo: {invoice['filename']} (Índice: {invoice['file_index']})")
                print(f"Índice de factura: {invoice['invoice_index']}")
                print(f"Estado: {invoice['status']}")
                print(f"Confianza: {invoice['parsing_confidence']:.2f}")
                print(f"Tiempo de procesamiento: {invoice['processing_time']:.2f}s")
                
                # Mostrar campos extraídos
                fields = invoice['invoice_fields']
                print("\n📋 CAMPOS EXTRAÍDOS:")
                print(f"  Tipo de factura: {fields.get('tipo_factura', 'N/A')}")
                print(f"  Vendedor: {fields.get('razon_social_vendedor', 'N/A')}")
                print(f"  CUIT Vendedor: {fields.get('cuit_vendedor', 'N/A')}")
                print(f"  Comprador: {fields.get('razon_social_comprador', 'N/A')}")
                print(f"  CUIT Comprador: {fields.get('cuit_comprador', 'N/A')}")
                print(f"  Condición IVA: {fields.get('condicion_iva_comprador', 'N/A')}")
                print(f"  Fecha emisión: {fields.get('fecha_emision', 'N/A')}")
                print(f"  Número factura: {fields.get('numero_factura', 'N/A')}")
                print(f"  Punto de venta: {fields.get('punto_venta', 'N/A')}")
                print(f"  Subtotal: ${fields.get('subtotal', 'N/A')}")
                print(f"  IVA: ${fields.get('iva', 'N/A')}")
                print(f"  Deuda impositiva: ${fields.get('deuda_impositiva', 'N/A')}")
                print(f"  Importe total: ${fields.get('importe_total', 'N/A')}")
                print(f"  Condición de venta: {fields.get('condicion_venta', 'N/A')}")
                
                # Mostrar items si existen
                items = fields.get('items', [])
                if items:
                    print(f"\n📦 ITEMS ({len(items)} items):")
                    for j, item in enumerate(items, 1):
                        print(f"  {j}. {item.get('descripcion', 'N/A')}")
                        print(f"     Código: {item.get('codigo', 'N/A')}")
                        print(f"     Cantidad: {item.get('cantidad', 'N/A')} {item.get('unidad_medida', 'unidad')}")
                        print(f"     Precio unitario: ${item.get('precio_unitario', 'N/A')}")
                        print(f"     Subtotal: ${item.get('subtotal', 'N/A')}")
                else:
                    print("\n📦 ITEMS: No se encontraron items")
                
                # Mostrar texto raw (truncado)
                raw_text = invoice.get('raw_text', '')
                if raw_text:
                    print(f"\n📄 TEXTO EXTRAÍDO (primeros 200 caracteres):")
                    print(f"  {raw_text[:200]}...")
                
                print("-" * 40)
            
            # Guardar resultado en archivo JSON
            output_file = "test_result_structured.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Resultado guardado en: {output_file}")
                    
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Error en la solicitud: {e}")

if __name__ == "__main__":
    test_improved_endpoint()
