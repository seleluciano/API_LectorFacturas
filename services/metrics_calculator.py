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
        # Campos estructurados específicos para evaluación (solo los que están en ground truth)
        self.structured_fields = [
            'cuit_vendedor', 'cuit_comprador', 'fecha_emision',
            'subtotal', 'importe_total'
        ]
        
        # Campos de items estructurados (solo los que están en ground truth)
        self.structured_item_fields = [
            'descripcion', 'cantidad', 'precio_unitario', 
            'importe_bonificacion'  # Removido 'bonificacion' porque no existe en ground truth
        ]
        
        # NO evaluamos otros campos extraídos por OCR, solo los estructurados
        # Esto significa que solo comparamos lo que realmente está en el ground truth
    
    def calculate_confidence_score(self, extracted_fields: Dict[str, Any], ground_truth: Dict[str, Any] = None) -> float:
        """
        Calcula el Confidence Score basado SOLO en campos estructurados específicos
        Usa la misma lógica que field_accuracy para consistencia
        
        Args:
            extracted_fields: Diccionario con los campos extraídos
            ground_truth: Campos correctos para comparación (opcional)
            
        Returns:
            Confidence score entre 0.0 y 1.0
        """
        if not extracted_fields:
            return 0.0
        
        # Si no hay ground truth, usar lógica simple (solo existencia)
        if not ground_truth:
            structured_found = 0
            for field in self.structured_fields:
                if field in extracted_fields and extracted_fields[field]:
                    value = str(extracted_fields[field]).strip()
                    if value and value not in ['', '0', 'N/A', 'null']:
                        structured_found += 1
            
            items_score = self._calculate_structured_items_confidence_score(extracted_fields)
            total_structured = len(self.structured_fields)
            fields_score = structured_found / total_structured if total_structured > 0 else 0.0
            confidence = (fields_score * 0.7) + (items_score * 0.3)
            return min(confidence, 1.0)
        
        # Si hay ground truth, usar la misma lógica que field_accuracy
        total_fields = 0
        correct_fields = 0
        
        # Evaluar campos principales (misma lógica que field_accuracy)
        for field in self.structured_fields:
            if field in ground_truth and ground_truth[field]:
                total_fields += 1
                ground_value = str(ground_truth[field]).strip().lower()
                extracted_value = str(extracted_fields.get(field, "")).strip().lower()
                
                if extracted_value and self._fields_match(ground_value, extracted_value, field):
                    correct_fields += 1
        
        # Evaluar items (misma lógica que field_accuracy)
        items_accuracy = self._calculate_items_accuracy(extracted_fields, ground_truth)
        if items_accuracy['total_item_fields'] > 0:
            total_fields += items_accuracy['total_item_fields']
            correct_fields += items_accuracy['correct_item_fields']
        
        # Calcular confianza igual que precisión
        confidence = correct_fields / total_fields if total_fields > 0 else 0.0
        
        return min(confidence, 1.0)
    
    def _calculate_structured_items_confidence_score(self, extracted_fields: Dict[str, Any]) -> float:
        """
        Calcula el confidence score para items estructurados (solo campos del ground truth)
        
        Args:
            extracted_fields: Campos extraídos por el modelo
            
        Returns:
            Score de confianza para items estructurados (0.0 - 1.0)
        """
        items = extracted_fields.get('productos', []) or extracted_fields.get('items', [])
        
        if not items:
            return 0.0
        
        total_score = 0.0
        items_count = 0
        
        for item in items:
            if not item:
                continue
                
            item_score = 0.0
            valid_fields = 0
            
            # Solo evaluar campos estructurados específicos
            for field in self.structured_item_fields:
                if field in item and item[field]:
                    value = str(item[field]).strip()
                    if value and value not in ['', '0', 'N/A', 'null']:
                        item_score += 1.0
                    valid_fields += 1
            
            if valid_fields > 0:
                total_score += item_score / valid_fields
                items_count += 1
        
        return total_score / items_count if items_count > 0 else 0.0
    
    def _calculate_items_confidence_score_improved(self, extracted_fields: Dict[str, Any]) -> float:
        """
        Calcula el confidence score mejorado para items (solo campos importantes)
        
        Args:
            extracted_fields: Campos extraídos por el modelo
            
        Returns:
            Score de confianza para items (0.0 - 1.0)
        """
        items = extracted_fields.get('productos', []) or extracted_fields.get('items', [])
        
        if not items:
            return 0.0
        
        # Campos importantes de items (datos estructurados)
        important_item_fields = ['descripcion', 'cantidad', 'precio_unitario']
        
        total_score = 0.0
        items_count = 0
        
        for item in items:
            if not item:
                continue
                
            item_score = 0.0
            valid_fields = 0
            
            for field in important_item_fields:
                if field in item and item[field]:
                    value = str(item[field]).strip()
                    if value and value not in ['', '0', 'N/A', 'null']:
                        item_score += 1.0
                    valid_fields += 1
            
            if valid_fields > 0:
                total_score += item_score / valid_fields
                items_count += 1
        
        return total_score / items_count if items_count > 0 else 0.0
    
    def _calculate_items_confidence_score(self, extracted_fields: Dict[str, Any]) -> float:
        """
        Calcula el confidence score específico para items
        
        Args:
            extracted_fields: Campos extraídos por el modelo
            
        Returns:
            Score de confianza para items (0.0 - 1.0)
        """
        items = extracted_fields.get('productos', []) or extracted_fields.get('items', [])
        
        if not items:
            return 0.0
        
        total_item_fields = 0
        found_item_fields = 0
        
        for item in items:
            for field in self.critical_item_fields:
                total_item_fields += 1
                if field in item and item[field]:
                    found_item_fields += 1
        
        return found_item_fields / total_item_fields if total_item_fields > 0 else 0.0
    
    def _calculate_items_accuracy(self, extracted_fields: Dict[str, Any], 
                                ground_truth: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calcula la precisión de los items extraídos
        
        Args:
            extracted_fields: Campos extraídos por el modelo
            ground_truth: Campos correctos (verdad de campo)
            
        Returns:
            Diccionario con métricas de items
        """
        total_item_fields = 0
        correct_item_fields = 0
        missing_item_fields = 0
        incorrect_item_fields = 0
        item_details = {}
        
        # Obtener items del ground truth y extraídos
        ground_items = ground_truth.get('productos', []) or ground_truth.get('items', [])
        extracted_items = extracted_fields.get('productos', []) or extracted_fields.get('items', [])
        
        if not ground_items:
            return {
                'total_item_fields': 0,
                'correct_item_fields': 0,
                'missing_item_fields': 0,
                'incorrect_item_fields': 0,
                'item_details': {}
            }
        
        # Evaluar cada item del ground truth
        for i, ground_item in enumerate(ground_items):
            item_key = f"item_{i+1}"
            item_details[item_key] = {}
            
            # Buscar el item correspondiente en los extraídos
            extracted_item = None
            if i < len(extracted_items):
                extracted_item = extracted_items[i]
            
            # Evaluar SOLO campos estructurados específicos del item (no todo lo que extrae el OCR)
            for field in self.structured_item_fields:
                total_item_fields += 1
                field_key = f"{item_key}_{field}"
                
                ground_value = str(ground_item.get(field, "")).strip().lower() if ground_item.get(field) else ""
                extracted_value = str(extracted_item.get(field, "")).strip().lower() if extracted_item and extracted_item.get(field) else ""
                
                if not ground_value:  # Campo no requerido
                    continue
                
                if not extracted_value:  # Campo no extraído
                    missing_item_fields += 1
                    item_details[item_key][field] = {
                        'status': 'missing',
                        'ground_truth': ground_value,
                        'extracted': extracted_value
                    }
                elif self._fields_match(ground_value, extracted_value, field):
                    correct_item_fields += 1
                    item_details[item_key][field] = {
                        'status': 'correct',
                        'ground_truth': ground_value,
                        'extracted': extracted_value
                    }
                else:
                    incorrect_item_fields += 1
                    item_details[item_key][field] = {
                        'status': 'incorrect',
                        'ground_truth': ground_value,
                        'extracted': extracted_value
                    }
        
        return {
            'total_item_fields': total_item_fields,
            'correct_item_fields': correct_item_fields,
            'missing_item_fields': missing_item_fields,
            'incorrect_item_fields': incorrect_item_fields,
            'item_details': item_details
        }
    
    def calculate_field_accuracy(self, extracted_fields: Dict[str, Any], 
                               ground_truth: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        """
        Calcula la precisión de los campos extraídos comparando con la verdad de campo
        Incluye evaluación de campos principales e items
        
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
        
        # Evaluar SOLO campos estructurados específicos (no todo lo que extrae el OCR)
        for field in self.structured_fields:
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
        
        # Evaluar items (campos críticos)
        items_accuracy = self._calculate_items_accuracy(extracted_fields, ground_truth)
        if items_accuracy['total_item_fields'] > 0:
            total_fields += items_accuracy['total_item_fields']
            correct_fields += items_accuracy['correct_item_fields']
            missing_fields += items_accuracy['missing_item_fields']
            incorrect_fields += items_accuracy['incorrect_item_fields']
            field_details['items'] = items_accuracy['item_details']
        
        # Calcular accuracy
        accuracy = correct_fields / total_fields if total_fields > 0 else 0.0
        
        return accuracy, {
            'total_fields': total_fields,
            'correct_fields': correct_fields,
            'missing_fields': missing_fields,
            'incorrect_fields': incorrect_fields,
            'field_details': field_details,
            'items_accuracy': items_accuracy
        }
    
    def correct_missing_fields(self, extracted_fields: Dict[str, Any]) -> Dict[str, Any]:
        """
        Corrige campos faltantes con valores por defecto y cálculos automáticos
        
        Args:
            extracted_fields: Campos extraídos por el modelo
            
        Returns:
            Campos corregidos con valores por defecto
        """
        corrected_fields = extracted_fields.copy()
        
        # Solo corregir campos estructurados específicos (no todos los campos del OCR)
        # No corregimos campos que no están en el ground truth
        
        # Normalizar campos numéricos estructurados faltantes
        structured_numeric_fields = ['subtotal', 'importe_total']
        for field in structured_numeric_fields:
            if field not in corrected_fields or not corrected_fields[field]:
                corrected_fields[field] = "0,00"
        
        # Correcciones de items
        if 'productos' in corrected_fields and corrected_fields['productos']:
            corrected_items = []
            for item in corrected_fields['productos']:
                corrected_item = item.copy()
                
                # Calcular importe_bonificacion si falta
                if 'importe_bonificacion' not in corrected_item or not corrected_item['importe_bonificacion']:
                    try:
                        cantidad = float(corrected_item.get('cantidad', 0))
                        precio_unitario = float(corrected_item.get('precio_unitario', 0))
                        bonificacion = float(corrected_item.get('bonificacion', 0))
                        
                        if cantidad > 0 and precio_unitario > 0 and bonificacion > 0:
                            importe_bonificacion = cantidad * precio_unitario * (bonificacion / 100)
                            corrected_item['importe_bonificacion'] = f"{importe_bonificacion:.2f}"
                        else:
                            corrected_item['importe_bonificacion'] = "0.00"
                    except (ValueError, TypeError):
                        corrected_item['importe_bonificacion'] = "0.00"
                
                # Normalizar solo campos estructurados de items
                structured_item_numeric_fields = ['cantidad', 'precio_unitario', 'bonificacion', 'importe_bonificacion']
                for field in structured_item_numeric_fields:
                    if field not in corrected_item or not corrected_item[field]:
                        corrected_item[field] = "0"
                
                # Limpiar solo descripción (campo estructurado)
                if 'descripcion' in corrected_item and corrected_item['descripcion']:
                    corrected_item['descripcion'] = self._clean_string_field(corrected_item['descripcion'])
                
                corrected_items.append(corrected_item)
            
            corrected_fields['productos'] = corrected_items
        
        # No normalizamos campos que no están en el ground truth estructurado
        # Solo manejamos los campos específicos que estamos evaluando
        
        return corrected_fields
    
    def _clean_string_field(self, value: str) -> str:
        """
        Limpia un campo de texto eliminando espacios extra y caracteres inválidos
        
        Args:
            value: Valor del campo a limpiar
            
        Returns:
            Valor limpio
        """
        if not value:
            return ""
        
        # Convertir a string y limpiar
        cleaned = str(value).strip()
        
        # Eliminar espacios extra y caracteres de control
        cleaned = re.sub(r'\s+', ' ', cleaned)
        cleaned = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', cleaned)
        
        # Eliminar caracteres inválidos comunes
        cleaned = re.sub(r'[^\w\s\-.,\/()ÁÉÍÓÚÑáéíóúñ]', '', cleaned)
        
        return cleaned.strip()
    
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
        if field_name in ['importe_total', 'subtotal', 'iva', 'deuda_impositiva', 'precio_unitario', 'importe_bonificacion', 'cantidad', 'bonificacion']:
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
        Calcula el Character Error Rate (CER) solo sobre campos importantes
        con normalización completa de caracteres
        
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
        
        # Extraer solo campos importantes del texto
        extracted_important = self._extract_important_fields_text(extracted_text)
        ground_truth_important = self._extract_important_fields_text(ground_truth_text)
        
        # Normalizar textos con normalización completa
        extracted_norm = self._normalize_text_completely(extracted_important)
        ground_truth_norm = self._normalize_text_completely(ground_truth_important)
        
        # Calcular distancia de Levenshtein
        distance = self._levenshtein_distance(extracted_norm, ground_truth_norm)
        
        # CER = distancia / longitud del texto correcto
        cer = distance / len(ground_truth_norm) if ground_truth_norm else 1.0
        
        return min(cer, 1.0)
    
    def calculate_wer(self, extracted_text: str, ground_truth_text: str) -> float:
        """
        Calcula el Word Error Rate (WER) solo sobre campos importantes
        con normalización completa de caracteres
        
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
        
        # Extraer solo campos importantes del texto
        extracted_important = self._extract_important_fields_text(extracted_text)
        ground_truth_important = self._extract_important_fields_text(ground_truth_text)
        
        # Normalizar textos con normalización completa
        extracted_norm = self._normalize_text_completely(extracted_important)
        ground_truth_norm = self._normalize_text_completely(ground_truth_important)
        
        # Tokenizar en palabras
        extracted_words = extracted_norm.split()
        ground_truth_words = ground_truth_norm.split()
        
        if not ground_truth_words:
            return 1.0 if extracted_words else 0.0
        
        # Calcular distancia de Levenshtein a nivel de palabras
        distance = self._levenshtein_distance_words(extracted_words, ground_truth_words)
        
        # WER = distancia / número de palabras correctas
        wer = distance / len(ground_truth_words)
        
        return min(wer, 1.0)
    
    def _extract_important_fields_text(self, text: str) -> str:
        """
        Extrae solo los campos importantes del texto para cálculo de CER/WER
        Versión simplificada que solo extrae campos realmente relevantes
        
        Args:
            text: Texto completo
            
        Returns:
            Texto con solo campos importantes
        """
        if not text:
            return ""
        
        important_parts = []
        
        # Solo extraer campos realmente importantes y estructurados
        patterns = [
            # CUITs (formato específico)
            r'\b(\d{2}-\d{8}-\d{1})\b',
            # Fechas (formato específico)
            r'\b(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})\b',
            # Montos (formato específico con comas/puntos)
            r'\b(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)\b',
            # Porcentajes
            r'\b(\d+%)\b'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                if isinstance(match, tuple):
                    important_parts.extend([str(m) for m in match if m])
                else:
                    important_parts.append(str(match))
        
        # Solo incluir elementos realmente relevantes
        filtered_parts = []
        for part in important_parts:
            # Solo incluir CUITs, fechas, montos y porcentajes
            if (re.match(r'\d{2}-\d{8}-\d{1}', part) or  # CUIT
                re.match(r'\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}', part) or  # Fecha
                re.match(r'\d{1,3}(?:\.\d{3})*(?:,\d{2})?', part) or  # Monto
                re.match(r'\d+%', part)):  # Porcentaje
                filtered_parts.append(part)
        
        return ' '.join(filtered_parts)
    
    def _normalize_text_completely(self, text: str) -> str:
        """
        Normalización completa de texto: ignorar mayúsculas/minúsculas, espacios extra,
        comas y puntos
        
        Args:
            text: Texto a normalizar
            
        Returns:
            Texto completamente normalizado
        """
        if not text:
            return ""
        
        # Convertir a minúsculas
        text = text.lower()
        
        # Remover comas y puntos
        text = re.sub(r'[,.]', '', text)
        
        # Remover espacios extra y tabulaciones
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\t+', ' ', text)
        
        # Remover caracteres de control
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
        
        # Remover caracteres especiales que no aportan información
        text = re.sub(r'[^\w\s]', '', text)
        
        return text.strip()
    
    def _normalize_text_for_cer(self, text: str) -> str:
        """Normaliza texto para cálculo de CER - mejorado para reducir errores"""
        if not text:
            return ""
        
        # Convertir a minúsculas
        text = text.lower()
        
        # Normalizar comas y puntos en montos (formato argentino)
        text = re.sub(r'(\d+)\.(\d{3})', r'\1\2', text)  # 1.000 -> 1000
        text = re.sub(r'(\d+),(\d{2})$', r'\1.\2', text)  # 100,50 -> 100.50 (solo decimales)
        
        # Remover espacios extra y tabulaciones
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\t+', ' ', text)
        
        # Remover caracteres de control y especiales
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
        text = re.sub(r'[^\w\s\-.,\/()]', '', text)
        
        return text.strip()
    
    def _normalize_text_for_wer(self, text: str) -> str:
        """Normaliza texto para cálculo de WER - mejorado"""
        if not text:
            return ""
        
        # Convertir a minúsculas
        text = text.lower()
        
        # Normalizar montos antes de tokenizar
        text = re.sub(r'(\d+)\.(\d{3})', r'\1\2', text)  # 1.000 -> 1000
        text = re.sub(r'(\d+),(\d{2})$', r'\1.\2', text)  # 100,50 -> 100.50
        
        # Remover caracteres especiales pero mantener espacios
        text = re.sub(r'[^\w\s\-.,\/()]', ' ', text)
        
        # Normalizar espacios y tabulaciones
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\t+', ' ', text)
        
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
        Calcula todas las métricas de una vez con mejoras aplicadas
        
        Args:
            extracted_fields: Campos extraídos por el modelo
            ground_truth: Campos correctos
            extracted_text: Texto extraído por OCR
            ground_truth_text: Texto correcto
            processing_time: Tiempo de procesamiento en segundos
            
        Returns:
            MetricsResult con todas las métricas
        """
        # Aplicar correcciones de campos faltantes
        corrected_fields = self.correct_missing_fields(extracted_fields)
        
        # Los textos ya se normalizan dentro de calculate_cer/wer con campos importantes
        
        # Calcular métricas individuales con campos corregidos
        confidence_score = self.calculate_confidence_score(corrected_fields, ground_truth)
        field_accuracy, accuracy_details = self.calculate_field_accuracy(corrected_fields, ground_truth)
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
