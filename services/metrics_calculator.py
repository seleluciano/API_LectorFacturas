"""
Sistema de métricas para evaluación del modelo de parsing de facturas
"""
import time
import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from difflib import SequenceMatcher
import statistics

logger = logging.getLogger(__name__)

@dataclass
class MetricsResult:
    """Resultado de las métricas calculadas"""
    confidence_score: float
    field_accuracy: float
    cer: float  # Character Error Rate
    wer: float  # Word Error Rate
    processing_latency: float  # Tiempo de procesamiento en segundos
    throughput: float  # Documentos por segundo
    total_fields: int
    correct_fields: int
    missing_fields: int
    incorrect_fields: int

class MetricsCalculator:
    """Calculadora de métricas para el modelo de parsing de facturas"""
    
    def __init__(self):
        # Campos críticos para el cálculo de accuracy
        self.critical_fields = [
            'tipo_factura', 'razon_social_vendedor', 'cuit_vendedor',
            'razon_social_comprador', 'cuit_comprador', 'fecha_emision',
            'importe_total', 'subtotal'
        ]
        
        # Campos adicionales
        self.additional_fields = [
            'numero_factura', 'punto_venta', 'condicion_iva_comprador',
            'condicion_venta', 'iva', 'deuda_impositiva'
        ]
        
        # Todos los campos
        self.all_fields = self.critical_fields + self.additional_fields
    
    def calculate_confidence_score(self, extracted_fields: Dict[str, Any]) -> float:
        """
        Calcula el Confidence Score basado en la cantidad y calidad de campos extraídos
        
        Args:
            extracted_fields: Diccionario con los campos extraídos
            
        Returns:
            Confidence score entre 0.0 y 1.0
        """
        if not extracted_fields:
            return 0.0
        
        # Peso de campos críticos vs adicionales
        critical_weight = 0.7
        additional_weight = 0.3
        
        # Contar campos críticos encontrados
        critical_found = sum(1 for field in self.critical_fields if field in extracted_fields and extracted_fields[field])
        critical_score = critical_found / len(self.critical_fields)
        
        # Contar campos adicionales encontrados
        additional_found = sum(1 for field in self.additional_fields if field in extracted_fields and extracted_fields[field])
        additional_score = additional_found / len(self.additional_fields)
        
        # Calcular score ponderado
        confidence = (critical_score * critical_weight) + (additional_score * additional_weight)
        
        # Bonus por items extraídos
        if 'items' in extracted_fields and extracted_fields['items']:
            items_count = len(extracted_fields['items']) if isinstance(extracted_fields['items'], list) else 1
            items_bonus = min(0.1, items_count * 0.02)  # Máximo 10% de bonus
            confidence += items_bonus
        
        return min(confidence, 1.0)
    
    def calculate_field_accuracy(self, extracted_fields: Dict[str, Any], 
                               ground_truth: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        """
        Calcula la precisión de los campos extraídos comparando con la verdad de campo
        
        Args:
            extracted_fields: Campos extraídos por el modelo
            ground_truth: Campos correctos (verdad de campo)
            
        Returns:
            Tuple con (accuracy, detalles)
        """
        if not ground_truth:
            return 0.0, {}
        
        total_fields = 0
        correct_fields = 0
        missing_fields = 0
        incorrect_fields = 0
        field_details = {}
        
        for field in self.all_fields:
            if field in ground_truth:
                total_fields += 1
                ground_value = str(ground_truth[field]).strip().lower() if ground_truth[field] else ""
                extracted_value = str(extracted_fields.get(field, "")).strip().lower() if extracted_fields.get(field) else ""
                
                if not ground_value:  # Campo no requerido en ground truth
                    continue
                
                if not extracted_value:  # Campo no extraído
                    missing_fields += 1
                    field_details[field] = {
                        'status': 'missing',
                        'ground_truth': ground_value,
                        'extracted': extracted_value
                    }
                elif self._fields_match(ground_value, extracted_value, field):
                    correct_fields += 1
                    field_details[field] = {
                        'status': 'correct',
                        'ground_truth': ground_value,
                        'extracted': extracted_value
                    }
                else:
                    incorrect_fields += 1
                    field_details[field] = {
                        'status': 'incorrect',
                        'ground_truth': ground_value,
                        'extracted': extracted_value
                    }
        
        # Calcular accuracy
        accuracy = correct_fields / total_fields if total_fields > 0 else 0.0
        
        return accuracy, {
            'total_fields': total_fields,
            'correct_fields': correct_fields,
            'missing_fields': missing_fields,
            'incorrect_fields': incorrect_fields,
            'field_details': field_details
        }
    
    def _fields_match(self, ground_value: str, extracted_value: str, field_name: str) -> bool:
        """
        Determina si dos valores de campo coinciden, considerando el tipo de campo
        
        Args:
            ground_value: Valor correcto
            extracted_value: Valor extraído
            field_name: Nombre del campo
            
        Returns:
            True si los valores coinciden
        """
        if not ground_value or not extracted_value:
            return ground_value == extracted_value
        
        # Normalizar valores
        ground_clean = self._normalize_field_value(ground_value, field_name)
        extracted_clean = self._normalize_field_value(extracted_value, field_name)
        
        # Para campos numéricos, comparar valores numéricos
        if field_name in ['importe_total', 'subtotal', 'iva', 'deuda_impositiva']:
            try:
                ground_num = self._parse_numeric_value(ground_clean)
                extracted_num = self._parse_numeric_value(extracted_clean)
                return abs(ground_num - extracted_num) < 0.01  # Tolerancia de 1 centavo
            except:
                return ground_clean == extracted_clean
        
        # Para CUIT, comparar solo números
        elif field_name in ['cuit_vendedor', 'cuit_comprador']:
            ground_digits = re.sub(r'\D', '', ground_clean)
            extracted_digits = re.sub(r'\D', '', extracted_clean)
            return ground_digits == extracted_digits
        
        # Para fechas, normalizar formato
        elif field_name == 'fecha_emision':
            return self._dates_match(ground_clean, extracted_clean)
        
        # Para otros campos, usar similitud de texto
        else:
            similarity = SequenceMatcher(None, ground_clean, extracted_clean).ratio()
            return similarity >= 0.8  # 80% de similitud
    
    def _normalize_field_value(self, value: str, field_name: str) -> str:
        """Normaliza un valor de campo para comparación"""
        value = value.strip().lower()
        
        # Remover caracteres especiales comunes
        value = re.sub(r'[^\w\s\-.,]', '', value)
        value = re.sub(r'\s+', ' ', value)
        
        return value
    
    def _parse_numeric_value(self, value: str) -> float:
        """Convierte un valor de texto a número"""
        # Remover símbolos de moneda y espacios
        value = re.sub(r'[^\d.,]', '', value)
        
        # Detectar formato (argentino vs americano)
        if '.' in value and ',' in value:
            # Tiene ambos separadores
            last_dot = value.rfind('.')
            last_comma = value.rfind(',')
            
            if last_comma > last_dot:
                # Formato argentino: 26.667,60
                return float(value.replace('.', '').replace(',', '.'))
            else:
                # Formato americano: 26,667.60
                return float(value.replace(',', ''))
        elif ',' in value:
            # Solo coma: formato argentino
            return float(value.replace(',', '.'))
        else:
            # Solo punto o sin separadores
            return float(value)
    
    def _dates_match(self, date1: str, date2: str) -> bool:
        """Compara dos fechas en diferentes formatos"""
        try:
            # Normalizar fechas
            date1_norm = self._normalize_date(date1)
            date2_norm = self._normalize_date(date2)
            return date1_norm == date2_norm
        except:
            return date1 == date2
    
    def _normalize_date(self, date_str: str) -> str:
        """Normaliza una fecha a formato YYYY-MM-DD"""
        # Remover caracteres no numéricos excepto separadores
        date_clean = re.sub(r'[^\d/\-.]', '', date_str)
        
        # Detectar formato y normalizar
        if '/' in date_clean:
            parts = date_clean.split('/')
        elif '-' in date_clean:
            parts = date_clean.split('-')
        elif '.' in date_clean:
            parts = date_clean.split('.')
        else:
            return date_str
        
        if len(parts) == 3:
            # Asumir formato DD/MM/YYYY o MM/DD/YYYY
            day, month, year = parts
            
            # Normalizar año a 4 dígitos
            if len(year) == 2:
                year = '20' + year if int(year) < 50 else '19' + year
            
            # Asumir formato DD/MM/YYYY (más común en Argentina)
            return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        
        return date_str
    
    def calculate_cer(self, extracted_text: str, ground_truth_text: str) -> float:
        """
        Calcula el Character Error Rate (CER)
        
        Args:
            extracted_text: Texto extraído por OCR
            ground_truth_text: Texto correcto
            
        Returns:
            CER entre 0.0 y 1.0 (0 = perfecto, 1 = todos los caracteres incorrectos)
        """
        if not ground_truth_text:
            return 1.0 if extracted_text else 0.0
        
        if not extracted_text:
            return 1.0
        
        # Normalizar textos
        extracted_norm = self._normalize_text_for_cer(extracted_text)
        ground_truth_norm = self._normalize_text_for_cer(ground_truth_text)
        
        # Calcular distancia de Levenshtein
        distance = self._levenshtein_distance(extracted_norm, ground_truth_norm)
        
        # CER = distancia / longitud del texto correcto
        cer = distance / len(ground_truth_norm) if ground_truth_norm else 1.0
        
        return min(cer, 1.0)
    
    def calculate_wer(self, extracted_text: str, ground_truth_text: str) -> float:
        """
        Calcula el Word Error Rate (WER)
        
        Args:
            extracted_text: Texto extraído por OCR
            ground_truth_text: Texto correcto
            
        Returns:
            WER entre 0.0 y 1.0 (0 = perfecto, 1 = todas las palabras incorrectas)
        """
        if not ground_truth_text:
            return 1.0 if extracted_text else 0.0
        
        if not extracted_text:
            return 1.0
        
        # Tokenizar en palabras
        extracted_words = self._normalize_text_for_wer(extracted_text).split()
        ground_truth_words = self._normalize_text_for_wer(ground_truth_text).split()
        
        if not ground_truth_words:
            return 1.0 if extracted_words else 0.0
        
        # Calcular distancia de Levenshtein a nivel de palabras
        distance = self._levenshtein_distance_words(extracted_words, ground_truth_words)
        
        # WER = distancia / número de palabras correctas
        wer = distance / len(ground_truth_words)
        
        return min(wer, 1.0)
    
    def _normalize_text_for_cer(self, text: str) -> str:
        """Normaliza texto para cálculo de CER"""
        # Convertir a minúsculas
        text = text.lower()
        
        # Remover espacios extra
        text = re.sub(r'\s+', ' ', text)
        
        # Remover caracteres especiales que no afectan la legibilidad
        text = re.sub(r'[^\w\s]', '', text)
        
        return text.strip()
    
    def _normalize_text_for_wer(self, text: str) -> str:
        """Normaliza texto para cálculo de WER"""
        # Convertir a minúsculas
        text = text.lower()
        
        # Remover caracteres especiales
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Normalizar espacios
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """Calcula la distancia de Levenshtein entre dos strings"""
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    def _levenshtein_distance_words(self, words1: List[str], words2: List[str]) -> int:
        """Calcula la distancia de Levenshtein entre dos listas de palabras"""
        if len(words1) < len(words2):
            return self._levenshtein_distance_words(words2, words1)
        
        if len(words2) == 0:
            return len(words1)
        
        previous_row = list(range(len(words2) + 1))
        for i, word1 in enumerate(words1):
            current_row = [i + 1]
            for j, word2 in enumerate(words2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (word1 != word2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    def calculate_processing_metrics(self, processing_times: List[float]) -> Dict[str, float]:
        """
        Calcula métricas de rendimiento de procesamiento
        
        Args:
            processing_times: Lista de tiempos de procesamiento en segundos
            
        Returns:
            Diccionario con métricas de rendimiento
        """
        if not processing_times:
            return {
                'avg_latency': 0.0,
                'min_latency': 0.0,
                'max_latency': 0.0,
                'median_latency': 0.0,
                'std_latency': 0.0,
                'throughput': 0.0
            }
        
        avg_latency = statistics.mean(processing_times)
        min_latency = min(processing_times)
        max_latency = max(processing_times)
        median_latency = statistics.median(processing_times)
        std_latency = statistics.stdev(processing_times) if len(processing_times) > 1 else 0.0
        
        # Throughput = documentos por segundo
        throughput = 1.0 / avg_latency if avg_latency > 0 else 0.0
        
        return {
            'avg_latency': avg_latency,
            'min_latency': min_latency,
            'max_latency': max_latency,
            'median_latency': median_latency,
            'std_latency': std_latency,
            'throughput': throughput
        }
    
    def calculate_comprehensive_metrics(self, 
                                      extracted_fields: Dict[str, Any],
                                      ground_truth: Dict[str, Any],
                                      extracted_text: str,
                                      ground_truth_text: str,
                                      processing_time: float) -> MetricsResult:
        """
        Calcula todas las métricas de una vez
        
        Args:
            extracted_fields: Campos extraídos por el modelo
            ground_truth: Campos correctos
            extracted_text: Texto extraído por OCR
            ground_truth_text: Texto correcto
            processing_time: Tiempo de procesamiento en segundos
            
        Returns:
            MetricsResult con todas las métricas
        """
        # Calcular métricas individuales
        confidence_score = self.calculate_confidence_score(extracted_fields)
        field_accuracy, accuracy_details = self.calculate_field_accuracy(extracted_fields, ground_truth)
        cer = self.calculate_cer(extracted_text, ground_truth_text)
        wer = self.calculate_wer(extracted_text, ground_truth_text)
        
        # Calcular throughput
        throughput = 1.0 / processing_time if processing_time > 0 else 0.0
        
        return MetricsResult(
            confidence_score=confidence_score,
            field_accuracy=field_accuracy,
            cer=cer,
            wer=wer,
            processing_latency=processing_time,
            throughput=throughput,
            total_fields=accuracy_details.get('total_fields', 0),
            correct_fields=accuracy_details.get('correct_fields', 0),
            missing_fields=accuracy_details.get('missing_fields', 0),
            incorrect_fields=accuracy_details.get('incorrect_fields', 0)
        )
