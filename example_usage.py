"""
Ejemplo de uso del sistema de métricas para el modelo de parsing de facturas
"""
import os
import sys
import json
import time
from pathlib import Path

# Agregar el directorio actual al path
sys.path.append(str(Path(__file__).parent))

from services.metrics_calculator import MetricsCalculator
from services.batch_processor import BatchProcessor

def example_single_document_metrics():
    """Ejemplo de cálculo de métricas para un documento individual"""
    print("Ejemplo: Metricas de un documento individual")
    print("-" * 50)
    
    # Crear calculador de métricas
    calculator = MetricsCalculator()
    
    # Datos extraídos por el modelo (simulados)
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
    
    # Textos extraídos y correctos
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
    
    processing_time = 2.3  # segundos
    
    # Calcular métricas completas
    metrics = calculator.calculate_comprehensive_metrics(
        extracted_fields=extracted_fields,
        ground_truth=ground_truth,
        extracted_text=extracted_text,
        ground_truth_text=ground_truth_text,
        processing_time=processing_time
    )
    
    # Mostrar resultados
    print(f"Confidence Score: {metrics.confidence_score:.3f}")
    print(f"Field Accuracy: {metrics.field_accuracy:.3f}")
    print(f"CER (Character Error Rate): {metrics.cer:.3f}")
    print(f"WER (Word Error Rate): {metrics.wer:.3f}")
    print(f"Processing Latency: {metrics.processing_latency:.2f} segundos")
    print(f"Throughput: {metrics.throughput:.2f} documentos/segundo")
    print(f"Campos correctos: {metrics.correct_fields}/{metrics.total_fields}")
    print(f"Campos faltantes: {metrics.missing_fields}")
    print(f"Campos incorrectos: {metrics.incorrect_fields}")
    
    return metrics

def example_batch_processing():
    """Ejemplo de procesamiento de lote con métricas"""
    print("\nEjemplo: Procesamiento de lote")
    print("-" * 50)
    
    # Crear procesador de lotes
    batch_processor = BatchProcessor(max_workers=2)
    
    # Simular resultados de procesamiento de lote
    simulated_results = []
    processing_times = []
    
    # Simular 5 documentos procesados
    for i in range(5):
        # Simular tiempo de procesamiento variable
        processing_time = 1.5 + (i * 0.3)  # 1.5s a 2.7s
        processing_times.append(processing_time)
        
        # Simular resultado exitoso
        result = {
            'file_path': f'test_factura_{i+1}.pdf',
            'success': True,
            'processing_time': processing_time,
            'confidence_score': 0.8 + (i * 0.02),  # 0.8 a 0.88
            'metrics': {
                'confidence_score': 0.8 + (i * 0.02),
                'field_accuracy': 0.85 + (i * 0.01),
                'cer': 0.05 - (i * 0.005),
                'wer': 0.08 - (i * 0.005),
                'correct_fields': 12 + i,
                'missing_fields': 2 - i,
                'incorrect_fields': 1 if i > 2 else 0
            }
        }
        simulated_results.append(result)
    
    # Simular un documento fallido
    simulated_results.append({
        'file_path': 'test_factura_6.pdf',
        'success': False,
        'processing_time': 0.5,
        'confidence_score': 0.0,
        'metrics': None
    })
    processing_times.append(0.5)
    
    total_time = sum(processing_times)
    
    # Calcular métricas del lote
    batch_metrics = batch_processor._calculate_batch_metrics(
        simulated_results, processing_times, total_time
    )
    
    # Mostrar resultados del lote
    print(f"Total de documentos: {len(simulated_results)}")
    print(f"Documentos exitosos: {batch_metrics['total_documents_processed']}")
    print(f"Tasa de éxito: {batch_metrics['success_rate']:.2%}")
    print(f"Throughput: {batch_metrics['throughput']:.2f} documentos/segundo")
    print(f"Tiempo promedio: {batch_metrics['avg_processing_time']:.2f} segundos")
    print(f"Confidence Score promedio: {batch_metrics['avg_confidence_score']:.3f}")
    
    if batch_metrics.get('accuracy_metrics'):
        acc = batch_metrics['accuracy_metrics']
        print(f"Precisión promedio: {acc['avg_field_accuracy']:.3f}")
        print(f"CER promedio: {acc['avg_cer']:.3f}")
        print(f"WER promedio: {acc['avg_wer']:.3f}")
        print(f"Campos correctos totales: {acc['total_correct_fields']}")
        print(f"Campos faltantes totales: {acc['total_missing_fields']}")
        print(f"Campos incorrectos totales: {acc['total_incorrect_fields']}")
    
    return batch_metrics

def example_ground_truth_creation():
    """Ejemplo de creación de archivo de ground truth"""
    print("\nEjemplo: Creacion de archivo de ground truth")
    print("-" * 50)
    
    # Crear datos de ground truth de ejemplo
    ground_truth_data = {
        "factura_ejemplo_1.pdf": {
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
        "factura_ejemplo_2.pdf": {
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
    filename = "ejemplo_ground_truth.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(ground_truth_data, f, indent=2, ensure_ascii=False)
    
    print(f"Archivo de ground truth creado: {filename}")
    print("Estructura del archivo:")
    print(json.dumps(ground_truth_data, indent=2, ensure_ascii=False))
    
    return filename

def example_performance_analysis():
    """Ejemplo de análisis de rendimiento"""
    print("\nEjemplo: Analisis de rendimiento")
    print("-" * 50)
    
    calculator = MetricsCalculator()
    
    # Simular tiempos de procesamiento de diferentes lotes
    batch_times = {
        "Lote 10": [1.2, 1.5, 1.3, 1.4, 1.6, 1.1, 1.7, 1.2, 1.4, 1.3],
        "Lote 25": [1.3, 1.4, 1.5, 1.2, 1.6, 1.1, 1.7, 1.3, 1.4, 1.5, 1.2, 1.6, 1.1, 1.7, 1.3, 1.4, 1.5, 1.2, 1.6, 1.1, 1.7, 1.3, 1.4, 1.5, 1.2],
        "Lote 50": [1.4, 1.5, 1.6, 1.3, 1.7, 1.2, 1.8, 1.4, 1.5, 1.6] * 5,  # Repetir para simular 50
        "Lote 100": [1.5, 1.6, 1.7, 1.4, 1.8, 1.3, 1.9, 1.5, 1.6, 1.7] * 10  # Repetir para simular 100
    }
    
    print("Analisis de rendimiento por tamano de lote:")
    print(f"{'Lote':<12} {'Docs/seg':<10} {'Tiempo (s)':<12} {'Min (s)':<10} {'Max (s)':<10}")
    print("-" * 60)
    
    for batch_name, times in batch_times.items():
        metrics = calculator.calculate_processing_metrics(times)
        print(f"{batch_name:<12} {metrics['throughput']:<10.2f} {metrics['avg_latency']:<12.2f} {metrics['min_latency']:<10.2f} {metrics['max_latency']:<10.2f}")
    
    # Recomendación
    print("\nRecomendaciones:")
    print("- Para lotes pequenos (10-25): Mejor para pruebas rapidas")
    print("- Para lotes medianos (50): Balance entre velocidad y estabilidad")
    print("- Para lotes grandes (100): Maximo throughput pero mayor uso de memoria")

def main():
    """Función principal del ejemplo"""
    print("Ejemplo de Uso del Sistema de Metricas")
    print("=" * 60)
    
    try:
        # Ejemplo 1: Métricas de documento individual
        example_single_document_metrics()
        
        # Ejemplo 2: Procesamiento de lote
        example_batch_processing()
        
        # Ejemplo 3: Creación de ground truth
        example_ground_truth_creation()
        
        # Ejemplo 4: Análisis de rendimiento
        example_performance_analysis()
        
        print("\n[SUCCESS] Todos los ejemplos completados exitosamente")
        print("\nProximos pasos:")
        print("   1. Coloca tus facturas en un directorio")
        print("   2. Edita 'ejemplo_ground_truth.json' con los datos correctos")
        print("   3. Ejecuta: python benchmark_model.py --test-dir <directorio> --ground-truth ejemplo_ground_truth.json")
        print("   4. O usa la API: curl -X POST http://localhost:8000/evaluate-metrics")
        
    except Exception as e:
        print(f"\n[ERROR] Error en los ejemplos: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
