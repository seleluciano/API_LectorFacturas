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

def test_null_fields():
    """Prueba específicamente los campos que estaban en null"""
    
    parser = InvoiceParser()
    
    # Textos de las facturas reales
    text1 = """ORIGINAL Global Networks SRL co0.001 Punto de Venta: 0004 Comp. Nro: 88982595 Razón Social: Global Networks SRL Fecha de Emisión: 27/04/2025 Domicilio Comercial:Calle Salta 600 CUIT: 30-99999999-7 Ingresos Brutos: 26928520538 Condición frente al IVA: Responsable Inscripto Fecha de Inicio de Actividades: 01/01/2020 Período Facturado Desde: 01/01/2025 Hasta: 31/12/2025 Fecha de Vto. para el pago: 30/04/2025 DNI: 20-12345678-9 Apellido y Nombre / Razón Social: María Gonzalez Condición frente al IVA: Responsable Inscripto Domicitio: San Juan 500 Condición de venta: Contado [ Producto / servicio Ju. medida] Precioun [Bont] imp. Bont. Subtotal 1 Servicio de consultoria 1 unidad 10.000,00 14% 1.400,00 8.600,00 2 Desarrollo de software 2 unidad 8.000,00 7% 1.120,00 14.880,00 3 Implementación de red y unidad 5.000,00 14% 2.100,00 12.900,00 Percepción IIBB: $ 1.500,00 IVA: $7.639,80 Subtotal: $36.380,00 Importe Otros Tributos: $265,00 Importe Total: $45.784,80 5165247793596 Fecha de Vto. de CAE: 01/05/2025 Pág. 1/1 Comprobante Autorizado Esta Agencia no se responsabllza poros datos Ingrezados an l dea de a operacion"""

    print("🔍 PROBANDO CAMPOS QUE ESTABAN EN NULL")
    print("=" * 60)
    
    for i, text in enumerate([text1], 1):
        print(f"\n📄 FACTURA {i}:")
        print("-" * 40)
        
        # Probar extracción específica de campos problemáticos
        print("🎯 PROBANDO TIPO_FACTURA:")
        tipo_factura = parser._extract_field(text, parser.patterns['tipo_factura'], 'tipo_factura')
        print(f"   Resultado: '{tipo_factura}'")
        
        print("\n🎯 PROBANDO CONDICION_VENTA:")
        condicion_venta = parser._extract_field(text, parser.patterns['condicion_venta'], 'condicion_venta')
        print(f"   Resultado: '{condicion_venta}'")
        
        # Probar parsing completo
        print(f"\n🔍 PARSING COMPLETO:")
        result = parser.parse_invoice(text)
        
        if result.get('success'):
            fields = result.get('extracted_fields', {})
            print(f"   tipo_factura: '{fields.get('tipo_factura', 'NULL')}'")
            print(f"   condicion_venta: '{fields.get('condicion_venta', 'NULL')}'")
            
            # Mostrar todos los campos para verificar
            print(f"\n📋 TODOS LOS CAMPOS:")
            for key, value in fields.items():
                if value is None:
                    print(f"   ❌ {key}: NULL")
                else:
                    print(f"   ✅ {key}: {value}")
        else:
            print(f"   ❌ Error en parsing: {result.get('error', 'Error desconocido')}")

if __name__ == "__main__":
    test_null_fields()
