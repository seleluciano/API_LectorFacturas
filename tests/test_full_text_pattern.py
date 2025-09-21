#!/usr/bin/env python3
"""
Test con el texto completo de factura_11.png
"""

import re

def test_full_text():
    """Test con el texto completo"""
    
    # Texto completo extraído de factura_11.png
    full_text = """ORIGINAL Global Solutions SA oat | FACTURA Razón Social: Global Solutions SA         Punto de Venta: 0004 Comp.Nro: 47342647 Fecha de Emisión: 27/04/2025            CUIT: 30-99999999-7 Ingresos Brutos: Fecha de Inicio de Actividades: Domicilio Comercial:     Condición frente al IVA:         Período Facturado Desde: Hasta: Fecha de Vto. para el pago: DNI: 20-12345678-9 Apellido y Nombre / Razón Social: Alvaro Fernandez Condición frente al IVA: Responsable Inscripto Domiclio: Condicién de venta: Contado                               [ Producto / Servicio — [u. — preciount [ont] imp. Bont. Subtotal 1 Análisis de datos 4 unidad 4.000,00 12% 1.920,00 14.080,00 2 Soporte técnico 5 unidad 2.000,00 11% 1.100,00 8.900,00 3 Mantenimiento mensual y unidad 1.500,00 11% 495,00 4.005,00   Percepción IIBB: $ 1.500,00 IVA: Subtotal: $26.985,00 Importe Otros Tributos: $ Importe Total: $34.354,85             5165247793596 Fecha de Vto. de CAE: 01/05/2025 Pág. 1/1   Comprobante Autorizado Esta Agencia no se responsabllza poros datos Ingrezados an l dea de a operacion"""
    
    print("🔍 ANÁLISIS DEL TEXTO COMPLETO")
    print("=" * 60)
    
    # Patrón 1: código descripción cantidad unidad precio % bonificación importe_bonificación subtotal
    pattern = r'(\d+)\s+([A-Za-záéíóúñÁÉÍÓÚÑ\s\-\.]{3,}?)\s+(\d+)\s+unidad\s+([\d.,]+)\s+(\d+%)\s+([\d.,]+)\s+([\d.,]+)'
    
    print(f"📝 Buscando patrón en texto completo...")
    print(f"🔍 Patrón: '{pattern}'")
    
    matches = re.findall(pattern, full_text, re.IGNORECASE | re.MULTILINE)
    print(f"✅ Matches encontrados: {len(matches)}")
    
    for i, match in enumerate(matches, 1):
        print(f"\n📊 Match {i}:")
        print(f"   Código: {match[0]}")
        print(f"   Descripción: '{match[1]}'")
        print(f"   Cantidad: {match[2]}")
        print(f"   Precio: {match[3]}")
        print(f"   Bonificación: {match[4]}")
        print(f"   Importe bonificación: {match[5]}")
        print(f"   Subtotal: {match[6]}")
    
    if not matches:
        print("❌ No se encontraron matches con el texto completo")
        
        # Buscar el texto específico del item 1
        print("\n🔍 Buscando texto específico del item 1:")
        item1_text = "1 Análisis de datos 4 unidad 4.000,00 12% 1.920,00 14.080,00"
        if item1_text in full_text:
            print(f"✅ Texto del item 1 encontrado en el texto completo")
            
            # Buscar alrededor del texto
            start_pos = full_text.find(item1_text)
            context = full_text[max(0, start_pos-50):start_pos+len(item1_text)+50]
            print(f"📋 Contexto: '{context}'")
            
            # Probar patrón en el contexto
            matches_context = re.findall(pattern, context, re.IGNORECASE | re.MULTILINE)
            print(f"🔍 Matches en contexto: {matches_context}")
        else:
            print(f"❌ Texto del item 1 NO encontrado en el texto completo")

if __name__ == "__main__":
    test_full_text()
