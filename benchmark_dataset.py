"""
Script para hacer benchmark del modelo con el dataset de facturas
Incluye imágenes y archivos JSON de ground truth
"""
import os
import sys
import time
import json
import argparse
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

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

class DatasetBenchmark:
    """Clase para hacer benchmark con dataset de facturas (imagen + JSON)"""
    
    def __init__(self, max_workers: int = 4):
        self.batch_processor = BatchProcessor(max_workers=max_workers)
        self.metrics_calculator = MetricsCalculator()
    
    def load_dataset_ground_truth(self, dataset_directory: str) -> Dict[str, Dict[str, Any]]:
        """
        Carga los archivos JSON del dataset como ground truth
        
        Args:
            dataset_directory: Directorio del dataset con imágenes y JSONs
            
        Returns:
            Diccionario con ground truth por archivo
        """
        ground_truth = {}
        
        # Buscar todos los archivos JSON
        json_files = list(Path(dataset_directory).glob("*.json"))
        
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Obtener el nombre base del archivo (sin extensión)
                base_name = json_file.stem
                
                # Buscar la imagen correspondiente
                image_extensions = ['.png', '.jpg', '.jpeg']
                image_path = None
                
                for ext in image_extensions:
                    potential_image = json_file.parent / f"{base_name}{ext}"
                    if potential_image.exists():
                        image_path = str(potential_image)
                        break
                
                if image_path:
                    # Mapear los campos del JSON a la estructura esperada
                    ground_truth[os.path.basename(image_path)] = {
                        'tipo_factura': data.get('tipo_factura', ''),
                        'razon_social_vendedor': data.get('razon_social_emisor', ''),
                        'cuit_vendedor': data.get('cuit_emisor', ''),
                        'razon_social_comprador': data.get('razon_social_receptor', ''),
                        'cuit_comprador': data.get('cuit_receptor', ''),
                        'condicion_iva_comprador': data.get('condicion_iva_receptor', ''),
                        'condicion_venta': data.get('condicion_venta', ''),
                        'fecha_emision': data.get('fecha_emision', ''),
                        'subtotal': data.get('subtotal', ''),
                        'importe_total': data.get('importe_total', ''),
                        'iva': data.get('iva', ''),
                        'deuda_impositiva': data.get('percepcion_iibb', ''),
                        'numero_factura': data.get('numero_factura', ''),
                        'punto_venta': data.get('punto_venta', ''),
                        'raw_text': self._generate_ground_truth_text(data),  # Generar texto del JSON
                        'items': data.get('items', [])
                    }
                    
                    logger.debug(f"Ground truth cargado para: {os.path.basename(image_path)}")
                else:
                    logger.warning(f"No se encontró imagen correspondiente para: {json_file}")
                    
            except Exception as e:
                logger.error(f"Error cargando JSON {json_file}: {e}")
        
        logger.info(f"Ground truth cargado: {len(ground_truth)} archivos")
        return ground_truth
    
    def _generate_ground_truth_text(self, data: Dict[str, Any]) -> str:
        """
        Genera texto del ground truth a partir de los datos JSON
        
        Args:
            data: Datos del JSON
            
        Returns:
            Texto generado para comparación CER/WER
        """
        text_parts = []
        
        # Agregar campos principales (usar nombres correctos del JSON)
        if data.get('cuit_vendedor'):
            text_parts.append(f"CUIT: {data['cuit_vendedor']}")
        if data.get('cuit_comprador'):
            text_parts.append(f"DNI: {data['cuit_comprador']}")
        if data.get('fecha_emision'):
            text_parts.append(f"Fecha de Emisión: {data['fecha_emision']}")
        if data.get('subtotal'):
            text_parts.append(f"Subtotal: {data['subtotal']}")
        if data.get('importe_total'):
            text_parts.append(f"Importe Total: {data['importe_total']}")
        
        # Agregar items (usar nombre correcto del JSON)
        items = data.get('items', [])
        for i, item in enumerate(items, 1):
            if isinstance(item, dict):
                descripcion = item.get('descripcion', '')
                cantidad = item.get('cantidad', '')
                precio_unitario = item.get('precio_unitario', '')
                bonificacion = item.get('bonificacion', '')
                importe_bonificacion = item.get('importe_bonificacion', '')
                
                if descripcion and cantidad and precio_unitario:
                    text_parts.append(f"{i} {descripcion} {cantidad} unidad {precio_unitario}")
                    if bonificacion:
                        text_parts.append(f"{bonificacion}")
                    if importe_bonificacion:
                        text_parts.append(f"{importe_bonificacion}")
        
        return ' '.join(text_parts)
    
    def find_dataset_images(self, dataset_directory: str) -> List[str]:
        """
        Encuentra todas las imágenes del dataset
        
        Args:
            dataset_directory: Directorio del dataset
            
        Returns:
            Lista de rutas de imágenes
        """
        image_extensions = ['.png', '.jpg', '.jpeg']
        image_paths = []
        
        for ext in image_extensions:
            pattern = f"*{ext}"
            files = list(Path(dataset_directory).glob(pattern))
            image_paths.extend([str(f) for f in files])
        
        return sorted(image_paths)
    
    def run_dataset_benchmark(self, 
                             dataset_directory: str,
                             batch_sizes: List[int] = [10, 20, 30, 50],
                             output_dir: str = "benchmark_results") -> Dict[str, Any]:
        """
        Ejecuta benchmark completo con el dataset de facturas
        
        Args:
            dataset_directory: Directorio del dataset con imágenes y JSONs
            batch_sizes: Tamaños de lote a probar
            output_dir: Directorio para guardar resultados
            
        Returns:
            Resultados del benchmark
        """
        logger.info("Iniciando benchmark del dataset de facturas")
        
        # Crear directorio de salida
        os.makedirs(output_dir, exist_ok=True)
        
        # Cargar ground truth desde los archivos JSON
        ground_truth_data = self.load_dataset_ground_truth(dataset_directory)
        
        # Buscar imágenes del dataset
        test_files = self.find_dataset_images(dataset_directory)
        if not test_files:
            raise ValueError(f"No se encontraron imágenes en {dataset_directory}")
        
        logger.info(f"Imágenes encontradas: {len(test_files)}")
        
        # Ejecutar benchmarks para diferentes tamaños de lote
        benchmark_results = {}
        
        for batch_size in batch_sizes:
            if batch_size > len(test_files):
                logger.warning(f"[WARNING] Tamaño de lote {batch_size} mayor que archivos disponibles ({len(test_files)})")
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
                results_file=os.path.join(output_dir, f"dataset_batch_{batch_size}_results.json")
            )
            batch_time = time.time() - start_time
            
            # Generar reporte
            report = self.batch_processor.generate_performance_report(batch_result)
            
            # Guardar reporte
            report_file = os.path.join(output_dir, f"dataset_batch_{batch_size}_report.txt")
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
            
            benchmark_results[batch_size] = {
                'batch_result': batch_result,
                'total_time': batch_time,
                'report': report
            }
            
            logger.info(f"[SUCCESS] Benchmark completado para lote de {batch_size} archivos")
            logger.info(f"   Throughput: {batch_result['performance_metrics']['throughput']:.2f} docs/seg")
            logger.info(f"   Tasa de éxito: {batch_result['performance_metrics']['success_rate']:.2%}")
        
        # Generar reporte consolidado
        consolidated_report = self._generate_consolidated_report(benchmark_results, dataset_directory, ground_truth_data)
        
        # Guardar reporte consolidado
        consolidated_file = os.path.join(output_dir, "dataset_consolidated_report.txt")
        with open(consolidated_file, 'w', encoding='utf-8') as f:
            f.write(consolidated_report)
        
        # Guardar resultados JSON
        results_file = os.path.join(output_dir, "dataset_benchmark_results.json")
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(benchmark_results, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"Benchmark del dataset completado. Resultados guardados en {output_dir}")
        
        return benchmark_results
    
    def _generate_consolidated_report(self, benchmark_results: Dict[str, Any], dataset_directory: str, ground_truth_data: Dict[str, Any]) -> str:
        """Genera un reporte consolidado de todos los benchmarks del dataset"""
        report = f"""
=== REPORTE CONSOLIDADO DE BENCHMARK DEL DATASET ===
Fecha: {time.strftime('%Y-%m-%d %H:%M:%S')}
Dataset: {dataset_directory}
Total de archivos en dataset: {len(self.find_dataset_images(dataset_directory))}

"""
        
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
        
        # Información del dataset
        report += "\nINFORMACIÓN DEL DATASET:\n"
        report += "-" * 40 + "\n"
        report += f"• Directorio: {dataset_directory}\n"
        report += f"• Total de facturas: {len(self.find_dataset_images(dataset_directory))}\n"
        report += f"• Formato: Imágenes PNG + JSON de ground truth\n"
        report += f"• Campos evaluados: {len(list(ground_truth_data.values())[0]) if ground_truth_data else 0}\n"
        
        return report

def main():
    """Función principal del script"""
    parser = argparse.ArgumentParser(description='Benchmark del modelo con dataset de facturas')
    parser.add_argument('--dataset-dir', required=True, help='Directorio del dataset con imágenes y JSONs')
    parser.add_argument('--batch-sizes', nargs='+', type=int, default=[10, 20, 30, 50],
                       help='Tamaños de lote a probar')
    parser.add_argument('--output-dir', default='benchmark_results',
                       help='Directorio para guardar resultados')
    parser.add_argument('--max-workers', type=int, default=4,
                       help='Número máximo de workers para procesamiento paralelo')
    
    args = parser.parse_args()
    
    # Verificar que el directorio del dataset existe
    if not os.path.exists(args.dataset_dir):
        logger.error(f"El directorio del dataset no existe: {args.dataset_dir}")
        sys.exit(1)
    
    # Crear benchmark
    benchmark = DatasetBenchmark(max_workers=args.max_workers)
    
    try:
        # Ejecutar benchmark
        results = benchmark.run_dataset_benchmark(
            dataset_directory=args.dataset_dir,
            batch_sizes=args.batch_sizes,
            output_dir=args.output_dir
        )
        
        logger.info("[SUCCESS] Benchmark del dataset completado exitosamente")
        
    except Exception as e:
        logger.error(f"[ERROR] Error ejecutando benchmark: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
