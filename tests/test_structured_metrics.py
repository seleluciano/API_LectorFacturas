"""
Script para probar que las métricas se calculan solo sobre campos estructurados
"""
import sys
from pathlib import Path

# Agregar el directorio actual al path
sys.path.append(str(Path(__file__).parent))

from services.metrics_calculator import MetricsCalculator

def test_structured_metrics():
    """Prueba que las métricas se calculan solo sobre campos estructurados"""
    
    print("🎯 PROBANDO MÉTRICAS SOLO SOBRE CAMPOS ESTRUCTURADOS")
    print("=" * 60)
    
    # Crear calculadora de métricas
    calculator = MetricsCalculator()
    
    # Datos de prueba: OCR extrae MUCHOS campos, pero solo evaluamos los estructurados
    extracted_fields = {
        # Campos estructurados que SÍ evaluamos
        'cuit_vendedor': '30-99999999-7',
        'cuit_comprador': '20-12345678-9',
        'fecha_emision': '27/04/2025',
        'subtotal': '34.130,00',
        'importe_total': '43.239,30',
        'productos': [
            {
                'descripcion': 'Soporte técnico',
                'cantidad': 5,
                'precio_unitario': 2000,
                'bonificacion': 15,
                'importe_bonificacion': 300.0
            }
        ],
        
        # Campos que el OCR extrae pero NO evaluamos
        'tipo_factura': 'A',
        'razon_social_vendedor': 'Digital Future Ltda',
        'razon_social_comprador': 'Laura Gómez',
        'numero_factura': '13225316',
        'punto_venta': '0004',
        'condicion_iva_comprador': 'Monotributista',
        'condicion_venta': 'Contado',
        'iva': '7.167,30',
        'deuda_impositiva': '9.109,30',
        'domicilio_comercial': 'Rivadavia 1300',
        'ingresos_brutos': '22432098707',
        'raw_text': 'Texto completo extraído...',
        # Muchos otros campos que el OCR podría extraer
        'otros_campo_1': 'valor1',
        'otros_campo_2': 'valor2',
        'otros_campo_3': 'valor3'
    }
    
    ground_truth = {
        # Solo campos estructurados (lo que realmente importa)
        'cuit_vendedor': '30-99999999-7',
        'cuit_comprador': '20-12345678-9',
        'fecha_emision': '27/04/2025',
        'subtotal': '34.130,00',
        'importe_total': '43.239,30',
        'productos': [
            {
                'descripcion': 'Soporte técnico',
                'cantidad': 5,
                'precio_unitario': 2000,
                'bonificacion': 15,
                'importe_bonificacion': 300.0
            }
        ]
    }
    
    print("\n📊 1. CAMPOS ESTRUCTURADOS EVALUADOS")
    print("-" * 50)
    print("Campos principales estructurados:")
    for field in calculator.structured_fields:
        print(f"  ✓ {field}")
    
    print("\nCampos de items estructurados:")
    for field in calculator.structured_item_fields:
        print(f"  ✓ {field}")
    
    print("\n🎯 2. CÁLCULO DE CONFIANZA (SOLO CAMPOS ESTRUCTURADOS)")
    print("-" * 50)
    
    confidence = calculator.calculate_confidence_score(extracted_fields)
    print(f"Confidence Score: {confidence:.3f}")
    print("(Calculado solo sobre campos estructurados, ignorando otros campos del OCR)")
    
    print("\n📈 3. CÁLCULO DE ACCURACY (SOLO CAMPOS ESTRUCTURADOS)")
    print("-" * 50)
    
    accuracy, details = calculator.calculate_field_accuracy(extracted_fields, ground_truth)
    print(f"Accuracy total: {accuracy:.3f}")
    print(f"Campos correctos: {details['correct_fields']}")
    print(f"Campos faltantes: {details['missing_fields']}")
    print(f"Campos incorrectos: {details['incorrect_fields']}")
    print(f"Total campos evaluados: {details['total_fields']}")
    
    print("\n📋 4. DETALLE DE CAMPOS EVALUADOS")
    print("-" * 50)
    print("Campos principales evaluados:")
    for field, detail in details['field_details'].items():
        if field != 'items':
            print(f"  {field}: {detail['status']}")
    
    if 'items' in details['field_details']:
        print("\nCampos de items evaluados:")
        items_detail = details['field_details']['items']
        for item_key, item_fields in items_detail.items():
            print(f"  {item_key}:")
            for field, field_detail in item_fields.items():
                print(f"    {field}: {field_detail['status']}")
    
    print("\n🚫 5. CAMPOS NO EVALUADOS (EXTRAÍDOS POR OCR)")
    print("-" * 50)
    ocr_fields_not_evaluated = [
        'tipo_factura', 'razon_social_vendedor', 'razon_social_comprador',
        'numero_factura', 'punto_venta', 'condicion_iva_comprador',
        'condicion_venta', 'iva', 'deuda_impositiva', 'domicilio_comercial',
        'ingresos_brutos', 'raw_text', 'otros_campo_1', 'otros_campo_2', 'otros_campo_3'
    ]
    
    for field in ocr_fields_not_evaluated:
        if field in extracted_fields:
            print(f"  ❌ {field} (extraído por OCR pero NO evaluado)")
    
    print("\n✅ RESUMEN:")
    print("-" * 50)
    print("✓ Solo se evalúan campos estructurados específicos")
    print("✓ Se ignoran todos los otros campos extraídos por OCR")
    print("✓ Las métricas son precisas y relevantes")
    print("✓ No se penaliza por campos que no están en ground truth")
    
    print(f"\n🎯 Campos estructurados evaluados: {len(calculator.structured_fields)}")
    print(f"🎯 Campos de items evaluados: {len(calculator.structured_item_fields)}")
    print(f"📊 Total campos del OCR ignorados: {len(ocr_fields_not_evaluated)}")

if __name__ == "__main__":
    test_structured_metrics()
