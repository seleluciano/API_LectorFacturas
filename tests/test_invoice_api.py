#!/usr/bin/env python3
"""
Script para probar el nuevo endpoint de procesamiento de facturas
"""

import requests
import json
import os
import time

def test_invoice_endpoint():
    """Probar el endpoint /process-invoice"""
    
    # URL del endpoint
    url = "http://localhost:8000/process-invoice"
    
    # Verificar que el servidor esté corriendo
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code != 200:
            print("❌ El servidor no está corriendo. Ejecuta: python start_server.py")
            return
        print("✅ Servidor corriendo correctamente")
    except requests.exceptions.RequestException:
        print("❌ No se puede conectar al servidor. Ejecuta: python start_server.py")
        return
    
    # Buscar archivos de imagen para probar
    test_files = []
    for ext in ['.jpg', '.jpeg', '.png', '.pdf']:
        for file in os.listdir('.'):
            if file.lower().endswith(ext):
                test_files.append(file)
                break
    
    if not test_files:
        print("❌ No se encontraron archivos de imagen para probar")
        print("💡 Coloca una imagen de factura en el directorio actual")
        return
    
    print(f"📁 Archivos encontrados: {test_files}")
    
    # Probar con el primer archivo encontrado
    test_file = test_files[0]
    print(f"🧪 Probando con archivo: {test_file}")
    
    try:
        # Preparar el archivo para envío
        with open(test_file, 'rb') as f:
            files = {'file': (test_file, f, 'image/jpeg')}
            
            print("📤 Enviando archivo...")
            start_time = time.time()
            
            # Enviar request
            response = requests.post(url, files=files, timeout=60)
            
            end_time = time.time()
            request_time = end_time - start_time
            
            print(f"⏱️  Tiempo de request: {request_time:.2f} segundos")
            print(f"📊 Status Code: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ Request exitoso!")
                
                # Parsear respuesta
                data = response.json()
                
                print("\n📋 RESULTADO ESTRUCTURADO:")
                print("=" * 50)
                
                # Mostrar campos de la factura
                invoice_fields = data.get('invoice_fields', {})
                print("🏢 EMPRESA:")
                print(f"  • Razón Social: {invoice_fields.get('empresa', 'No detectado')}")
                print(f"  • CUIT: {invoice_fields.get('cuit', 'No detectado')}")
                print(f"  • Punto de Venta: {invoice_fields.get('punto_venta', 'No detectado')}")
                
                print("\n📄 FACTURA:")
                print(f"  • Número: {invoice_fields.get('numero_factura', 'No detectado')}")
                print(f"  • Fecha: {invoice_fields.get('fecha', 'No detectado')}")
                
                print("\n👤 CLIENTE:")
                print(f"  • Nombre: {invoice_fields.get('cliente', 'No detectado')}")
                print(f"  • DNI: {invoice_fields.get('dni_cliente', 'No detectado')}")
                print(f"  • Domicilio: {invoice_fields.get('domicilio_cliente', 'No detectado')}")
                
                print("\n💰 IMPORTES:")
                print(f"  • Subtotal: {invoice_fields.get('subtotal', 'No detectado')}")
                print(f"  • IVA: {invoice_fields.get('iva', 'No detectado')}")
                print(f"  • Total: {invoice_fields.get('importe_total', 'No detectado')}")
                
                # Mostrar productos si existen
                productos = invoice_fields.get('productos', [])
                if productos:
                    print(f"\n🛍️  PRODUCTOS ({len(productos)}):")
                    for i, producto in enumerate(productos, 1):
                        print(f"  {i}. {producto.get('descripcion', 'Sin descripción')}")
                        print(f"     Cantidad: {producto.get('cantidad', 'N/A')}")
                        print(f"     Precio: ${producto.get('precio_unitario', 'N/A')}")
                        print(f"     Subtotal: ${producto.get('subtotal', 'N/A')}")
                
                print("\n📊 METADATOS:")
                print(f"  • Tiempo de procesamiento: {data.get('processing_time', 0):.2f}s")
                print(f"  • Tamaño del archivo: {data.get('file_size', 0):,} bytes")
                print(f"  • Confianza del parsing: {data.get('metadata', {}).get('invoice_parsing', {}).get('parsing_confidence', 0):.2%}")
                
                print("\n📝 TEXTO COMPLETO:")
                print("-" * 30)
                raw_text = data.get('raw_text', '')
                if raw_text:
                    print(raw_text[:500] + "..." if len(raw_text) > 500 else raw_text)
                else:
                    print("No se extrajo texto")
                
                # Guardar respuesta en archivo
                output_file = f"invoice_response_{int(time.time())}.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                print(f"\n💾 Respuesta guardada en: {output_file}")
                
            else:
                print(f"❌ Error en el request: {response.status_code}")
                print(f"📝 Mensaje: {response.text}")
                
    except requests.exceptions.Timeout:
        print("⏰ Timeout - El request tardó demasiado")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error en el request: {e}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

def test_old_endpoint():
    """Probar el endpoint original para comparar"""
    
    url = "http://localhost:8000/process-image"
    
    # Buscar archivos de imagen para probar
    test_files = []
    for ext in ['.jpg', '.jpeg', '.png', '.pdf']:
        for file in os.listdir('.'):
            if file.lower().endswith(ext):
                test_files.append(file)
                break
    
    if not test_files:
        return
    
    test_file = test_files[0]
    print(f"\n🔄 Probando endpoint original con: {test_file}")
    
    try:
        with open(test_file, 'rb') as f:
            files = {'file': (test_file, f, 'image/jpeg')}
            
            response = requests.post(url, files=files, timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Endpoint original funcionando")
                print(f"⏱️  Tiempo: {data.get('processing_time', 0):.2f}s")
                print(f"📝 Texto extraído: {len(data.get('raw_text', ''))} caracteres")
            else:
                print(f"❌ Error en endpoint original: {response.status_code}")
                
    except Exception as e:
        print(f"❌ Error probando endpoint original: {e}")

if __name__ == "__main__":
    print("🚀 Probando API de Procesamiento de Facturas")
    print("=" * 50)
    
    # Probar endpoint nuevo
    test_invoice_endpoint()
    
    # Probar endpoint original para comparar
    test_old_endpoint()
    
    print("\n✨ Pruebas completadas!")
    print("\n💡 Para usar con Postman:")
    print("   • URL: http://localhost:8000/process-invoice")
    print("   • Método: POST")
    print("   • Body: form-data")
    print("   • Key: file, Type: File")
    print("   • Value: selecciona tu archivo de factura")
