#!/usr/bin/env python3
"""
Análisis detallado de campos con comparación real con ground truth
"""

import json
import os
import time
from typing import Dict, List, Any
from collections import defaultdict
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.metrics_calculator import MetricsCalculator

class DetailedFieldAnalysis:
    """Análisis detallado de campos con ground truth real"""
    
    def __init__(self):
        self.metrics_calculator = MetricsCalculator()
    
    def analyze_benchmark_with_ground_truth(self, benchmark_results_file: str, dataset_directory: str) -> Dict[str, Any]:
        """
        Analiza los resultados del benchmark comparando con ground truth real
        
        Args:
            benchmark_results_file: Ruta al archivo JSON de resultados del benchmark
            dataset_directory: Directorio del dataset con los JSONs de ground truth
            
        Returns:
            Diccionario con análisis detallado por campo
        """
        # Cargar resultados del benchmark
        with open(benchmark_results_file, 'r', encoding='utf-8') as f:
            benchmark_data = json.load(f)
        
        # Cargar ground truth real
        ground_truth_data = self._load_ground_truth_data(dataset_directory)
        
        analysis = {
            'field_statistics': defaultdict(lambda: {
                'total_occurrences': 0,
                'correct_matches': 0,
                'incorrect_matches': 0,
                'missing_fields': 0,
                'accuracy_rate': 0.0,
                'error_examples': []
            }),
            'document_analysis': [],
            'summary': {}
        }
        
        # Procesar cada documento individual
        for batch_size, batch_data in benchmark_data.items():
            individual_results = batch_data['batch_result']['individual_results']
            
            for result in individual_results:
                if result['success']:
                    filename = result['filename']
                    if filename in ground_truth_data:
                        doc_analysis = self._analyze_document_with_ground_truth(
                            result, ground_truth_data[filename]
                        )
                        analysis['document_analysis'].append(doc_analysis)
                        
                        # Agregar estadísticas por campo
                        self._update_field_statistics(analysis['field_statistics'], doc_analysis)
        
        # Calcular tasas de precisión por campo
        for field_name, stats in analysis['field_statistics'].items():
            if stats['total_occurrences'] > 0:
                stats['accuracy_rate'] = stats['correct_matches'] / stats['total_occurrences']
        
        # Generar resumen
        analysis['summary'] = self._generate_summary(analysis['field_statistics'])
        
        return analysis
    
    def _load_ground_truth_data(self, dataset_directory: str) -> Dict[str, Dict[str, Any]]:
        """Carga los datos de ground truth desde los JSONs del dataset"""
        ground_truth_data = {}
        
        for filename in os.listdir(dataset_directory):
            if filename.endswith('.json'):
                json_path = os.path.join(dataset_directory, filename)
                try:
                    with open(json_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # Crear nombre de imagen correspondiente
                    image_filename = filename.replace('.json', '.png')
                    ground_truth_data[image_filename] = data
                    
                except Exception as e:
                    print(f"Error cargando {json_path}: {e}")
        
        return ground_truth_data
    
    def _analyze_document_with_ground_truth(self, result: Dict[str, Any], ground_truth: Dict[str, Any]) -> Dict[str, Any]:
        """Analiza un documento comparando con ground truth real"""
        extracted_fields = result['extracted_fields']
        
        doc_analysis = {
            'filename': result['filename'],
            'confidence_score': result.get('metrics', {}).get('confidence_score', 0.0),
            'field_accuracy': result.get('metrics', {}).get('field_accuracy', 0.0),
            'field_analysis': {},
            'items_analysis': {}
        }
        
        # Analizar campos principales
        for field in self.metrics_calculator.structured_fields:
            if field in ground_truth and ground_truth[field]:
                ground_value = str(ground_truth[field]).strip().lower()
                extracted_value = str(extracted_fields.get(field, "")).strip().lower()
                
                match = self.metrics_calculator._fields_match(ground_value, extracted_value, field)
                
                doc_analysis['field_analysis'][field] = {
                    'status': 'correct' if match else 'incorrect',
                    'ground_truth': ground_value,
                    'extracted': extracted_value,
                    'match': match
                }
            else:
                doc_analysis['field_analysis'][field] = {
                    'status': 'missing',
                    'ground_truth': '',
                    'extracted': '',
                    'match': False
                }
        
        # Analizar items
        ground_items = ground_truth.get('items', [])
        extracted_items = extracted_fields.get('items', [])
        
        for i, ground_item in enumerate(ground_items):
            item_key = f"item_{i+1}"
            doc_analysis['items_analysis'][item_key] = {}
            
            # Buscar item correspondiente en extraídos
            extracted_item = extracted_items[i] if i < len(extracted_items) else {}
            
            for field in self.metrics_calculator.structured_item_fields:
                if field in ground_item and ground_item[field]:
                    ground_value = str(ground_item[field]).strip().lower()
                    extracted_value = str(extracted_item.get(field, "")).strip().lower()
                    
                    match = self.metrics_calculator._fields_match(ground_value, extracted_value, field)
                    
                    doc_analysis['items_analysis'][item_key][field] = {
                        'status': 'correct' if match else 'incorrect',
                        'ground_truth': ground_value,
                        'extracted': extracted_value,
                        'match': match
                    }
                else:
                    doc_analysis['items_analysis'][item_key][field] = {
                        'status': 'missing',
                        'ground_truth': '',
                        'extracted': '',
                        'match': False
                    }
        
        return doc_analysis
    
    def _update_field_statistics(self, field_statistics: Dict[str, Dict[str, Any]], doc_analysis: Dict[str, Any]):
        """Actualiza las estadísticas de campos con el análisis del documento"""
        
        # Actualizar campos principales
        for field_name, field_data in doc_analysis['field_analysis'].items():
            stats = field_statistics[field_name]
            stats['total_occurrences'] += 1
            
            if field_data['status'] == 'correct':
                stats['correct_matches'] += 1
            elif field_data['status'] == 'incorrect':
                stats['incorrect_matches'] += 1
                # Guardar ejemplo de error
                if len(stats['error_examples']) < 3:
                    stats['error_examples'].append({
                        'document': doc_analysis['filename'],
                        'ground_truth': field_data['ground_truth'],
                        'extracted': field_data['extracted']
                    })
            elif field_data['status'] == 'missing':
                stats['missing_fields'] += 1
        
        # Actualizar campos de items
        for item_key, item_data in doc_analysis['items_analysis'].items():
            for field_name, field_data in item_data.items():
                stats = field_statistics[field_name]
                stats['total_occurrences'] += 1
                
                if field_data['status'] == 'correct':
                    stats['correct_matches'] += 1
                elif field_data['status'] == 'incorrect':
                    stats['incorrect_matches'] += 1
                    # Guardar ejemplo de error
                    if len(stats['error_examples']) < 3:
                        stats['error_examples'].append({
                            'document': doc_analysis['filename'],
                            'ground_truth': field_data['ground_truth'],
                            'extracted': field_data['extracted']
                        })
                elif field_data['status'] == 'missing':
                    stats['missing_fields'] += 1
    
    def _generate_summary(self, field_statistics: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Genera resumen de estadísticas"""
        
        # Filtrar campos que realmente se evaluaron
        evaluated_fields = {k: v for k, v in field_statistics.items() if v['total_occurrences'] > 0}
        
        if not evaluated_fields:
            return {'total_fields_analyzed': 0, 'average_accuracy': 0.0, 'worst_performing_fields': [], 'best_performing_fields': []}
        
        # Ordenar campos por tasa de precisión (peor primero)
        sorted_fields = sorted(
            evaluated_fields.items(),
            key=lambda x: x[1]['accuracy_rate']
        )
        
        worst_fields = sorted_fields[:5]  # Top 5 peores campos
        best_fields = sorted_fields[-5:]  # Top 5 mejores campos
        
        total_fields = len(evaluated_fields)
        avg_accuracy = sum(stats['accuracy_rate'] for stats in evaluated_fields.values()) / total_fields
        
        return {
            'total_fields_analyzed': total_fields,
            'average_accuracy': avg_accuracy,
            'worst_performing_fields': worst_fields,
            'best_performing_fields': best_fields
        }
    
    def generate_detailed_report(self, analysis: Dict[str, Any], output_file: str):
        """Genera reporte detallado"""
        report = f"""
=== REPORTE DETALLADO DE ANÁLISIS DE CAMPOS ===
Fecha: {time.strftime('%Y-%m-%d %H:%M:%S')}
Total de documentos analizados: {len(analysis['document_analysis'])}

RESUMEN EJECUTIVO:
{"=" * 60}
• Total de campos analizados: {analysis['summary']['total_fields_analyzed']}
• Precisión promedio: {analysis['summary']['average_accuracy']:.3f} ({analysis['summary']['average_accuracy']*100:.1f}%)

CAMPOS CON PEOR RENDIMIENTO (Top 5):
{"=" * 60}
"""
        
        # Agregar campos con peor rendimiento
        for i, (field_name, stats) in enumerate(analysis['summary']['worst_performing_fields'], 1):
            report += f"""
{i}. {field_name.upper()}:
   Precisión: {stats['accuracy_rate']:.3f} ({stats['accuracy_rate']*100:.1f}%)
   Total evaluado: {stats['total_occurrences']}
   Correctos: {stats['correct_matches']} ({stats['correct_matches']/stats['total_occurrences']*100:.1f}%)
   Incorrectos: {stats['incorrect_matches']} ({stats['incorrect_matches']/stats['total_occurrences']*100:.1f}%)
   Faltantes: {stats['missing_fields']} ({stats['missing_fields']/stats['total_occurrences']*100:.1f}%)
"""
            
            # Agregar ejemplos de errores
            if stats['error_examples']:
                report += "   Ejemplos de errores:\n"
                for example in stats['error_examples']:
                    report += f"     • {example['document']}: '{example['extracted']}' vs '{example['ground_truth']}'\n"
        
        report += f"""
CAMPOS CON MEJOR RENDIMIENTO (Top 5):
{"=" * 60}
"""
        
        # Agregar campos con mejor rendimiento
        for i, (field_name, stats) in enumerate(analysis['summary']['best_performing_fields'], 1):
            report += f"""
{i}. {field_name.upper()}:
   Precisión: {stats['accuracy_rate']:.3f} ({stats['accuracy_rate']*100:.1f}%)
   Total evaluado: {stats['total_occurrences']}
   Correctos: {stats['correct_matches']} ({stats['correct_matches']/stats['total_occurrences']*100:.1f}%)
   Incorrectos: {stats['incorrect_matches']} ({stats['incorrect_matches']/stats['total_occurrences']*100:.1f}%)
   Faltantes: {stats['missing_fields']} ({stats['missing_fields']/stats['total_occurrences']*100:.1f}%)
"""
        
        report += f"""
ANÁLISIS COMPLETO POR CAMPO:
{"=" * 60}
"""
        
        # Agregar análisis completo de todos los campos
        sorted_fields = sorted(
            analysis['field_statistics'].items(),
            key=lambda x: x[1]['accuracy_rate']
        )
        
        for field_name, stats in sorted_fields:
            if stats['total_occurrences'] > 0:
                report += f"""
{field_name.upper()}:
   Precisión: {stats['accuracy_rate']:.3f} ({stats['accuracy_rate']*100:.1f}%)
   Total evaluado: {stats['total_occurrences']}
   Correctos: {stats['correct_matches']} ({stats['correct_matches']/stats['total_occurrences']*100:.1f}%)
   Incorrectos: {stats['incorrect_matches']} ({stats['incorrect_matches']/stats['total_occurrences']*100:.1f}%)
   Faltantes: {stats['missing_fields']} ({stats['missing_fields']/stats['total_occurrences']*100:.1f}%)
"""
                
                # Agregar ejemplos de errores si los hay
                if stats['error_examples']:
                    report += "   Ejemplos de errores:\n"
                    for example in stats['error_examples']:
                        report += f"     • {example['document']}: '{example['extracted']}' vs '{example['ground_truth']}'\n"
        
        report += f"""
ANÁLISIS POR DOCUMENTO:
{"=" * 60}
"""
        
        # Agregar análisis por documento
        doc_accuracies = [(doc['filename'], doc['field_accuracy']) for doc in analysis['document_analysis']]
        doc_accuracies.sort(key=lambda x: x[1])
        
        worst_docs = doc_accuracies[:5]
        best_docs = doc_accuracies[-5:]
        
        report += "Documentos con peor rendimiento:\n"
        for filename, accuracy in worst_docs:
            report += f"  • {filename}: {accuracy:.3f} ({accuracy*100:.1f}%)\n"
        
        report += "\nDocumentos con mejor rendimiento:\n"
        for filename, accuracy in best_docs:
            report += f"  • {filename}: {accuracy:.3f} ({accuracy*100:.1f}%)\n"
        
        report += f"""
RECOMENDACIONES ESPECÍFICAS:
{"=" * 60}
"""
        
        # Generar recomendaciones específicas
        worst_field = analysis['summary']['worst_performing_fields'][0] if analysis['summary']['worst_performing_fields'] else None
        if worst_field:
            field_name, stats = worst_field
            report += f"🎯 PRIORIDAD ALTA: Mejorar el campo '{field_name}'\n"
            report += f"   • Precisión actual: {stats['accuracy_rate']*100:.1f}%\n"
            report += f"   • Total evaluado: {stats['total_occurrences']} veces\n"
            
            if stats['missing_fields'] > stats['incorrect_matches']:
                report += f"   • Problema principal: CAMPOS FALTANTES ({stats['missing_fields']} de {stats['total_occurrences']})\n"
                report += f"   • Recomendación: Mejorar extracción/reconocimiento de este campo\n"
            else:
                report += f"   • Problema principal: CAMPOS INCORRECTOS ({stats['incorrect_matches']} de {stats['total_occurrences']})\n"
                report += f"   • Recomendación: Mejorar precisión de extracción o validación\n"
        
        avg_accuracy = analysis['summary']['average_accuracy']
        if avg_accuracy < 0.7:
            report += f"\n⚠️  PRECISIÓN GENERAL BAJA: {avg_accuracy*100:.1f}%\n"
            report += f"   • Recomendación: Considerar mejoras en el modelo OCR\n"
        elif avg_accuracy < 0.9:
            report += f"\n✅ PRECISIÓN MODERADA: {avg_accuracy*100:.1f}%\n"
            report += f"   • Recomendación: Enfocar mejoras en campos específicos\n"
        else:
            report += f"\n🎉 PRECISIÓN EXCELENTE: {avg_accuracy*100:.1f}%\n"
            report += f"   • El modelo funciona muy bien\n"
        
        # Guardar reporte
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        return report

def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Análisis detallado de campos con ground truth real')
    parser.add_argument('--benchmark-file', default='benchmark_results/dataset_benchmark_results.json',
                       help='Archivo JSON de resultados del benchmark')
    parser.add_argument('--dataset-dir', default=r'C:\Users\selel\OneDrive\Documentos\Facultad\ARPYME\creacion_dataset\dataset_facturas',
                       help='Directorio del dataset con JSONs de ground truth')
    parser.add_argument('--output', default='benchmark_results/detailed_field_analysis.txt',
                       help='Archivo de salida del reporte')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.benchmark_file):
        print(f"Error: No se encontró el archivo {args.benchmark_file}")
        return
    
    if not os.path.exists(args.dataset_dir):
        print(f"Error: No se encontró el directorio {args.dataset_dir}")
        return
    
    # Generar análisis
    analyzer = DetailedFieldAnalysis()
    analysis = analyzer.analyze_benchmark_with_ground_truth(args.benchmark_file, args.dataset_dir)
    
    # Generar reporte
    report = analyzer.generate_detailed_report(analysis, args.output)
    
    print(f"✅ Reporte detallado generado: {args.output}")
    print(f"📊 Total de documentos analizados: {len(analysis['document_analysis'])}")
    print(f"📋 Total de campos analizados: {analysis['summary']['total_fields_analyzed']}")
    print(f"🎯 Precisión promedio: {analysis['summary']['average_accuracy']:.3f} ({analysis['summary']['average_accuracy']*100:.1f}%)")
    
    if analysis['summary']['worst_performing_fields']:
        worst_field, worst_stats = analysis['summary']['worst_performing_fields'][0]
        print(f"⚠️  Campo con peor rendimiento: {worst_field} ({worst_stats['accuracy_rate']*100:.1f}%)")

if __name__ == "__main__":
    main()
