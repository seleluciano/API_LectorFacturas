"""
Procesador de lotes para evaluar el rendimiento del modelo con múltiples facturas
"""
import time
import os
import logging
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
import json

from services.advanced_image_processor import AdvancedImageProcessor
from services.invoice_parser import InvoiceParser
from services.metrics_calculator import MetricsCalculator, MetricsResult
from utils.file_utils import validate_file_type, validate_file_size

logger = logging.getLogger(__name__)

class BatchProcessor:
    """Procesador de lotes para evaluar el rendimiento del modelo"""
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.image_processor = AdvancedImageProcessor()
        self.invoice_parser = InvoiceParser()
        self.metrics_calculator = MetricsCalculator()
    
    def process_batch(self, 
                     file_paths: List[str], 
                     ground_truth_data: Optional[Dict[str, Dict[str, Any]]] = None,
                     save_results: bool = True,
                     results_file: str = "batch_results.json") -> Dict[str, Any]:
        """
        Procesa un lote de facturas y calcula métricas de rendimiento
        
        Args:
            file_paths: Lista de rutas de archivos a procesar
            ground_truth_data: Diccionario con datos de verdad de campo (opcional)
            save_results: Si guardar resultados en archivo
            results_file: Nombre del archivo de resultados
            
        Returns:
            Diccionario con resultados del lote
        """
        logger.info(f"Procesando lote de {len(file_paths)} facturas")
        
        start_time = time.time()
        results = []
        processing_times = []
        successful_count = 0
        failed_count = 0
        
        # Procesar archivos en paralelo
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Enviar tareas
            future_to_path = {
                executor.submit(self._process_single_file, path, ground_truth_data): path 
                for path in file_paths
            }
            
            # Recoger resultados
            for future in as_completed(future_to_path):
                path = future_to_path[future]
                try:
                    result = future.result()
                    results.append(result)
                    processing_times.append(result['processing_time'])
                    
                    if result['success']:
                        successful_count += 1
                    else:
                        failed_count += 1
                        
                except Exception as e:
                    logger.error(f"Error procesando {path}: {e}")
                    failed_count += 1
                    results.append({
                        'file_path': path,
                        'success': False,
                        'error': str(e),
                        'processing_time': 0.0
                    })
        
        total_time = time.time() - start_time
        
        # Calcular métricas del lote
        batch_metrics = self._calculate_batch_metrics(results, processing_times, total_time)
        
        # Crear resultado final
        batch_result = {
            'batch_info': {
                'total_files': len(file_paths),
                'successful_files': successful_count,
                'failed_files': failed_count,
                'total_processing_time': total_time,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            },
            'performance_metrics': batch_metrics,
            'individual_results': results
        }
        
        # Guardar resultados si se solicita
        if save_results:
            self._save_results(batch_result, results_file)
        
        logger.info(f"Lote procesado: {successful_count}/{len(file_paths)} exitosos en {total_time:.2f}s")
        
        return batch_result
    
    def _process_single_file(self, 
                           file_path: str, 
                           ground_truth_data: Optional[Dict[str, Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Procesa un archivo individual
        
        Args:
            file_path: Ruta del archivo
            ground_truth_data: Datos de verdad de campo
            
        Returns:
            Resultado del procesamiento
        """
        start_time = time.time()
        
        try:
            # Validar archivo
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Archivo no encontrado: {file_path}")
            
            # Procesar imagen
            result = self.image_processor.process_image(file_path)
            
            if result.status != "success":
                raise Exception(f"Error en procesamiento de imagen: {result.error_message}")
            
            # Extraer datos de factura
            invoice_data = result.metadata.get("invoice_parsing", {})
            
            if not invoice_data.get("success", False):
                raise Exception("No se pudo extraer datos de factura")
            
            # Obtener la primera factura (asumir una factura por archivo)
            invoices = invoice_data.get("invoices", [])
            if not invoices:
                raise Exception("No se encontraron facturas en el archivo")
            
            invoice = invoices[0]
            extracted_fields = invoice.get("extracted_fields", {})
            extracted_text = invoice.get("raw_text", "")
            
            # Calcular métricas si hay ground truth
            metrics = None
            if ground_truth_data:
                filename = os.path.basename(file_path)
                if filename in ground_truth_data:
                    ground_truth = ground_truth_data[filename]
                    ground_truth_text = ground_truth.get('raw_text', '')
                    
                    metrics = self.metrics_calculator.calculate_comprehensive_metrics(
                        extracted_fields=extracted_fields,
                        ground_truth=ground_truth,
                        extracted_text=extracted_text,
                        ground_truth_text=ground_truth_text,
                        processing_time=result.processing_time
                    )
            
            processing_time = time.time() - start_time
            
            return {
                'file_path': file_path,
                'filename': os.path.basename(file_path),
                'success': True,
                'processing_time': processing_time,
                'extracted_fields': extracted_fields,
                'extracted_text': extracted_text,
                'confidence_score': metrics.confidence_score if metrics else invoice.get("parsing_confidence", 0.0),
                'metrics': metrics.__dict__ if metrics else None,
                'metadata': {
                    'file_size': result.file_size,
                    'content_type': result.content_type,
                    'text_blocks_count': len(result.text_blocks),
                    'tables_count': len(result.tables),
                    'figures_count': len(result.figures)
                }
            }
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Error procesando {file_path}: {e}")
            
            return {
                'file_path': file_path,
                'filename': os.path.basename(file_path),
                'success': False,
                'error': str(e),
                'processing_time': processing_time,
                'extracted_fields': {},
                'extracted_text': '',
                'confidence_score': 0.0,
                'metrics': None
            }
    
    def _calculate_batch_metrics(self, 
                               results: List[Dict[str, Any]], 
                               processing_times: List[float],
                               total_time: float) -> Dict[str, Any]:
        """
        Calcula métricas agregadas del lote
        
        Args:
            results: Lista de resultados individuales
            processing_times: Lista de tiempos de procesamiento
            total_time: Tiempo total del lote
            
        Returns:
            Métricas del lote
        """
        successful_results = [r for r in results if r['success']]
        
        if not successful_results:
            return {
                'throughput': 0.0,
                'avg_processing_time': 0.0,
                'avg_confidence_score': 0.0,
                'success_rate': 0.0
            }
        
        # Métricas de rendimiento
        throughput = len(successful_results) / total_time if total_time > 0 else 0.0
        avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0.0
        
        # Métricas de calidad
        confidence_scores = [r['confidence_score'] for r in successful_results]
        avg_confidence_score = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
        
        # Métricas de accuracy (si hay ground truth)
        metrics_results = [r['metrics'] for r in successful_results if r['metrics']]
        accuracy_metrics = {}
        
        if metrics_results:
            # Calcular promedios de métricas
            field_accuracies = [m['field_accuracy'] for m in metrics_results]
            cer_values = [m['cer'] for m in metrics_results]
            wer_values = [m['wer'] for m in metrics_results]
            
            accuracy_metrics = {
                'avg_field_accuracy': sum(field_accuracies) / len(field_accuracies),
                'avg_cer': sum(cer_values) / len(cer_values),
                'avg_wer': sum(wer_values) / len(wer_values),
                'total_correct_fields': sum(m['correct_fields'] for m in metrics_results),
                'total_missing_fields': sum(m['missing_fields'] for m in metrics_results),
                'total_incorrect_fields': sum(m['incorrect_fields'] for m in metrics_results),
                'total_fields': sum(m['total_fields'] for m in metrics_results)
            }
        
        return {
            'throughput': throughput,
            'avg_processing_time': avg_processing_time,
            'avg_confidence_score': avg_confidence_score,
            'success_rate': len(successful_results) / len(results),
            'total_documents_processed': len(successful_results),
            'total_processing_time': total_time,
            'accuracy_metrics': accuracy_metrics
        }
    
    def _save_results(self, results: Dict[str, Any], filename: str):
        """Guarda los resultados en un archivo JSON"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            logger.info(f"Resultados guardados en {filename}")
        except Exception as e:
            logger.error(f"Error guardando resultados: {e}")
    
    def create_test_batch(self, 
                         source_directory: str, 
                         batch_size: int = 50,
                         output_file: str = "test_batch_paths.txt") -> List[str]:
        """
        Crea un lote de prueba con archivos de un directorio
        
        Args:
            source_directory: Directorio con archivos de prueba
            batch_size: Tamaño del lote
            output_file: Archivo donde guardar las rutas
            
        Returns:
            Lista de rutas de archivos
        """
        if not os.path.exists(source_directory):
            raise FileNotFoundError(f"Directorio no encontrado: {source_directory}")
        
        # Buscar archivos válidos
        valid_extensions = ['.jpg', '.jpeg', '.png', '.pdf']
        file_paths = []
        
        for ext in valid_extensions:
            pattern = f"**/*{ext}"
            files = list(Path(source_directory).glob(pattern))
            file_paths.extend([str(f) for f in files])
        
        # Limitar al tamaño del lote
        if len(file_paths) > batch_size:
            file_paths = file_paths[:batch_size]
        
        # Guardar rutas en archivo
        with open(output_file, 'w', encoding='utf-8') as f:
            for path in file_paths:
                f.write(f"{path}\n")
        
        logger.info(f"Lote de prueba creado con {len(file_paths)} archivos en {output_file}")
        
        return file_paths
    
    def load_ground_truth(self, ground_truth_file: str) -> Dict[str, Dict[str, Any]]:
        """
        Carga datos de verdad de campo desde un archivo JSON
        
        Args:
            ground_truth_file: Archivo JSON con ground truth
            
        Returns:
            Diccionario con ground truth por archivo
        """
        try:
            with open(ground_truth_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error cargando ground truth: {e}")
            return {}
    
    def generate_performance_report(self, batch_result: Dict[str, Any]) -> str:
        """
        Genera un reporte de rendimiento en texto
        
        Args:
            batch_result: Resultado del procesamiento del lote
            
        Returns:
            Reporte en formato texto
        """
        batch_info = batch_result['batch_info']
        performance = batch_result['performance_metrics']
        
        report = f"""
=== REPORTE DE RENDIMIENTO DEL MODELO ===
Fecha: {batch_info['timestamp']}

RESUMEN DEL LOTE:
- Total de archivos: {batch_info['total_files']}
- Archivos procesados exitosamente: {batch_info['successful_files']}
- Archivos fallidos: {batch_info['failed_files']}
- Tasa de éxito: {performance['success_rate']:.2%}
- Tiempo total de procesamiento: {batch_info['total_processing_time']:.2f} segundos

MÉTRICAS DE RENDIMIENTO:
- Throughput: {performance['throughput']:.2f} documentos/segundo
- Tiempo promedio por documento: {performance['avg_processing_time']:.2f} segundos
- Confidence Score promedio: {performance['avg_confidence_score']:.3f}

MÉTRICAS DE CALIDAD:
"""
        
        if performance.get('accuracy_metrics'):
            acc = performance['accuracy_metrics']
            report += f"""
- Precisión de campos promedio: {acc['avg_field_accuracy']:.3f}
- CER (Character Error Rate) promedio: {acc['avg_cer']:.3f}
- WER (Word Error Rate) promedio: {acc['avg_wer']:.3f}
- Total de campos evaluados: {acc['total_fields']}
- Campos correctos totales: {acc['total_correct_fields']}
- Campos faltantes totales: {acc['total_missing_fields']}
- Campos incorrectos totales: {acc['total_incorrect_fields']}
"""
        else:
            report += "- No se proporcionaron datos de ground truth para métricas de calidad\n"
        
        return report
