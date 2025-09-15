 c#!/usr/bin/env python3
"""
Script para probar la nueva factura
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.invoice_parser import InvoiceParser

def test_new_invoice():
    """Probar la nueva factura"""
    
    # Texto de la nueva factura
    sample_text = """ORIGINAL Redes y Servicios SA Le PAGTURA Punto de Venta: 0004 Comp.Nro: 68759114 Razón Social: Redes y Servicios SA Fecha de Emisión: 27/04/2025 CUIT: 30-99999999-7 Ingresos Brutos: 24216953725 Fecha de Inicio de Actividades: 01/01/2020 Domicilio Comercial:Calle Tucumán 700 Condición frente al IVA: Responsable Inscripto 1/01/2025 Hasta: 31/12/2025 Fecha de Vto. para el pago: 30/04/2025 Período Facturado Desde: DNI: 20-12345678-9 Apellido y Nombre / Razón Social: Marcela Pérez Domicilio: Av. Santa Fe 1100 Condición frente al IVA: Monotributista Condición de venta: Contado [ Producto / servicio Ju. medida] Precioun [Bont] imp. Bont. Subtotal 1 Servicio de consultoria 1 unidad 10.000,00 14% 1.400,00 8.600,00 2 Instalación de servidores 1 unidad 12.000,00 2% 240,00 11.760,00 Percepción IIBB: $ 1.500,00 IVA: $4.275,60 Subtotal: $20.360,00 Importe Otros Tributos: $532,00 Importe Total: $26.667,60 5165247793596 Fecha de Vto. de CAE: 01/05/2025 Pág. 1/1 Comprobante Autorizado Esta Agencia no se responsabllza poros datos Ingrezados an l dea de a operacion"""
    
    print("🧪 Probando Nueva Factura")
    print("=" * 40)
    
    # Crear parser
    parser = InvoiceParser()
    
    # Parsear la factura
    result = parser.parse_invoice(sample_text)
    
    if result['success']:
        fields = result['extracted_fields']
        
        print("📊 CAMPOS EXTRAÍDOS:")
        print(f"  Razón Social Vendedor: {fields.get('razon_social_vendedor', 'No encontrado')}")
        print(f"  CUIT Vendedor: {fields.get('cuit_vendedor', 'No encontrado')}")
        print(f"  Razón Social Comprador: {fields.get('razon_social_comprador', 'No encontrado')}")
        print(f"  CUIT Comprador: {fields.get('cuit_comprador', 'No encontrado')}")
        print(f"  Subtotal: {fields.get('subtotal', 'No encontrado')}")
        print(f"  Importe Total: {fields.get('importe_total', 'No encontrado')}")
        print(f"  Deuda Impositiva: {fields.get('deuda_impositiva', 'No encontrado')}")
        
        # Verificar cálculo manual
        if 'importe_total' in fields and 'subtotal' in fields:
            try:
                importe_total = float(fields['importe_total'].replace('$', '').replace(',', '.'))
                subtotal = float(fields['subtotal'].replace('$', '').replace(',', '.'))
                deuda_calculada = importe_total - subtotal
                
                print(f"\n🔢 CÁLCULO MANUAL:")
                print(f"  {importe_total} - {subtotal} = {deuda_calculada}")
                
                if abs(deuda_calculada - 6.3076) < 0.01:
                    print("✅ Cálculo correcto!")
                else:
                    print(f"❌ Cálculo incorrecto. Debería ser 6.3076")
                    
            except Exception as e:
                print(f"❌ Error en cálculo manual: {e}")
        else:
            print("❌ No se encontraron los campos necesarios")
            
        # Mostrar items
        items = fields.get('items', [])
        if items:
            print(f"\n🛍️  ITEMS ({len(items)}):")
            for i, item in enumerate(items, 1):
                print(f"  {i}. {item.get('descripcion', 'Sin descripción')}")
                print(f"     Cantidad: {item.get('cantidad', 'N/A')}")
                print(f"     Precio: ${item.get('precio_unitario', 'N/A')}")
                print(f"     Subtotal: ${item.get('subtotal', 'N/A')}")
            
    else:
        print(f"❌ Error en el parsing: {result.get('error', 'Desconocido')}")

if __name__ == "__main__":
    test_new_invoice()
