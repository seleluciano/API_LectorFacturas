"""
Script para probar las mejoras implementadas en el sistema de métricas
"""
import sys
from pathlib import Path

# Agregar el directorio actual al path
sys.path.append(str(Path(__file__).parent))

from services.metrics_calculator import MetricsCalculator

def test_improvements():
    """Prueba las mejoras implementadas en el sistema de métricas"""
    
    print("🧪 PROBANDO MEJORAS DEL SISTEMA DE MÉTRICAS")
    print("=" * 60)
    
    # Crear calculadora de métricas
    calculator = MetricsCalculator()
    
    # Datos de prueba con campos faltantes e inconsistentes
    extracted_fields = {
        'cuit_vendedor': '30-99999999-7',
        'cuit_comprador': '20-12345678-9',
        'fecha_emision': '27/04/2025',
        'subtotal': '34.130,00',
        'importe_total': '43.239,30',
        # Campos faltantes que deberían corregirse
        # 'punto_venta': faltante
        # 'tipo_factura': faltante
        'productos': [
            {
                'descripcion': '  Soporte técnico  ',  # Con espacios extra
                'cantidad': 5,
                'precio_unitario': 2000,
                'bonificacion': 15,
                # 'importe_bonificacion': faltante (debería calcularse)
            },
            {
                'descripcion': 'Licencia software',
                'cantidad': 2,
                'precio_unitario': 3000,
                'bonificacion': 7,
                'importe_bonificacion': 210.0
            }
        ]
    }
    
    ground_truth = {
        'cuit_vendedor': '30-99999999-7',
        'cuit_comprador': '20-12345678-9',
        'fecha_emision': '27/04/2025',
        'subtotal': '34.130,00',
        'importe_total': '43.239,30',
        'punto_venta': '0004',
        'tipo_factura': 'A',
        'productos': [
            {
                'descripcion': 'Soporte técnico',
                'cantidad': 5,
                'precio_unitario': 2000,
                'bonificacion': 15,
                'importe_bonificacion': 300.0
            },
            {
                'descripcion': 'Licencia software',
                'cantidad': 2,
                'precio_unitario': 3000,
                'bonificacion': 7,
                'importe_bonificacion': 210.0
            }
        ]
    }
    
    # Texto de prueba con formato inconsistente
    extracted_text = "ORIGINAL A Digital Future Ltda  34.130,00  43.239,30  CUIT: 30-99999999-7"
    ground_truth_text = "ORIGINAL A Digital Future Ltda 34.130,00 43.239,30 CUIT: 30-99999999-7"
    
    print("\n📊 1. PROBANDO CORRECCIÓN DE CAMPOS FALTANTES")
    print("-" * 50)
    
    # Aplicar correcciones
    corrected_fields = calculator.correct_missing_fields(extracted_fields)
    
    print("Campos corregidos:")
    print(f"  punto_venta: {corrected_fields.get('punto_venta', 'FALTANTE')}")
    print(f"  tipo_factura: {corrected_fields.get('tipo_factura', 'FALTANTE')}")
    
    # Verificar cálculo de importe_bonificacion
    if corrected_fields.get('productos'):
        for i, item in enumerate(corrected_fields['productos']):
            print(f"  Item {i+1} - importe_bonificacion: {item.get('importe_bonificacion', 'FALTANTE')}")
            print(f"  Item {i+1} - descripcion limpia: '{item.get('descripcion', '')}'")
    
    print("\n🎯 2. PROBANDO CÁLCULO DE CONFIANZA MEJORADO")
    print("-" * 50)
    
    # Calcular confianza con campos originales
    confidence_original = calculator.calculate_confidence_score(extracted_fields)
    print(f"Confianza con campos originales: {confidence_original:.3f}")
    
    # Calcular confianza con campos corregidos
    confidence_corrected = calculator.calculate_confidence_score(corrected_fields)
    print(f"Confianza con campos corregidos: {confidence_corrected:.3f}")
    
    print("\n📈 3. PROBANDO CÁLCULO DE ACCURACY")
    print("-" * 50)
    
    # Calcular accuracy
    accuracy, details = calculator.calculate_field_accuracy(corrected_fields, ground_truth)
    print(f"Accuracy total: {accuracy:.3f}")
    print(f"Campos correctos: {details['correct_fields']}")
    print(f"Campos faltantes: {details['missing_fields']}")
    print(f"Campos incorrectos: {details['incorrect_fields']}")
    
    print("\n📝 4. PROBANDO LIMPIEZA DE TEXTO (CER/WER)")
    print("-" * 50)
    
    # Calcular CER y WER
    cer = calculator.calculate_cer(extracted_text, ground_truth_text)
    wer = calculator.calculate_wer(extracted_text, ground_truth_text)
    
    print(f"CER (Character Error Rate): {cer:.3f}")
    print(f"WER (Word Error Rate): {wer:.3f}")
    
    # Probar con texto limpio
    cleaned_extracted = calculator._clean_string_field(extracted_text)
    cleaned_ground_truth = calculator._clean_string_field(ground_truth_text)
    
    print(f"\nTexto extraído limpio: '{cleaned_extracted}'")
    print(f"Texto ground truth limpio: '{cleaned_ground_truth}'")
    
    cer_cleaned = calculator.calculate_cer(cleaned_extracted, cleaned_ground_truth)
    wer_cleaned = calculator.calculate_wer(cleaned_extracted, cleaned_ground_truth)
    
    print(f"CER con texto limpio: {cer_cleaned:.3f}")
    print(f"WER con texto limpio: {wer_cleaned:.3f}")
    
    print("\n🚀 5. PROBANDO MÉTRICAS COMPREHENSIVAS")
    print("-" * 50)
    
    # Calcular métricas comprehensivas
    metrics = calculator.calculate_comprehensive_metrics(
        extracted_fields=extracted_fields,
        ground_truth=ground_truth,
        extracted_text=extracted_text,
        ground_truth_text=ground_truth_text,
        processing_time=2.5
    )
    
    print(f"Confidence Score: {metrics.confidence_score:.3f}")
    print(f"Field Accuracy: {metrics.field_accuracy:.3f}")
    print(f"CER: {metrics.cer:.3f}")
    print(f"WER: {metrics.wer:.3f}")
    print(f"Throughput: {metrics.throughput:.2f} docs/seg")
    
    print("\n✅ RESUMEN DE MEJORAS:")
    print("-" * 50)
    print("✓ Confianza calculada solo sobre campos importantes")
    print("✓ Campos faltantes corregidos automáticamente")
    print("✓ Cálculo automático de importe_bonificacion")
    print("✓ Limpieza de texto para reducir CER/WER")
    print("✓ Normalización de montos (formato argentino)")
    print("✓ Métricas comprehensivas mejoradas")

if __name__ == "__main__":
    test_improvements()
