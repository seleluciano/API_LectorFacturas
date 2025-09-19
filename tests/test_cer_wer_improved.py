"""
Script para probar CER/WER mejorado: solo campos importantes con normalización completa
"""
import sys
from pathlib import Path

# Agregar el directorio actual al path
sys.path.append(str(Path(__file__).parent))

from services.metrics_calculator import MetricsCalculator

def test_cer_wer_improved():
    """Prueba CER/WER mejorado con solo campos importantes y normalización completa"""
    
    print("🎯 PROBANDO CER/WER MEJORADO - SOLO CAMPOS IMPORTANTES")
    print("=" * 60)
    
    # Crear calculadora de métricas
    calculator = MetricsCalculator()
    
    # Texto extraído por OCR (con errores y campos irrelevantes)
    extracted_text = """
    ORIGINAL A Digital Future Ltda Le PAGTURA Punto de Venta: 0004
    Comp. Nro: 13225316 Fecha de Emisión: 27/04/2025
    CUIT: 30-99999999-7 Ingresos Brutos: 22432098707
    Inicio de Actividades: 01/01/2020
    DNI: 20-12345678-9 Apellido y Nombre / Razón Social: Laura Gómez
    Domicilio: Cabildo 1000 Condición frente al IVA: Monotributista
    Condición de venta: Contado
    
    1 Soporte técnico 5 unidad 2000,00 15% 300,00 9700,00
    2 Licencia software 2 unidad 3000,00 7% 210,00 5790,00
    
    Subtotal: 34.130,00
    Importe Otros: 442,00
    IVA: 7.167,30
    Percepción IIBB: 1.500,00
    Importe Total: 43.239,30
    
    Otros datos irrelevantes: ABC123 XYZ789
    """
    
    # Texto ground truth (correcto)
    ground_truth_text = """
    ORIGINAL A Digital Future Ltda Le PAGTURA Punto de Venta: 0004
    Comp. Nro: 13225316 Fecha de Emisión: 27/04/2025
    CUIT: 30-99999999-7 Ingresos Brutos: 22432098707
    Inicio de Actividades: 01/01/2020
    DNI: 20-12345678-9 Apellido y Nombre / Razón Social: Laura Gómez
    Domicilio: Cabildo 1000 Condición frente al IVA: Monotributista
    Condición de venta: Contado
    
    1 Soporte técnico 5 unidad 2000,00 15% 300,00 9700,00
    2 Licencia software 2 unidad 3000,00 7% 210,00 5790,00
    
    Subtotal: 34.130,00
    Importe Otros: 442,00
    IVA: 7.167,30
    Percepción IIBB: 1.500,00
    Importe Total: 43.239,30
    """
    
    print("\n📝 1. TEXTO EXTRAÍDO (CON ERRORES Y CAMPOS IRRELEVANTES)")
    print("-" * 60)
    print(extracted_text[:200] + "...")
    
    print("\n📝 2. TEXTO GROUND TRUTH (CORRECTO)")
    print("-" * 60)
    print(ground_truth_text[:200] + "...")
    
    print("\n🔍 3. EXTRACCIÓN DE CAMPOS IMPORTANTES")
    print("-" * 60)
    
    # Extraer solo campos importantes
    extracted_important = calculator._extract_important_fields_text(extracted_text)
    ground_truth_important = calculator._extract_important_fields_text(ground_truth_text)
    
    print("Campos importantes extraídos (OCR):")
    print(f"  '{extracted_important}'")
    print("\nCampos importantes extraídos (Ground Truth):")
    print(f"  '{ground_truth_important}'")
    
    print("\n🔧 4. NORMALIZACIÓN COMPLETA")
    print("-" * 60)
    
    # Normalizar completamente
    extracted_normalized = calculator._normalize_text_completely(extracted_important)
    ground_truth_normalized = calculator._normalize_text_completely(ground_truth_important)
    
    print("Texto normalizado (OCR):")
    print(f"  '{extracted_normalized}'")
    print("\nTexto normalizado (Ground Truth):")
    print(f"  '{ground_truth_normalized}'")
    
    print("\n📊 5. CÁLCULO DE CER/WER MEJORADO")
    print("-" * 60)
    
    # Calcular CER/WER con el método mejorado
    cer = calculator.calculate_cer(extracted_text, ground_truth_text)
    wer = calculator.calculate_wer(extracted_text, ground_truth_text)
    
    print(f"CER (Character Error Rate): {cer:.3f}")
    print(f"WER (Word Error Rate): {wer:.3f}")
    
    print("\n✅ 6. BENEFICIOS DEL CER/WER MEJORADO")
    print("-" * 60)
    print("✓ Solo evalúa campos importantes (estructurados)")
    print("✓ Ignora campos irrelevantes extraídos por OCR")
    print("✓ Normalización completa: minúsculas, sin comas/puntos, sin espacios extra")
    print("✓ Más preciso y relevante para evaluación del modelo")
    print("✓ No penaliza por texto irrelevante")
    
    print(f"\n🎯 Campos evaluados: {len(extracted_important.split())} elementos importantes")
    print(f"📊 CER perfecto: {cer:.3f} (0.000 = sin errores)")
    print(f"📊 WER perfecto: {wer:.3f} (0.000 = sin errores)")


if __name__ == "__main__":
    test_cer_wer_improved()
