#!/usr/bin/env python3
"""
Script para probar el cálculo de deuda impositiva directamente
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.invoice_parser import InvoiceParser

def test_calculation():
    """Probar el cálculo de deuda impositiva directamente"""
    
    # Texto de ejemplo de la factura
    sample_text = """ORIGINAL A : A RA HighTech Innovations SRL | eoo.001 FACTU Comp. Nro: 21696565 Punto de Venta: 0004 Fecha de Emisión: 27/04/2025 Razón Social: HighTech Innovations SRL CUIT: 30-99999999-7 Ingresos Brutos: 26791555947 Fecha de Inicio de Actividades: 01/01/2020 Domicilio Comercial:Avenida Rivadavia 1200 Condición frente al IVA: Responsable Inscripto 1/01/2025 Hasta: 31/12/2025 Fecha de Vto. para el pago: 30/04/2025 Período Facturado Desde: DNI: 20-12345678-9 Apellido y Nombre / Razón Social: Ricardo Herrera Domicilio: Calle Montevideo 1200 Condición frente al IVA: Responsable Inscripto Condicién de venta: Contado [ Producto / Servicio [cantidad — Ju. medida] Precio unit. [%Bonit] imp. Bont. 'Subtotal 1 Análisis de datos 4 unidad 4.000,00 19% 3.040,00 12.960,00 Percepción IIBB: $ 1.500,00 IVA: $2.721,60 Subtotal: $12.960,00 Importe Otros Tributos: $710,00 Importe Total: $17.891,60 5165247793596 Fecha de Vto. de CAE: 01/05/2025 Pág. 1/1 Comprobante Autorizado Esta Agencia no se responsabllza poros datos Ingrezados an l dea de a operacion"""
    
    print("🧪 Probando Cálculo de Deuda Impositiva")
    print("=" * 50)
    
    # Crear parser
    parser = InvoiceParser()
    
    # Parsear la factura
    result = parser.parse_invoice(sample_text)
    
    if result['success']:
        fields = result['extracted_fields']
        
        print("📊 CAMPOS EXTRAÍDOS:")
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
                
                if deuda_calculada == 4.9316:
                    print("✅ Cálculo correcto!")
                else:
                    print(f"❌ Cálculo incorrecto. Debería ser 4.9316")
                    
            except Exception as e:
                print(f"❌ Error en cálculo manual: {e}")
        else:
            print("❌ No se encontraron los campos necesarios")
            
        # Mostrar todos los campos
        print(f"\n📋 TODOS LOS CAMPOS:")
        for key, value in fields.items():
            print(f"  {key}: {value}")
            
    else:
        print(f"❌ Error en el parsing: {result.get('error', 'Desconocido')}")

if __name__ == "__main__":
    test_calculation()
