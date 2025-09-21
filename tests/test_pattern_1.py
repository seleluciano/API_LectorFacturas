#!/usr/bin/env python3
"""
Test específico para el patrón 1
"""

import re

def test_pattern_1():
    """Test del patrón principal"""
    
    text = "1 Análisis de datos 4 unidad 4.000,00 12% 1.920,00 14.080,00"
    
    # Patrón 1: código descripción cantidad unidad precio % bonificación importe_bonificación subtotal
    pattern = r'(\d+)\s+([A-Za-záéíóúñÁÉÍÓÚÑ\s\-\.]{3,}?)\s+(\d+)\s+unidad\s+([\d.,]+)\s+(\d+%)\s+([\d.,]+)\s+([\d.,]+)'
    
    print(f"📝 Texto: '{text}'")
    print(f"🔍 Patrón: '{pattern}'")
    
    matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
    print(f"✅ Matches encontrados: {matches}")
    
    if matches:
        match = matches[0]
        print(f"📊 Match: {match}")
        print(f"   Código: {match[0]}")
        print(f"   Descripción: {match[1]}")
        print(f"   Cantidad: {match[2]}")
        print(f"   Precio: {match[3]}")
        print(f"   Bonificación: {match[4]}")
        print(f"   Importe bonificación: {match[5]}")
        print(f"   Subtotal: {match[6]}")
    else:
        print("❌ No se encontraron matches")
        
        # Probar variaciones del patrón
        print("\n🔍 Probando variaciones:")
        
        # Sin el ? en la descripción
        pattern2 = r'(\d+)\s+([A-Za-záéíóúñÁÉÍÓÚÑ\s\-\.]{3,})\s+(\d+)\s+unidad\s+([\d.,]+)\s+(\d+%)\s+([\d.,]+)\s+([\d.,]+)'
        matches2 = re.findall(pattern2, text, re.IGNORECASE | re.MULTILINE)
        print(f"   Patrón sin ?: {matches2}")
        
        # Con más flexibilidad en la descripción
        pattern3 = r'(\d+)\s+([A-Za-záéíóúñÁÉÍÓÚÑ\s\-\.]+?)\s+(\d+)\s+unidad\s+([\d.,]+)\s+(\d+%)\s+([\d.,]+)\s+([\d.,]+)'
        matches3 = re.findall(pattern3, text, re.IGNORECASE | re.MULTILINE)
        print(f"   Patrón más flexible: {matches3}")

if __name__ == "__main__":
    test_pattern_1()
