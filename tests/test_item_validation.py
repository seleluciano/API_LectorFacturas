#!/usr/bin/env python3
"""
Test de validación de items
"""

import re

def _is_valid_item(item):
    """Valida que el item tenga información mínima requerida y sea coherente."""
    descripcion = item.get('descripcion', '').strip()
    codigo = item.get('codigo', '').strip()
    cantidad = item.get('cantidad', '').strip()
    precio_unitario = item.get('precio_unitario', '').strip()

    print(f"🔍 Validando item: {item}")
    print(f"   Descripción: '{descripcion}' (longitud: {len(descripcion)})")
    print(f"   Código: '{codigo}'")
    print(f"   Cantidad: '{cantidad}'")
    print(f"   Precio: '{precio_unitario}'")

    # 1. Descripción: No vacía, más de 2 caracteres, no palabras genéricas, no demasiado larga
    if not descripcion or len(descripcion) <= 2:
        print("   ❌ Descripción vacía o muy corta")
        return False
    elif descripcion.lower() in ['unidad', 'item', 'producto', 'servicio', 'cantidad', 'medida', 'precio', 'total', 'bonificación', 'subtotal', 'pág', 'pag']:
        print("   ❌ Descripción es palabra genérica")
        return False
    elif len(descripcion) > 100:
        print("   ❌ Descripción demasiado larga")
        return False
    else:
        print("   ✅ Descripción OK")

    # 2. Código: Debe ser un número simple (1 o 2 dígitos)
    if not re.fullmatch(r'\d{1,2}', codigo):
        print("   ❌ Código no es número simple")
        return False
    else:
        print("   ✅ Código OK")

    # 3. Cantidad: Debe ser un número válido y razonable (entre 1 y 100)
    try:
        cantidad_num = int(cantidad)
        if not (1 <= cantidad_num <= 100):
            print(f"   ❌ Cantidad fuera de rango: {cantidad_num}")
            return False
        else:
            print("   ✅ Cantidad OK")
    except ValueError:
        print("   ❌ Cantidad no es número válido")
        return False

    # 4. Precio Unitario: Debe ser un número válido y mayor que 0
    try:
        # Simular _parse_numeric_value
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
            print(f"   ❌ Precio no es mayor que 0: {precio_num}")
            return False
        else:
            print("   ✅ Precio OK")
    except (ValueError, TypeError):
        print("   ❌ Precio no es número válido")
        return False
    
    print("   ✅ ITEM VÁLIDO")
    return True

def test_item_validation():
    """Test de validación de items"""
    
    print("🧪 TEST DE VALIDACIÓN DE ITEMS")
    print("=" * 60)
    
    # Item 1 (que debería ser válido)
    item1 = {
        'codigo': '1',
        'descripcion': 'Análisis de datos',
        'cantidad': '4',
        'precio_unitario': '4.000,00',
        'importe_bonificacion': '1.920,00',
        'subtotal': '14.080,00'
    }
    
    print("\n📝 Probando Item 1:")
    valid1 = _is_valid_item(item1)
    print(f"Resultado: {'✅ VÁLIDO' if valid1 else '❌ INVÁLIDO'}")
    
    # Item 2 (que sabemos que es válido)
    item2 = {
        'codigo': '2',
        'descripcion': 'Soporte técnico',
        'cantidad': '5',
        'precio_unitario': '2.000,00',
        'importe_bonificacion': '1.100,00',
        'subtotal': '8.900,00'
    }
    
    print("\n📝 Probando Item 2:")
    valid2 = _is_valid_item(item2)
    print(f"Resultado: {'✅ VÁLIDO' if valid2 else '❌ INVÁLIDO'}")

if __name__ == "__main__":
    test_item_validation()
