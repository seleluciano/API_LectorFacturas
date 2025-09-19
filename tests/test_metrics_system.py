"""
Script de prueba para demostrar el funcionamiento del sistema de métricas
"""
import os
import sys
import json
import logging
from pathlib import Path

# Agregar el directorio actual al path
sys.path.append(str(Path(__file__).parent))

from services.metrics_calculator import MetricsCalculator, MetricsResult
from services.batch_processor import BatchProcessor

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_metrics_calculator():
    """Prueba el calculador de métricas con datos de ejemplo"""
    print("Probando MetricsCalculator...")
    
    calculator = MetricsCalculator()
    
    # Datos de ejemplo - campos extraídos por el modelo
    extracted_fields = {
        'tipo_factura': 'A',
        'razon_social_vendedor': 'Empresa Ejemplo SRL',
        'cuit_vendedor': '20-12345678-9',
        'razon_social_comprador': 'Cliente Ejemplo',
        'cuit_comprador': '20-87654321-0',
        'condicion_iva_comprador': 'Responsable Inscripto',
        'condicion_venta': 'Contado',
        'fecha_emision': '01/01/2024',
        'subtotal': '1000,00',
        'importe_total': '1210,00',
        'iva': '210,00',
        'deuda_impositiva': '210,00',
        'numero_factura': '0001-00000001',
        'punto_venta': '0001',
        'items': [
            {
                'codigo': '1',
                'descripcion': 'Producto de ejemplo',
                'cantidad': '1',
                'precio_unitario': '1000,00',
                'subtotal': '1000,00'
            }
        ]
    }
    
    # Datos de verdad de campo (ground truth)
    ground_truth = {
        'tipo_factura': 'A',
        'razon_social_vendedor': 'Empresa Ejemplo SRL',
        'cuit_vendedor': '20-12345678-9',
        'razon_social_comprador': 'Cliente Ejemplo',
        'cuit_comprador': '20-87654321-0',
        'condicion_iva_comprador': 'Responsable Inscripto',
        'condicion_venta': 'Contado',
        'fecha_emision': '01/01/2024',
        'subtotal': '1000,00',
        'importe_total': '1210,00',
        'iva': '210,00',
        'deuda_impositiva': '210,00',
        'numero_factura': '0001-00000001',
        'punto_venta': '0001'
    }
    
    # Textos de ejemplo
    extracted_text = """
    ORIGINAL A Empresa Ejemplo SRL Le PAGTURA Punto de Venta: 0001
    Comp. Nro: 0001-00000001 Fecha de Emisión: 01/01/2024
    CUIT: 20-12345678-9
    DNI: 20-87654321-0 Apellido y Nombre / Razón Social: Cliente Ejemplo
    Condición frente al IVA: Responsable Inscripto
    Condición de venta: Contado
    1 Producto de ejemplo 1 unidad 1000,00 21% 210,00 1000,00
    Subtotal: $ 1000,00
    IVA: $ 210,00
    Importe Total: $ 1210,00
    """
    
    ground_truth_text = """
    ORIGINAL A Empresa Ejemplo SRL Le PAGTURA Punto de Venta: 0001
    Comp. Nro: 0001-00000001 Fecha de Emisión: 01/01/2024
    CUIT: 20-12345678-9
    DNI: 20-87654321-0 Apellido y Nombre / Razón Social: Cliente Ejemplo
    Condición frente al IVA: Responsable Inscripto
    Condición de venta: Contado
    1 Producto de ejemplo 1 unidad 1000,00 21% 210,00 1000,00
    Subtotal: $ 1000,00
    IVA: $ 210,00
    Importe Total: $ 1210,00
    """
    
    processing_time = 2.5  # segundos
    
    # Calcular métricas
    print("\nCalculando metricas...")
    
    # Confidence Score
    confidence = calculator.calculate_confidence_score(extracted_fields)
    print(f"   Confidence Score: {confidence:.3f}")
    
    # Field Accuracy
    accuracy, accuracy_details = calculator.calculate_field_accuracy(extracted_fields, ground_truth)
    print(f"   Field Accuracy: {accuracy:.3f}")
    print(f"   Campos correctos: {accuracy_details['correct_fields']}/{accuracy_details['total_fields']}")
    
    # CER y WER
    cer = calculator.calculate_cer(extracted_text, ground_truth_text)
    wer = calculator.calculate_wer(extracted_text, ground_truth_text)
    print(f"   CER (Character Error Rate): {cer:.3f}")
    print(f"   WER (Word Error Rate): {wer:.3f}")
    
    # Métricas de rendimiento
    throughput = 1.0 / processing_time
    print(f"   Throughput: {throughput:.2f} documentos/segundo")
    print(f"   Latency: {processing_time:.2f} segundos")
    
    # Métricas completas
    print("\nMetricas completas:")
    metrics = calculator.calculate_comprehensive_metrics(
        extracted_fields, ground_truth, extracted_text, ground_truth_text, processing_time
    )
    
    print(f"   Confidence Score: {metrics.confidence_score:.3f}")
    print(f"   Field Accuracy: {metrics.field_accuracy:.3f}")
    print(f"   CER: {metrics.cer:.3f}")
    print(f"   WER: {metrics.wer:.3f}")
    print(f"   Processing Latency: {metrics.processing_latency:.2f}s")
    print(f"   Throughput: {metrics.throughput:.2f} docs/seg")
    print(f"   Total Fields: {metrics.total_fields}")
    print(f"   Correct Fields: {metrics.correct_fields}")
    print(f"   Missing Fields: {metrics.missing_fields}")
    print(f"   Incorrect Fields: {metrics.incorrect_fields}")
    
    return metrics

def test_metrics_with_errors():
    """Prueba las métricas con datos que contienen errores"""
    print("\nProbando metricas con errores...")
    
    calculator = MetricsCalculator()
    
    # Datos con errores
    extracted_fields_with_errors = {
        'tipo_factura': 'B',  # Error: debería ser 'A'
        'razon_social_vendedor': 'Empresa Ejemplo SRL',  # Correcto
        'cuit_vendedor': '20-12345678-9',  # Correcto
        'razon_social_comprador': 'Cliente Incorrecto',  # Error
        'cuit_comprador': '20-87654321-0',  # Correcto
        'fecha_emision': '02/01/2024',  # Error: debería ser '01/01/2024'
        'subtotal': '1000,00',  # Correcto
        'importe_total': '1200,00',  # Error: debería ser '1210,00'
        # Faltan algunos campos
    }
    
    ground_truth = {
        'tipo_factura': 'A',
        'razon_social_vendedor': 'Empresa Ejemplo SRL',
        'cuit_vendedor': '20-12345678-9',
        'razon_social_comprador': 'Cliente Ejemplo',
        'cuit_comprador': '20-87654321-0',
        'condicion_iva_comprador': 'Responsable Inscripto',
        'condicion_venta': 'Contado',
        'fecha_emision': '01/01/2024',
        'subtotal': '1000,00',
        'importe_total': '1210,00',
        'iva': '210,00',
        'deuda_impositiva': '210,00',
        'numero_factura': '0001-00000001',
        'punto_venta': '0001'
    }
    
    # Texto con errores de OCR
    extracted_text_with_errors = """
    ORIGINAL B Empresa Ejemplo SRL Le PAGTURA Punto de Venta: 0001
    Comp. Nro: 0001-00000001 Fecha de Emisión: 02/01/2024
    CUIT: 20-12345678-9
    DNI: 20-87654321-0 Apellido y Nombre / Razón Social: Cliente Incorrecto
    Condición frente al IVA: Responsable Inscripto
    Condición de venta: Contado
    1 Producto de ejemplo 1 unidad 1000,00 21% 210,00 1000,00
    Subtotal: $ 1000,00
    IVA: $ 210,00
    Importe Total: $ 1200,00
    """
    
    ground_truth_text = """
    ORIGINAL A Empresa Ejemplo SRL Le PAGTURA Punto de Venta: 0001
    Comp. Nro: 0001-00000001 Fecha de Emisión: 01/01/2024
    CUIT: 20-12345678-9
    DNI: 20-87654321-0 Apellido y Nombre / Razón Social: Cliente Ejemplo
    Condición frente al IVA: Responsable Inscripto
    Condición de venta: Contado
    1 Producto de ejemplo 1 unidad 1000,00 21% 210,00 1000,00
    Subtotal: $ 1000,00
    IVA: $ 210,00
    Importe Total: $ 1210,00
    """
    
    processing_time = 3.2  # segundos
    
    # Calcular métricas
    metrics = calculator.calculate_comprehensive_metrics(
        extracted_fields_with_errors, ground_truth, 
        extracted_text_with_errors, ground_truth_text, processing_time
    )
    
    print(f"   Confidence Score: {metrics.confidence_score:.3f}")
    print(f"   Field Accuracy: {metrics.field_accuracy:.3f}")
    print(f"   CER: {metrics.cer:.3f}")
    print(f"   WER: {metrics.wer:.3f}")
    print(f"   Processing Latency: {metrics.processing_latency:.2f}s")
    print(f"   Throughput: {metrics.throughput:.2f} docs/seg")
    print(f"   Total Fields: {metrics.total_fields}")
    print(f"   Correct Fields: {metrics.correct_fields}")
    print(f"   Missing Fields: {metrics.missing_fields}")
    print(f"   Incorrect Fields: {metrics.incorrect_fields}")
    
    return metrics

def test_batch_processor():
    """Prueba el procesador de lotes (simulado)"""
    print("\nProbando BatchProcessor...")
    
    # Crear datos de prueba simulados
    test_results = [
        {
            'file_path': 'test1.pdf',
            'success': True,
            'processing_time': 2.1,
            'confidence_score': 0.85,
            'metrics': {
                'confidence_score': 0.85,
                'field_accuracy': 0.92,
                'cer': 0.05,
                'wer': 0.08,
                'correct_fields': 12,
                'missing_fields': 1,
                'incorrect_fields': 0
            }
        },
        {
            'file_path': 'test2.pdf',
            'success': True,
            'processing_time': 1.8,
            'confidence_score': 0.78,
            'metrics': {
                'confidence_score': 0.78,
                'field_accuracy': 0.88,
                'cer': 0.07,
                'wer': 0.12,
                'correct_fields': 11,
                'missing_fields': 2,
                'incorrect_fields': 0
            }
        },
        {
            'file_path': 'test3.pdf',
            'success': False,
            'processing_time': 0.5,
            'confidence_score': 0.0,
            'metrics': None
        }
    ]
    
    processing_times = [2.1, 1.8, 0.5]
    total_time = 4.4
    
    # Crear procesador de lotes
    batch_processor = BatchProcessor()
    
    # Calcular métricas del lote
    batch_metrics = batch_processor._calculate_batch_metrics(test_results, processing_times, total_time)
    
    print(f"   Throughput: {batch_metrics['throughput']:.2f} documentos/segundo")
    print(f"   Tiempo promedio: {batch_metrics['avg_processing_time']:.2f} segundos")
    print(f"   Confidence Score promedio: {batch_metrics['avg_confidence_score']:.3f}")
    print(f"   Tasa de éxito: {batch_metrics['success_rate']:.2%}")
    
    if batch_metrics.get('accuracy_metrics'):
        acc = batch_metrics['accuracy_metrics']
        print(f"   Precisión promedio: {acc['avg_field_accuracy']:.3f}")
        print(f"   CER promedio: {acc['avg_cer']:.3f}")
        print(f"   WER promedio: {acc['avg_wer']:.3f}")
    
    return batch_metrics

def create_sample_ground_truth():
    """Crea un archivo de ground truth de ejemplo"""
    print("\nCreando archivo de ground truth de ejemplo...")
    
    sample_data = {
        "factura1.pdf": {
            "tipo_factura": "A",
            "razon_social_vendedor": "Empresa Ejemplo SRL",
            "cuit_vendedor": "20-12345678-9",
            "razon_social_comprador": "Cliente Ejemplo",
            "cuit_comprador": "20-87654321-0",
            "condicion_iva_comprador": "Responsable Inscripto",
            "condicion_venta": "Contado",
            "fecha_emision": "01/01/2024",
            "subtotal": "1000,00",
            "importe_total": "1210,00",
            "iva": "210,00",
            "deuda_impositiva": "210,00",
            "numero_factura": "0001-00000001",
            "punto_venta": "0001",
            "raw_text": "Texto completo de la factura 1..."
        },
        "factura2.pdf": {
            "tipo_factura": "B",
            "razon_social_vendedor": "Otra Empresa SA",
            "cuit_vendedor": "30-98765432-1",
            "razon_social_comprador": "Otro Cliente",
            "cuit_comprador": "20-11111111-1",
            "condicion_iva_comprador": "Consumidor Final",
            "condicion_venta": "Contado",
            "fecha_emision": "15/01/2024",
            "subtotal": "500,00",
            "importe_total": "605,00",
            "iva": "105,00",
            "deuda_impositiva": "105,00",
            "numero_factura": "0002-00000001",
            "punto_venta": "0002",
            "raw_text": "Texto completo de la factura 2..."
        }
    }
    
    # Guardar archivo
    with open('sample_ground_truth.json', 'w', encoding='utf-8') as f:
        json.dump(sample_data, f, indent=2, ensure_ascii=False)
    
    print("   Archivo 'sample_ground_truth.json' creado")
    print("   Edita este archivo con los datos correctos para tus facturas de prueba")

def main():
    """Función principal de prueba"""
    print("Probando Sistema de Metricas del Modelo de Parsing de Facturas")
    print("=" * 70)
    
    try:
        # Probar calculador de métricas
        test_metrics_calculator()
        
        # Probar con errores
        test_metrics_with_errors()
        
        # Probar procesador de lotes
        test_batch_processor()
        
        # Crear ground truth de ejemplo
        create_sample_ground_truth()
        
        print("\n[SUCCESS] Todas las pruebas completadas exitosamente")
        print("\nProximos pasos:")
        print("   1. Coloca archivos de facturas en un directorio")
        print("   2. Edita 'sample_ground_truth.json' con los datos correctos")
        print("   3. Ejecuta: python benchmark_model.py --test-dir <directorio> --ground-truth sample_ground_truth.json")
        
    except Exception as e:
        print(f"\n[ERROR] Error en las pruebas: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
