#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.invoice_parser import InvoiceParser
import logging

# Configurar logging para ver los mensajes de debug
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_item_extraction():
    """Prueba la extracción de items con texto de ejemplo"""
    
    parser = InvoiceParser()
    
    # Texto de ejemplo basado en las facturas que recibiste
    text1 = """ORIGINAL Global Networks SRL co0.001 Punto de Venta: 0004 Comp. Nro: 88982595 Razón Social: Global Networks SRL Fecha de Emisión: 27/04/2025 Domicilio Comercial:Calle Salta 600 CUIT: 30-99999999-7 Ingresos Brutos: 26928520538 Condición frente al IVA: Responsable Inscripto Fecha de Inicio de Actividades: 01/01/2020 Período Facturado Desde: 01/01/2025 Hasta: 31/12/2025 Fecha de Vto. para el pago: 30/04/2025 DNI: 20-12345678-9 Apellido y Nombre / Razón Social: María Gonzalez Condición frente al IVA: Responsable Inscripto Domicitio: San Juan 500 Condición de venta: Contado [ Producto / servicio Ju. medida] Precioun [Bont] imp. Bont. Subtotal 1 Servicio de consultoria 1 unidad 10.000,00 14% 1.400,00 8.600,00 2 Desarrollo de software 2 unidad 8.000,00 7% 1.120,00 14.880,00 3 Implementación de red y unidad 5.000,00 14% 2.100,00 12.900,00 Percepción IIBB: $ 1.500,00 IVA: $7.639,80 Subtotal: $36.380,00 Importe Otros Tributos: $265,00 Importe Total: $45.784,80 5165247793596 Fecha de Vto. de CAE: 01/05/2025 Pág. 1/1 Comprobante Autorizado Esta Agencia no se responsabllza poros datos Ingrezados an l dea de a operacion"""

    text2 = """ORIGINAL Network Solutions SA co0.001 Punto de Venta: 0004 Comp. Nro: 33999111 Razón Social: Network Solutions SA Fecha de Emisión: 27/04/2025 Domicilio Comercial:Caballito 400 CUIT: 30-99999999-7 Ingresos Brutos: 20266622664 Condición frente al IVA: Responsable Inscripto Fecha de Inicio de Actividades: 01/01/2020 Período Facturado Desde: 01/01/2025 Hasta: 31/12/2025 Fecha de Vto. para el pago: 30/04/2025 DNI: 20-12345678-9 Apellido y Nombre / Razón Social: Marta Rodriguez Condición frente al IVA: Monotributista Domicilio: Maipú 200 Condición de venta: Contado [ Producto / servicio Ju. medida] Precioun [Bont] imp. Bont. Subtotal 1 Consultoría en IT. 1 unidad 7.500,00 10% 750,00 6.750,00 2 Implementación de red 3 unidad 5.000,00 14% 2.100,00 12.900,00 3 Servicio de consultoria + unidad 10.000,00 7% 700,00 9.300,00 4 Capacitación 1 unidad 5.000,00 19% 950,00 4.050,00 Percepción IIBB: $ 1.500,00 IVA: $6.930,00 Subtotal: $33.000,00 Importe Otros Tributos: $252,00 Importe Total: $41.682,00 ARCA Pág. 1/1 5165247793596 os Fecha de Vto. de CAE: 01/05/2025 Comprobante Autorizado Esta Agencia no se responsabllza poros datos Ingrezados an l dea de a operacion"""

    print("🔍 PROBANDO EXTRACCIÓN DE ITEMS")
    print("=" * 60)
    
    for i, text in enumerate([text1, text2], 1):
        print(f"\n📄 FACTURA {i}:")
        print("-" * 40)
        
        # Extraer items directamente
        items = parser._extract_items(text)
        
        print(f"✅ Items encontrados: {len(items)}")
        
        for j, item in enumerate(items, 1):
            print(f"\n  📦 ITEM {j}:")
            print(f"    Código: {item.get('codigo', 'N/A')}")
            print(f"    Descripción: {item.get('descripcion', 'N/A')}")
            print(f"    Cantidad: {item.get('cantidad', 'N/A')}")
            print(f"    Precio unitario: ${item.get('precio_unitario', 'N/A')}")
            print(f"    Importe bonificación: ${item.get('importe_bonificacion', 'N/A')}")
            print(f"    Subtotal: ${item.get('subtotal', 'N/A')}")
        
        # Probar parsing completo
        print(f"\n🔍 PARSING COMPLETO:")
        result = parser.parse_invoice(text)
        
        if result.get('success'):
            extracted_items = result.get('extracted_fields', {}).get('items', [])
            print(f"  Items en resultado final: {len(extracted_items)}")
            
            for j, item in enumerate(extracted_items, 1):
                print(f"    {j}. {item.get('descripcion', 'N/A')} - ${item.get('precio_unitario', 'N/A')}")
        else:
            print(f"  ❌ Error en parsing: {result.get('error', 'Error desconocido')}")

if __name__ == "__main__":
    test_item_extraction()
