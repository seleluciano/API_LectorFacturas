#!/usr/bin/env python3
"""
Script para probar ambos formatos de números
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.invoice_parser import InvoiceParser

def test_number_formats():
    """Probar diferentes formatos de números"""
    
    print("🧪 Probando Diferentes Formatos de Números")
    print("=" * 50)
    
    # Crear parser
    parser = InvoiceParser()
    
    # Función para convertir cualquier formato a float (corregida)
    def parse_number(number_str):
        number_str = number_str.strip()
        
        if '.' in number_str and ',' in number_str:
            # Tiene ambos separadores
            # Determinar cuál es el separador decimal
            last_dot = number_str.rfind('.')
            last_comma = number_str.rfind(',')
            
            if last_comma > last_dot:
                # Coma está después del último punto: 26.667,60 (formato argentino)
                return float(number_str.replace('.', '').replace(',', '.'))
            else:
                # Punto está después de la última coma: 26,667.60 (formato americano)
                return float(number_str.replace(',', ''))
        elif ',' in number_str:
            # Solo coma: 26667,60 (formato argentino)
            return float(number_str.replace(',', '.'))
        elif '.' in number_str:
            # Solo punto: 26667.60 (formato americano)
            return float(number_str)
        else:
            # Sin separadores: 26667
            return float(number_str)
    
    # Casos de prueba
    test_cases = [
        ("26.667,60", "Formato argentino"),
        ("26,667.60", "Formato americano"),
        ("26667,60", "Formato argentino sin separador de miles"),
        ("26667.60", "Formato americano sin separador de miles"),
        ("26667", "Sin separadores"),
        ("1.234.567,89", "Formato argentino grandes números"),
        ("1,234,567.89", "Formato americano grandes números")
    ]
    
    print("📊 PRUEBAS DE FORMATOS:")
    for test_value, description in test_cases:
        try:
            result = parse_number(test_value)
            print(f"  ✅ {test_value:15} ({description:30}) -> {result}")
        except Exception as e:
            print(f"  ❌ {test_value:15} ({description:30}) -> Error: {e}")
    
    print("\n🧮 PRUEBA DE CÁLCULO:")
    
    # Probar cálculo con formato argentino
    print("\n📈 Formato Argentino:")
    argentino_total = parse_number("26.667,60")
    argentino_subtotal = parse_number("20.360,00")
    deuda_argentina = argentino_total - argentino_subtotal
    print(f"  {argentino_total} - {argentino_subtotal} = {deuda_argentina}")
    
    # Probar cálculo con formato americano
    print("\n📈 Formato Americano:")
    americano_total = parse_number("26,667.60")
    americano_subtotal = parse_number("20,360.00")
    deuda_americana = americano_total - americano_subtotal
    print(f"  {americano_total} - {americano_subtotal} = {deuda_americana}")
    
    # Verificar que ambos dan el mismo resultado
    if abs(deuda_argentina - deuda_americana) < 0.01:
        print("✅ Ambos formatos dan el mismo resultado!")
    else:
        print("❌ Los formatos dan resultados diferentes!")

if __name__ == "__main__":
    test_number_formats()

