#!/usr/bin/env python3
"""
Test completo del flujo de extracción de items
"""

import re

def _clean_item_description(description):
    """Limpia la descripción del item con mejoras genéricas para OCR"""
    # Limpiar espacios múltiples
    description = re.sub(r'\s+', ' ', description).strip()
    
    # PRIMERO: Separar palabras pegadas (problema principal identificado)
    description = _separate_joined_words(description)
    
    # Correcciones genéricas para errores OCR comunes (sin ser específicas de empresa)
    generic_ocr_fixes = {
        # Caracteres comúnmente confundidos
        r'\b0\b': 'o',  # 0 -> o cuando está solo
        r'\bo\b': '0',  # o -> 0 cuando está solo
        r'\bl\b': '1',  # l -> 1 cuando está solo
        r'\b1\b': 'l',  # 1 -> l cuando está solo
    }
    
    # Aplicar correcciones genéricas
    for pattern, replacement in generic_ocr_fixes.items():
        description = re.sub(pattern, replacement, description, flags=re.IGNORECASE)

    # Unir palabras compuestas que el OCR pudo haber separado incorrectamente
    description = re.sub(r'\b(soporte)\s+(tecnico)\b', r'\1\2', description, flags=re.IGNORECASE)
    description = re.sub(r'\b(mantenimiento)\s+(mensual)\b', r'\1\2', description, flags=re.IGNORECASE)
    description = re.sub(r'\b(licencia)\s+(software)\b', r'\1\2', description, flags=re.IGNORECASE)
    description = re.sub(r'\b(implementacion)\s+(red)\b', r'\1\2', description, flags=re.IGNORECASE)
    description = re.sub(r'\b(servicio)\s+(consultoria)\b', r'\1\2', description, flags=re.IGNORECASE)

    return description

def _separate_joined_words(text):
    """Intenta separar palabras que el OCR pudo haber pegado incorrectamente."""
    # Patrones específicos para palabras compuestas comunes en facturas
    specific_separations = {
        r'(?i)(soportetecnico)': 'Soporte técnico',
        r'(?i)(mantenimientomensual)': 'Mantenimiento mensual',
        r'(?i)(licenciasoftware)': 'Licencia software',
        r'(?i)(implementaciondered)': 'Implementación de red',
        r'(?i)(implementacionred)': 'Implementación red',
        r'(?i)(serviciodeconsultoria)': 'Servicio de consultoría',
        r'(?i)(servicioconsultoria)': 'Servicio consultoría',
        r'(?i)(instalaciondeservidores)': 'Instalación de servidores',
        r'(?i)(capacitacion)': 'Capacitación', # Para corregir acentos si se pegó
    }

    for pattern, replacement in specific_separations.items():
        text = re.sub(pattern, replacement, text)

    # Patrón genérico para separar palabras cuando una minúscula es seguida por una mayúscula
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
    
    return text

def _process_item_match_generic(match, pattern_idx):
    """Procesa un match de item según el patrón usado"""
    try:
        if pattern_idx == 0:  # Patrón completo con todos los campos
            return {
                'codigo': match[0],
                'descripcion': _clean_item_description(match[1]),
                'cantidad': match[2],
                'unidad_medida': 'unidad',
                'precio_unitario': match[3],
                'importe_bonificacion': match[5],
                'subtotal': match[6]
            }
        # ... otros patrones
    except (ValueError, IndexError) as e:
        print(f"Error procesando item match: {e}")
        return None
    
    return None

def _is_valid_item(item):
    """Valida que el item tenga información mínima requerida y sea coherente."""
    descripcion = item.get('descripcion', '').strip()
    codigo = item.get('codigo', '').strip()
    cantidad = item.get('cantidad', '').strip()
    precio_unitario = item.get('precio_unitario', '').strip()

    # 1. Descripción: No vacía, más de 2 caracteres, no palabras genéricas, no demasiado larga
    if not descripcion or len(descripcion) <= 2 or \
       descripcion.lower() in ['unidad', 'item', 'producto', 'servicio', 'cantidad', 'medida', 'precio', 'total', 'bonificación', 'subtotal', 'pág', 'pag'] or \
       len(descripcion) > 100:
        return False

    # 2. Código: Debe ser un número simple (1 o 2 dígitos)
    if not re.fullmatch(r'\d{1,2}', codigo):
        return False

    # 3. Cantidad: Debe ser un número válido y razonable (entre 1 y 100)
    try:
        cantidad_num = int(cantidad)
        if not (1 <= cantidad_num <= 100):
            return False
    except ValueError:
        return False

    # 4. Precio Unitario: Debe ser un número válido y mayor que 0
    try:
        precio_clean = re.sub(r'[^\d.,]', '', precio_unitario)
        if ',' in precio_clean and '.' in precio_clean:
            parts = precio_clean.split(',')
            if len(parts) == 2:
                integer_part = parts[0].replace('.', '')
                decimal_part = parts[1][:2]
                precio_num = float(f"{integer_part}.{decimal_part}")
            else:
                precio_num = float(precio_clean.replace(',', '.'))
        elif ',' in precio_clean:
            precio_num = float(precio_clean.replace(',', '.'))
        else:
            precio_num = float(precio_clean)
        
        if not (precio_num > 0):
            return False
    except (ValueError, TypeError):
        return False
    
    return True

def test_complete_flow():
    """Test del flujo completo de extracción"""
    
    print("🧪 TEST DEL FLUJO COMPLETO DE EXTRACCIÓN")
    print("=" * 60)
    
    # Texto completo
    full_text = """ORIGINAL Global Solutions SA oat | FACTURA Razón Social: Global Solutions SA         Punto de Venta: 0004 Comp.Nro: 47342647 Fecha de Emisión: 27/04/2025            CUIT: 30-99999999-7 Ingresos Brutos: Fecha de Inicio de Actividades: Domicilio Comercial:     Condición frente al IVA:         Período Facturado Desde: Hasta: Fecha de Vto. para el pago: DNI: 20-12345678-9 Apellido y Nombre / Razón Social: Alvaro Fernandez Condición frente al IVA: Responsable Inscripto Domiclio: Condicién de venta: Contado                               [ Producto / Servicio — [u. — preciount [ont] imp. Bont. Subtotal 1 Análisis de datos 4 unidad 4.000,00 12% 1.920,00 14.080,00 2 Soporte técnico 5 unidad 2.000,00 11% 1.100,00 8.900,00 3 Mantenimiento mensual y unidad 1.500,00 11% 495,00 4.005,00   Percepción IIBB: $ 1.500,00 IVA: Subtotal: $26.985,00 Importe Otros Tributos: $ Importe Total: $34.354,85             5165247793596 Fecha de Vto. de CAE: 01/05/2025 Pág. 1/1   Comprobante Autorizado Esta Agencia no se responsabllza poros datos Ingrezados an l dea de a operacion"""
    
    # Patrón 1
    pattern = r'(\d+)\s+([A-Za-záéíóúñÁÉÍÓÚÑ\s\-\.]{3,}?)\s+(\d+)\s+unidad\s+([\d.,]+)\s+(\d+%)\s+([\d.,]+)\s+([\d.,]+)'
    
    print("🔍 Buscando matches...")
    matches = re.findall(pattern, full_text, re.IGNORECASE | re.MULTILINE)
    print(f"✅ Matches encontrados: {len(matches)}")
    
    items = []
    items_by_code = {}
    
    for i, match in enumerate(matches):
        print(f"\n📝 Procesando match {i+1}: {match}")
        
        item = _process_item_match_generic(match, 0)
        if item:
            print(f"✅ Item procesado: {item}")
            
            if _is_valid_item(item):
                print(f"✅ Item válido")
                codigo = item['codigo']
                
                if codigo not in items_by_code:
                    items_by_code[codigo] = item
                    items.append(item)
                    print(f"✅ Item agregado")
                else:
                    print(f"⚠️ Item duplicado, código {codigo} ya existe")
            else:
                print(f"❌ Item no válido")
        else:
            print(f"❌ No se pudo procesar el match")
    
    print(f"\n📊 RESULTADO FINAL:")
    print(f"Total items extraídos: {len(items)}")
    for i, item in enumerate(items, 1):
        print(f"  {i}. Código: {item['codigo']}, Descripción: {item['descripcion']}")

if __name__ == "__main__":
    test_complete_flow()
