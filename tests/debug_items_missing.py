#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
from services.invoice_parser import InvoiceParser

def test_items_extraction():
    """Prueba la extracción de items en la factura actual"""
    
    text = """ORIGINAL : A Soluciones Innovadoras SA coo.001 PAGTURA     Punto de Venta: 0004 Comp. Nro: 94565021 Razón Social: Soluciones Innovadoras SA Fecha de Emisión: 27/04/2025 CUIT: 30-99999999-7 Ingresos Brutos: 20575693962 Fecha de Inicio de Actividades: 01/01/2020 Domicilio Comercial:Av. Siempre Viva 742 Condición frente al IVA: Responsable Inscripto             Período Facturado Desde: 01/01/2025 Hasta: 31/12/2025 Fecha de Vto. para el pago: 30/04/2025 DNI: 20-12345678-9 Apellido y Nombre / Razón Social: Pedro Martinez Condición frente al IVA: Responsable Inscripto Domicilio: Palermo 350 Condición de venta: Contado                               [ Producto / servicio Ju. medida] Precioun [Bont] imp. Bont. Subtotal 1 Análisis de datos 4 unidad 4.000,00 19% 3.040,00 12.960,00 2 Capacitación unidad 5.000,00 9% 450,00 4.550,00 3 Implementación de red y unidad 5.000,00 20% 3.000,00 12.000,00   Percepción IIBB: $ 1.500,00 IVA: $6.197,10 Subtotal: $29.510,00 Importe Otros Tributos: $865,00 Importe Total: $38.072,10         5165247793596 Fecha de Vto. de CAE: 01/05/2025   Pág. 1/1   Comprobante Autorizado Esta Agencia no se responsabllza poros datos Ingrezados an l dea de a operacion"""
    
    print("Texto de la factura:")
    print("=" * 80)
    print(text)
    print("=" * 80)
    
    # Crear parser
    parser = InvoiceParser()
    
    # Probar extracción de items
    print("\n🔍 Probando extracción de items:")
    items = parser._extract_items(text)
    print(f"Items encontrados: {len(items)}")
    
    for i, item in enumerate(items, 1):
        print(f"Item {i}: {item}")
    
    # Probar patrones específicos
    print("\n🔍 Probando patrones específicos:")
    
    # Patrón 1: Formato estándar
    pattern1 = r'(\d+)\s+([A-Za-záéíóúñÁÉÍÓÚÑ\s]{3,}?)\s+(\d+)\s+(?:unidad|unidades|u\.|u)\s+([\d.,]+)\s+(\d+%)\s+([\d.,]+)\s+([\d.,]+)(?=\s+\d+\s+[A-Za-z]|\s+Percepción|$)'
    matches1 = re.findall(pattern1, text, re.IGNORECASE | re.MULTILINE)
    print(f"Patrón 1 - Matches: {len(matches1)}")
    for match in matches1:
        print(f"  {match}")
    
    # Patrón 2: Con cantidad implícita
    pattern2 = r'(\d+)\s+([A-Za-záéíóúñÁÉÍÓÚÑ]{3,}\s+[A-Za-záéíóúñÁÉÍÓÚÑ]+)\s+unidad\s+([\d.,]+)\s+(\d+%)\s+([\d.,]+)\s+([\d.,]+)(?=\s+\d+\s+[A-Za-z]|\s+Percepción|$)'
    matches2 = re.findall(pattern2, text, re.IGNORECASE | re.MULTILINE)
    print(f"Patrón 2 - Matches: {len(matches2)}")
    for match in matches2:
        print(f"  {match}")
    
    # Patrón 3: Multiplicación
    pattern3 = r'(\d+)\s+([A-Za-záéíóúñÁÉÍÓÚÑ]{3,}\s+[A-Za-záéíóúñÁÉÍÓÚÑ]+)\s+\$?([\d.,]+)\s*[x×]\s*(\d+)\s*=\s*\$?([\d.,]+)(?=\s+\d+\s+[A-Za-z]|\s+Total|$)'
    matches3 = re.findall(pattern3, text, re.IGNORECASE | re.MULTILINE)
    print(f"Patrón 3 - Matches: {len(matches3)}")
    for match in matches3:
        print(f"  {match}")
    
    # Patrón 4: Formato estructurado
    pattern4 = r'(?:Item\s+)?(\d+)[:\s]+([A-Za-záéíóúñÁÉÍÓÚÑ]{3,}\s+[A-Za-záéíóúñÁÉÍÓÚÑ]+)[\-:]\s*(?:Cantidad|cant\.|qty\.?)[:\s]*(\d+)[\-:]\s*(?:Precio|price|prec\.?)[:\s]*\$?([\d.,]+)(?=\s+\d+\s+[A-Za-z]|\s+Total|$)'
    matches4 = re.findall(pattern4, text, re.IGNORECASE | re.MULTILINE)
    print(f"Patrón 4 - Matches: {len(matches4)}")
    for match in matches4:
        print(f"  {match}")
    
    # Buscar la sección de items específicamente
    print("\n🔍 Buscando sección de items:")
    items_section = re.search(r'\[ Producto / servicio.*?Percepción IIBB', text, re.DOTALL)
    if items_section:
        section_text = items_section.group(0)
        print("Sección encontrada:")
        print(section_text)
        
        # Buscar números de línea
        line_numbers = re.findall(r'^\s*(\d+)\s+([A-Za-záéíóúñÁÉÍÓÚÑ\s]+?)\s+(\d+)?\s*unidad\s+([\d.,]+)\s+(\d+%)\s+([\d.,]+)\s+([\d.,]+)', section_text, re.MULTILINE)
        print(f"\nLíneas encontradas: {len(line_numbers)}")
        for line in line_numbers:
            print(f"  {line}")
    else:
        print("No se encontró la sección de items")
    
    # Probar parsing completo
    print("\n🔍 Probando parsing completo:")
    result = parser.parse_multiple_invoices(text)
    print(f"Facturas encontradas: {result.get('total_invoices', 0)}")
    
    for invoice in result.get('invoices', []):
        fields = invoice.get('extracted_fields', {})
        items = fields.get('items', [])
        print(f"Items en la factura: {len(items)}")
        for i, item in enumerate(items, 1):
            print(f"  Item {i}: {item}")

if __name__ == "__main__":
    test_items_extraction()
