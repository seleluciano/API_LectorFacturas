#!/usr/bin/env python3
"""
Script para probar el parsing mejorado
"""

import requests
import json

def test_improved_endpoint():
    """Probar el endpoint /process-invoice mejorado"""
    
    url = "http://localhost:8000/process-invoice"
    
    # Verificar que el servidor esté corriendo
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code != 200:
            print("❌ El servidor no está corriendo")
            return
        print("✅ Servidor corriendo")
    except:
        print("❌ No se puede conectar al servidor")
        return
    
    # Buscar archivos de imagen
    import os
    test_files = []
    for ext in ['.jpg', '.jpeg', '.png', '.pdf']:
        for file in os.listdir('.'):
            if file.lower().endswith(ext):
                test_files.append(file)
                break
    
    if not test_files:
        print("❌ No se encontraron archivos de imagen")
        return
    
    test_file = test_files[0]
    print(f"🧪 Probando con: {test_file}")
    
    try:
        with open(test_file, 'rb') as f:
            files = {'file': (test_file, f, 'image/jpeg')}
            
            print("📤 Enviando request...")
            response = requests.post(url, files=files, timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                
                print("\n🎯 CAMPOS MEJORADOS:")
                print("=" * 40)
                
                invoice_fields = data.get('invoice_fields', {})
                
                print(f"🏢 Empresa: '{invoice_fields.get('empresa', 'No detectado')}'")
                print(f"🆔 CUIT: '{invoice_fields.get('cuit', 'No detectado')}'")
                print(f"📄 Número: '{invoice_fields.get('numero_factura', 'No detectado')}'")
                print(f"📅 Fecha: '{invoice_fields.get('fecha', 'No detectado')}'")
                print(f"🏪 PV: '{invoice_fields.get('punto_venta', 'No detectado')}'")
                print(f"👤 Cliente: '{invoice_fields.get('cliente', 'No detectado')}'")
                print(f"🆔 DNI: '{invoice_fields.get('dni_cliente', 'No detectado')}'")
                print(f"🏠 Domicilio: '{invoice_fields.get('domicilio_cliente', 'No detectado')}'")
                print(f"💰 Total: '{invoice_fields.get('importe_total', 'No detectado')}'")
                print(f"📊 IVA: '{invoice_fields.get('iva', 'No detectado')}'")
                print(f"📈 Subtotal: '{invoice_fields.get('subtotal', 'No detectado')}'")
                
                # Mostrar productos
                productos = invoice_fields.get('productos', [])
                if productos:
                    print(f"\n🛍️  Productos ({len(productos)}):")
                    for i, producto in enumerate(productos, 1):
                        print(f"  {i}. {producto.get('descripcion', 'Sin descripción')}")
                        print(f"     Cantidad: {producto.get('cantidad', 'N/A')}")
                        print(f"     Precio: ${producto.get('precio_unitario', 'N/A')}")
                        print(f"     Subtotal: ${producto.get('subtotal', 'N/A')}")
                
                # Guardar resultado
                with open('improved_parsing_result.json', 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                print(f"\n💾 Resultado guardado en: improved_parsing_result.json")
                
            else:
                print(f"❌ Error: {response.status_code}")
                print(response.text)
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Probando Parsing Mejorado")
    print("=" * 30)
    test_improved_endpoint()
