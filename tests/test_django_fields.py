#!/usr/bin/env python3
"""
Script para probar los campos específicos del modelo Django
"""

import requests
import json

def test_django_fields():
    """Probar el endpoint con campos del modelo Django"""
    
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
                
                print("\n🎯 CAMPOS DEL MODELO DJANGO:")
                print("=" * 50)
                
                invoice_fields = data.get('invoice_fields', {})
                
                print("📋 CAMPOS PRINCIPALES:")
                print(f"  🏷️  Tipo Factura: '{invoice_fields.get('tipo_factura', 'No detectado')}'")
                print(f"  🏢 Razón Social Vendedor: '{invoice_fields.get('razon_social_vendedor', 'No detectado')}'")
                print(f"  🆔 CUIT Vendedor: '{invoice_fields.get('cuit_vendedor', 'No detectado')}'")
                print(f"  👤 Razón Social Comprador: '{invoice_fields.get('razon_social_comprador', 'No detectado')}'")
                print(f"  🆔 CUIT Comprador: '{invoice_fields.get('cuit_comprador', 'No detectado')}'")
                print(f"  📊 Condición IVA Comprador: '{invoice_fields.get('condicion_iva_comprador', 'No detectado')}'")
                print(f"  💳 Condición Venta: '{invoice_fields.get('condicion_venta', 'No detectado')}'")
                print(f"  📅 Fecha Emisión: '{invoice_fields.get('fecha_emision', 'No detectado')}'")
                
                print("\n💰 IMPORTES:")
                print(f"  📈 Subtotal: '{invoice_fields.get('subtotal', 'No detectado')}'")
                print(f"  💸 Deuda Impositiva: '{invoice_fields.get('deuda_impositiva', 'No detectado')}'")
                print(f"  💰 Importe Total: '{invoice_fields.get('importe_total', 'No detectado')}'")
                
                print("\n📄 CAMPOS ADICIONALES:")
                print(f"  🔢 Número Factura: '{invoice_fields.get('numero_factura', 'No detectado')}'")
                print(f"  🏪 Punto Venta: '{invoice_fields.get('punto_venta', 'No detectado')}'")
                
                # Mostrar items
                items = invoice_fields.get('items', [])
                if items:
                    print(f"\n🛍️  ITEMS DE LA FACTURA ({len(items)}):")
                    for i, item in enumerate(items, 1):
                        print(f"  {i}. {item.get('descripcion', 'Sin descripción')}")
                        print(f"     Código: '{item.get('codigo', 'N/A')}'")
                        print(f"     Cantidad: {item.get('cantidad', 'N/A')}")
                        print(f"     Unidad: {item.get('unidad_medida', 'N/A')}")
                        print(f"     Precio Unit.: ${item.get('precio_unitario', 'N/A')}")
                        print(f"     Bonificación: ${item.get('importe_bonificacion', 'N/A')}")
                        print(f"     Subtotal: ${item.get('subtotal', 'N/A')}")
                        print()
                
                # Verificar campos críticos
                print("\n✅ VERIFICACIÓN DE CAMPOS CRÍTICOS:")
                critical_fields = [
                    'tipo_factura', 'razon_social_vendedor', 'cuit_vendedor',
                    'razon_social_comprador', 'cuit_comprador', 'fecha_emision',
                    'subtotal', 'importe_total'
                ]
                
                found_fields = 0
                for field in critical_fields:
                    if invoice_fields.get(field) and invoice_fields.get(field) != 'No detectado':
                        print(f"  ✅ {field}: {invoice_fields.get(field)}")
                        found_fields += 1
                    else:
                        print(f"  ❌ {field}: No detectado")
                
                print(f"\n📊 RESUMEN: {found_fields}/{len(critical_fields)} campos críticos detectados")
                
                # Guardar resultado
                with open('django_fields_result.json', 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                print(f"\n💾 Resultado guardado en: django_fields_result.json")
                
            else:
                print(f"❌ Error: {response.status_code}")
                print(response.text)
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Probando Campos del Modelo Django")
    print("=" * 40)
    test_django_fields()
