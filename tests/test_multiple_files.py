#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import os

def test_multiple_files_endpoint():
    """Prueba el endpoint de múltiples archivos"""
    
    # URL del endpoint
    url = "http://localhost:8000/process-multiple-invoices"
    
    # Verificar que el servidor esté corriendo
    try:
        response = requests.get("http://localhost:8000/docs")
        if response.status_code != 200:
            print("❌ El servidor no está corriendo. Ejecuta: python main.py")
            return
    except:
        print("❌ El servidor no está corriendo. Ejecuta: python main.py")
        return
    
    print("Probando endpoint de múltiples archivos:")
    print("=" * 50)
    
    # Crear archivos de prueba (simulados)
    test_files = []
    
    # Verificar si hay archivos de prueba en el directorio
    test_dir = "temp_uploads"
    if os.path.exists(test_dir):
        files = [f for f in os.listdir(test_dir) if f.endswith(('.png', '.jpg', '.jpeg', '.pdf'))]
        if files:
            print(f"Archivos encontrados en {test_dir}: {files[:2]}")  # Tomar máximo 2 archivos
            
            # Preparar archivos para envío
            for file_name in files[:2]:
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
        print(f"Enviando {len(test_files)} archivos...")
        response = requests.post(url, files=test_files)
        
        # Cerrar archivos
        for _, (_, file_obj, _) in test_files:
            file_obj.close()
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Respuesta exitosa:")
            print(f"Total archivos: {data['total_files']}")
            print(f"Archivos exitosos: {data['successful_files']}")
            print(f"Archivos fallidos: {data['failed_files']}")
            print(f"Total facturas encontradas: {data['summary']['total_invoices_found']}")
            print(f"Tiempo total de procesamiento: {data['summary']['processing_time_total']:.2f}s")
            
            print("\nDetalles por archivo:")
            for i, result in enumerate(data['results'], 1):
                print(f"\n--- ARCHIVO {i}: {result['filename']} ---")
                if result.get('success'):
                    print(f"✅ Procesado exitosamente")
                    print(f"Tiempo: {result.get('processing_time', 0):.2f}s")
                    
                    # Mostrar facturas encontradas
                    invoice_data = result.get('metadata', {}).get('invoice_parsing', {})
                    if invoice_data:
                        total_invoices = invoice_data.get('total_invoices', 0)
                        print(f"Facturas encontradas: {total_invoices}")
                        
                        for j, invoice in enumerate(invoice_data.get('invoices', []), 1):
                            if invoice.get('success'):
                                fields = invoice.get('extracted_fields', {})
                                print(f"  Factura {j}:")
                                print(f"    Vendedor: {fields.get('razon_social_vendedor', 'N/A')}")
                                print(f"    Comprador: {fields.get('razon_social_comprador', 'N/A')}")
                                print(f"    Total: ${fields.get('importe_total', 'N/A')}")
                else:
                    print(f"❌ Error: {result.get('error', 'Error desconocido')}")
                    
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Error en la solicitud: {e}")

if __name__ == "__main__":
    test_multiple_files_endpoint()
