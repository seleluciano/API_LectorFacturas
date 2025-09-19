"""
Script principal para hacer benchmark del modelo de parsing de facturas
Mide métricas de rendimiento y calidad del modelo
"""
import os
import sys
import time
import json
import argparse
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

# Agregar el directorio actual al path
sys.path.append(str(Path(__file__).parent))

from services.batch_processor import BatchProcessor
from services.metrics_calculator import MetricsCalculator

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ModelBenchmark:
    """Clase principal para hacer benchmark del modelo"""
    
    def __init__(self, max_workers: int = 4):
        self.batch_processor = BatchProcessor(max_workers=max_workers)
        self.metrics_calculator = MetricsCalculator()
    
    def run_benchmark(self, 
                     test_directory: str,
                     batch_sizes: List[int] = [10, 25, 50, 100],
                     ground_truth_file: Optional[str] = None,
                     output_dir: str = "benchmark_results") -> Dict[str, Any]:
        """
        Ejecuta benchmark completo del modelo
        
        Args:
            test_directory: Directorio con archivos de prueba
            batch_sizes: Tamaños de lote a probar
            ground_truth_file: Archivo con datos de verdad de campo
            output_dir: Directorio para guardar resultados
            
        Returns:
            Resultados del benchmark
        """
        logger.info("Iniciando benchmark del modelo de parsing de facturas")
        
        # Crear directorio de salida
        os.makedirs(output_dir, exist_ok=True)
        
        # Cargar ground truth si se proporciona
        ground_truth_data = None
        if ground_truth_file and os.path.exists(ground_truth_file):
            ground_truth_data = self.batch_processor.load_ground_truth(ground_truth_file)
            logger.info(f"Ground truth cargado: {len(ground_truth_data)} archivos")
        
        # Buscar archivos de prueba
        test_files = self._find_test_files(test_directory)
        if not test_files:
            raise ValueError(f"No se encontraron archivos de prueba en {test_directory}")
        
        logger.info(f"Archivos de prueba encontrados: {len(test_files)}")
        
        # Ejecutar benchmarks para diferentes tamaños de lote
        benchmark_results = {}
        
        for batch_size in batch_sizes:
            if batch_size > len(test_files):
                logger.warning(f"[WARNING] Tamano de lote {batch_size} mayor que archivos disponibles ({len(test_files)})")
                continue
            
            logger.info(f"Ejecutando benchmark con lote de {batch_size} archivos")
            
            # Seleccionar archivos para este lote
            batch_files = test_files[:batch_size]
            
            # Procesar lote
            start_time = time.time()
            batch_result = self.batch_processor.process_batch(
                file_paths=batch_files,
                ground_truth_data=ground_truth_data,
                save_results=True,
                results_file=os.path.join(output_dir, f"batch_{batch_size}_results.json")
            )
            batch_time = time.time() - start_time
            
            # Generar reporte
            report = self.batch_processor.generate_performance_report(batch_result)
            
            # Guardar reporte
            report_file = os.path.join(output_dir, f"batch_{batch_size}_report.txt")
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
            
            benchmark_results[batch_size] = {
                'batch_result': batch_result,
                'total_time': batch_time,
                'report': report
            }
            
            logger.info(f"[SUCCESS] Benchmark completado para lote de {batch_size} archivos")
            logger.info(f"   Throughput: {batch_result['performance_metrics']['throughput']:.2f} docs/seg")
            logger.info(f"   Tasa de exito: {batch_result['performance_metrics']['success_rate']:.2%}")
        
        # Generar reporte consolidado
        consolidated_report = self._generate_consolidated_report(benchmark_results)
        
        # Guardar reporte consolidado
        consolidated_file = os.path.join(output_dir, "consolidated_report.txt")
        with open(consolidated_file, 'w', encoding='utf-8') as f:
            f.write(consolidated_report)
        
        # Guardar resultados JSON
        results_file = os.path.join(output_dir, "benchmark_results.json")
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(benchmark_results, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"Benchmark completado. Resultados guardados en {output_dir}")
        
        return benchmark_results
    
    def _find_test_files(self, directory: str) -> List[str]:
        """Encuentra archivos de prueba válidos en el directorio"""
        if not os.path.exists(directory):
            return []
        
        valid_extensions = ['.jpg', '.jpeg', '.png', '.pdf']
        file_paths = []
        
        for ext in valid_extensions:
            pattern = f"**/*{ext}"
            files = list(Path(directory).glob(pattern))
            file_paths.extend([str(f) for f in files])
        
        return sorted(file_paths)
    
    def _generate_consolidated_report(self, benchmark_results: Dict[str, Any]) -> str:
        """Genera un reporte consolidado de todos los benchmarks"""
        report = """
=== REPORTE CONSOLIDADO DE BENCHMARK DEL MODELO ===
Fecha: {}\n
""".format(time.strftime('%Y-%m-%d %H:%M:%S'))
        
        # Tabla de rendimiento por tamaño de lote
        report += "RENDIMIENTO POR TAMAÑO DE LOTE:\n"
        report += "-" * 80 + "\n"
        report += f"{'Lote':<8} {'Docs/seg':<10} {'Tiempo (s)':<12} {'Éxito (%)':<12} {'Confianza':<12}\n"
        report += "-" * 80 + "\n"
        
        for batch_size, result in benchmark_results.items():
            perf = result['batch_result']['performance_metrics']
            report += f"{batch_size:<8} {perf['throughput']:<10.2f} {result['total_time']:<12.2f} {perf['success_rate']*100:<12.1f} {perf['avg_confidence_score']:<12.3f}\n"
        
        # Análisis de tendencias
        report += "\nANÁLISIS DE TENDENCIAS:\n"
        report += "-" * 40 + "\n"
        
        throughputs = [result['batch_result']['performance_metrics']['throughput'] for result in benchmark_results.values()]
        success_rates = [result['batch_result']['performance_metrics']['success_rate'] for result in benchmark_results.values()]
        
        if throughputs:
            report += f"Throughput promedio: {sum(throughputs)/len(throughputs):.2f} documentos/segundo\n"
            report += f"Throughput máximo: {max(throughputs):.2f} documentos/segundo\n"
            report += f"Throughput mínimo: {min(throughputs):.2f} documentos/segundo\n"
        
        if success_rates:
            report += f"Tasa de éxito promedio: {sum(success_rates)/len(success_rates)*100:.1f}%\n"
            report += f"Tasa de éxito máxima: {max(success_rates)*100:.1f}%\n"
            report += f"Tasa de éxito mínima: {min(success_rates)*100:.1f}%\n"
        
        # Recomendaciones
        report += "\nRECOMENDACIONES:\n"
        report += "-" * 40 + "\n"
        
        if throughputs:
            best_throughput_batch = max(benchmark_results.keys(), 
                                      key=lambda x: benchmark_results[x]['batch_result']['performance_metrics']['throughput'])
            report += f"• Mejor throughput con lote de {best_throughput_batch} documentos\n"
        
        if success_rates:
            best_success_batch = max(benchmark_results.keys(),
                                   key=lambda x: benchmark_results[x]['batch_result']['performance_metrics']['success_rate'])
            report += f"• Mejor tasa de éxito con lote de {best_success_batch} documentos\n"
        
        # Métricas de calidad si están disponibles
        quality_metrics = []
        for result in benchmark_results.values():
            acc_metrics = result['batch_result']['performance_metrics'].get('accuracy_metrics')
            if acc_metrics:
                quality_metrics.append(acc_metrics)
        
        if quality_metrics:
            report += "\nMÉTRICAS DE CALIDAD PROMEDIO:\n"
            report += "-" * 40 + "\n"
            
            avg_accuracy = sum(m['avg_field_accuracy'] for m in quality_metrics) / len(quality_metrics)
            avg_cer = sum(m['avg_cer'] for m in quality_metrics) / len(quality_metrics)
            avg_wer = sum(m['avg_wer'] for m in quality_metrics) / len(quality_metrics)
            
            report += f"• Precisión de campos: {avg_accuracy:.3f}\n"
            report += f"• CER (Character Error Rate): {avg_cer:.3f}\n"
            report += f"• WER (Word Error Rate): {avg_wer:.3f}\n"
        
        return report
    
    def create_sample_ground_truth(self, 
                                 test_files: List[str], 
                                 output_file: str = "sample_ground_truth.json"):
        """
        Crea un archivo de ejemplo de ground truth para los archivos de prueba
        
        Args:
            test_files: Lista de archivos de prueba
            output_file: Archivo de salida para el ground truth
        """
        sample_ground_truth = {}
        
        for file_path in test_files:
            filename = os.path.basename(file_path)
            
            # Crear datos de ejemplo
            sample_ground_truth[filename] = {
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
                'raw_text': 'Texto completo de la factura...'
            }
        
        # Guardar archivo
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(sample_ground_truth, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Archivo de ground truth de ejemplo creado: {output_file}")
        logger.info("   Edita este archivo con los datos correctos para cada factura")

def main():
    """Función principal del script"""
    parser = argparse.ArgumentParser(description='Benchmark del modelo de parsing de facturas')
    parser.add_argument('--test-dir', required=True, help='Directorio con archivos de prueba')
    parser.add_argument('--batch-sizes', nargs='+', type=int, default=[10, 25, 50, 100],
                       help='Tamaños de lote a probar')
    parser.add_argument('--ground-truth', help='Archivo JSON con datos de verdad de campo')
    parser.add_argument('--output-dir', default='benchmark_results',
                       help='Directorio para guardar resultados')
    parser.add_argument('--max-workers', type=int, default=4,
                       help='Número máximo de workers para procesamiento paralelo')
    parser.add_argument('--create-sample-gt', action='store_true',
                       help='Crear archivo de ground truth de ejemplo')
    
    args = parser.parse_args()
    
    # Crear benchmark
    benchmark = ModelBenchmark(max_workers=args.max_workers)
    
    try:
        if args.create_sample_gt:
            # Crear ground truth de ejemplo
            test_files = benchmark._find_test_files(args.test_dir)
            if test_files:
                benchmark.create_sample_ground_truth(test_files, 'sample_ground_truth.json')
            else:
                logger.error("No se encontraron archivos de prueba para crear ground truth")
        else:
            # Ejecutar benchmark
            results = benchmark.run_benchmark(
                test_directory=args.test_dir,
                batch_sizes=args.batch_sizes,
                ground_truth_file=args.ground_truth,
                output_dir=args.output_dir
            )
            
            logger.info("[SUCCESS] Benchmark completado exitosamente")
            
    except Exception as e:
        logger.error(f"[ERROR] Error ejecutando benchmark: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
