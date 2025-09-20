#!/usr/bin/env python3
"""
Generador de reporte detallado de análisis de campos
"""

import json
import os
import time
from typing import Dict, List, Any
from collections import defaultdict, Counter
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.metrics_calculator import MetricsCalculator

class FieldAnalysisReport:
    """Genera reportes detallados de análisis de campos"""
    
    def __init__(self):
        self.metrics_calculator = MetricsCalculator()
    
    def analyze_benchmark_results(self, benchmark_results_file: str) -> Dict[str, Any]:
        """
        Analiza los resultados del benchmark y genera estadísticas detalladas por campo
        
        Args:
            benchmark_results_file: Ruta al archivo JSON de resultados del benchmark
            
        Returns:
            Diccionario con análisis detallado por campo
        """
        with open(benchmark_results_file, 'r', encoding='utf-8') as f:
            benchmark_data = json.load(f)
        
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
                if result['success'] and result['metrics']:
                    doc_analysis = self._analyze_single_document(result)
                    analysis['document_analysis'].append(doc_analysis)
                    
                    # Agregar estadísticas por campo
                    for field_name, field_stats in doc_analysis['field_analysis'].items():
                        stats = analysis['field_statistics'][field_name]
                        stats['total_occurrences'] += 1
                        
                        if field_stats['status'] == 'correct':
                            stats['correct_matches'] += 1
                        elif field_stats['status'] == 'incorrect':
                            stats['incorrect_matches'] += 1
                            # Guardar ejemplo de error
                            if len(stats['error_examples']) < 5:  # Máximo 5 ejemplos por campo
                                stats['error_examples'].append({
                                    'document': result['filename'],
                                    'ground_truth': field_stats['ground_truth'],
                                    'extracted': field_stats['extracted']
                                })
                        elif field_stats['status'] == 'missing':
                            stats['missing_fields'] += 1
        
        # Calcular tasas de precisión por campo
        for field_name, stats in analysis['field_statistics'].items():
            if stats['total_occurrences'] > 0:
                stats['accuracy_rate'] = stats['correct_matches'] / stats['total_occurrences']
        
        # Generar resumen
        analysis['summary'] = self._generate_summary(analysis['field_statistics'])
        
        return analysis
    
    def _analyze_single_document(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analiza un documento individual
        
        Args:
            result: Resultado individual del benchmark
            
        Returns:
            Análisis detallado del documento
        """
        extracted_fields = result['extracted_fields']
        metrics = result['metrics']
        
        doc_analysis = {
            'filename': result['filename'],
            'confidence_score': metrics['confidence_score'],
            'field_accuracy': metrics['field_accuracy'],
            'field_analysis': {},
            'items_analysis': {}
        }
        
        # Analizar campos principales
        for field in self.metrics_calculator.structured_fields:
            doc_analysis['field_analysis'][field] = {
                'status': 'missing',
                'ground_truth': '',
                'extracted': '',
                'match': False
            }
            
            if field in extracted_fields:
                doc_analysis['field_analysis'][field]['extracted'] = str(extracted_fields[field])
                doc_analysis['field_analysis'][field]['status'] = 'extracted'
        
        # Analizar items
        items = extracted_fields.get('items', [])
        for i, item in enumerate(items):
            item_key = f"item_{i+1}"
            doc_analysis['items_analysis'][item_key] = {}
            
            for field in self.metrics_calculator.structured_item_fields:
                field_key = f"{item_key}_{field}"
                doc_analysis['items_analysis'][item_key][field] = {
                    'status': 'missing',
                    'ground_truth': '',
                    'extracted': '',
                    'match': False
                }
                
                if field in item:
                    doc_analysis['items_analysis'][item_key][field]['extracted'] = str(item[field])
                    doc_analysis['items_analysis'][item_key][field]['status'] = 'extracted'
        
        return doc_analysis
    
    def _generate_summary(self, field_statistics: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Genera resumen de estadísticas"""
        
        # Ordenar campos por tasa de precisión (peor primero)
        sorted_fields = sorted(
            field_statistics.items(),
            key=lambda x: x[1]['accuracy_rate']
        )
        
        worst_fields = sorted_fields[:5]  # Top 5 peores campos
        best_fields = sorted_fields[-5:]  # Top 5 mejores campos
        
        total_fields = len(field_statistics)
        avg_accuracy = sum(stats['accuracy_rate'] for stats in field_statistics.values()) / total_fields if total_fields > 0 else 0
        
        return {
            'total_fields_analyzed': total_fields,
            'average_accuracy': avg_accuracy,
            'worst_performing_fields': worst_fields,
            'best_performing_fields': best_fields
        }
    
    def generate_report(self, analysis: Dict[str, Any], output_file: str):
        """
        Genera reporte detallado en formato de texto
        
        Args:
            analysis: Análisis detallado
            output_file: Archivo de salida
        """
        report = f"""
=== REPORTE DETALLADO DE ANÁLISIS DE CAMPOS ===
Fecha: {time.strftime('%Y-%m-%d %H:%M:%S')}
Total de documentos analizados: {len(analysis['document_analysis'])}

RESUMEN EJECUTIVO:
{"=" * 50}
• Total de campos analizados: {analysis['summary']['total_fields_analyzed']}
• Precisión promedio: {analysis['summary']['average_accuracy']:.3f} ({analysis['summary']['average_accuracy']*100:.1f}%)

CAMPOS CON PEOR RENDIMIENTO:
{"=" * 50}
"""
        
        # Agregar campos con peor rendimiento
        for field_name, stats in analysis['summary']['worst_performing_fields']:
            report += f"""
• {field_name.upper()}:
  - Precisión: {stats['accuracy_rate']:.3f} ({stats['accuracy_rate']*100:.1f}%)
  - Total evaluado: {stats['total_occurrences']}
  - Correctos: {stats['correct_matches']}
  - Incorrectos: {stats['incorrect_matches']}
  - Faltantes: {stats['missing_fields']}
"""
            
            # Agregar ejemplos de errores
            if stats['error_examples']:
                report += "  - Ejemplos de errores:\n"
                for example in stats['error_examples'][:3]:  # Máximo 3 ejemplos
                    report += f"    * {example['document']}: '{example['extracted']}' vs '{example['ground_truth']}'\n"
        
        report += f"""
CAMPOS CON MEJOR RENDIMIENTO:
{"=" * 50}
"""
        
        # Agregar campos con mejor rendimiento
        for field_name, stats in analysis['summary']['best_performing_fields']:
            report += f"""
• {field_name.upper()}:
  - Precisión: {stats['accuracy_rate']:.3f} ({stats['accuracy_rate']*100:.1f}%)
  - Total evaluado: {stats['total_occurrences']}
  - Correctos: {stats['correct_matches']}
  - Incorrectos: {stats['incorrect_matches']}
  - Faltantes: {stats['missing_fields']}
"""
        
        report += f"""
ANÁLISIS DETALLADO POR CAMPO:
{"=" * 50}
"""
        
        # Agregar análisis detallado de todos los campos
        sorted_fields = sorted(
            analysis['field_statistics'].items(),
            key=lambda x: x[1]['accuracy_rate']
        )
        
        for field_name, stats in sorted_fields:
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
                report += "  Ejemplos de errores:\n"
                for example in stats['error_examples']:
                    report += f"    - {example['document']}: '{example['extracted']}' vs '{example['ground_truth']}'\n"
        
        report += f"""
ANÁLISIS POR DOCUMENTO:
{"=" * 50}
"""
        
        # Agregar análisis por documento (top 5 peores y mejores)
        doc_accuracies = [(doc['filename'], doc['field_accuracy']) for doc in analysis['document_analysis']]
        doc_accuracies.sort(key=lambda x: x[1])
        
        worst_docs = doc_accuracies[:5]
        best_docs = doc_accuracies[-5:]
        
        report += "Documentos con peor rendimiento:\n"
        for filename, accuracy in worst_docs:
            report += f"  - {filename}: {accuracy:.3f} ({accuracy*100:.1f}%)\n"
        
        report += "\nDocumentos con mejor rendimiento:\n"
        for filename, accuracy in best_docs:
            report += f"  - {filename}: {accuracy:.3f} ({accuracy*100:.1f}%)\n"
        
        report += f"""
RECOMENDACIONES:
{"=" * 50}
"""
        
        # Generar recomendaciones basadas en el análisis
        worst_field = analysis['summary']['worst_performing_fields'][0] if analysis['summary']['worst_performing_fields'] else None
        if worst_field:
            field_name, stats = worst_field
            report += f"• Priorizar mejora en el campo '{field_name}' (precisión: {stats['accuracy_rate']*100:.1f}%)\n"
            
            if stats['missing_fields'] > stats['incorrect_matches']:
                report += f"  - Problema principal: campos faltantes ({stats['missing_fields']} de {stats['total_occurrences']})\n"
                report += f"  - Recomendación: mejorar extracción/reconocimiento de este campo\n"
            else:
                report += f"  - Problema principal: campos incorrectos ({stats['incorrect_matches']} de {stats['total_occurrences']})\n"
                report += f"  - Recomendación: mejorar precisión de extracción o validación\n"
        
        avg_accuracy = analysis['summary']['average_accuracy']
        if avg_accuracy < 0.7:
            report += f"• Precisión general baja ({avg_accuracy*100:.1f}%): considerar mejoras en el modelo OCR\n"
        elif avg_accuracy < 0.9:
            report += f"• Precisión moderada ({avg_accuracy*100:.1f}%): hay margen de mejora en campos específicos\n"
        else:
            report += f"• Precisión excelente ({avg_accuracy*100:.1f}%): el modelo funciona muy bien\n"
        
        # Guardar reporte
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        return report

def main():
    """Función principal para generar el reporte"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generar reporte detallado de análisis de campos')
    parser.add_argument('--benchmark-file', default='benchmark_results/dataset_benchmark_results.json',
                       help='Archivo JSON de resultados del benchmark')
    parser.add_argument('--output', default='benchmark_results/field_analysis_report.txt',
                       help='Archivo de salida del reporte')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.benchmark_file):
        print(f"Error: No se encontró el archivo {args.benchmark_file}")
        return
    
    # Generar análisis
    analyzer = FieldAnalysisReport()
    analysis = analyzer.analyze_benchmark_results(args.benchmark_file)
    
    # Generar reporte
    report = analyzer.generate_report(analysis, args.output)
    
    print(f"Reporte generado exitosamente: {args.output}")
    print(f"Total de documentos analizados: {len(analysis['document_analysis'])}")
    print(f"Total de campos analizados: {analysis['summary']['total_fields_analyzed']}")
    print(f"Precisión promedio: {analysis['summary']['average_accuracy']:.3f}")

if __name__ == "__main__":
    main()
