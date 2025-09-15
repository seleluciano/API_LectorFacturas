import re
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class InvoiceParser:
    """Parser inteligente para extraer campos específicos de facturas"""
    
    def __init__(self):
        self.patterns = {
            # Campos para Factura según modelo Django
            'tipo_factura': [
                r'FACTU\s+([ABC])',
                r'Factura\s+([ABC])',
                r'Tipo:\s*([ABC])',
                r'([ABC])\s+[0-9]+'  # A 12345678
            ],
            'razon_social_vendedor': [
                r'Razón Social:\s*([A-Z][^CUIT]+?)(?=\s+CUIT)',
                r'([A-Z][a-z\s]+SRL|SA|LTD|INC)(?=\s+CUIT)',
                r'ORIGINAL\s+[ABC]\s*:\s*([A-Z][^|]+?)(?=\s*\|)',
                r'ORIGINAL\s+([A-Z][a-z\s]+SA|SRL)(?=\s+Le)',
                r'([A-Z][a-z\s]+SA|SRL)(?=\s+Le\s+PAGTURA)'
            ],
            'cuit_vendedor': [
                r'CUIT:\s*(\d{2}-\d{8}-\d{1})',
                r'CUIT\s*(\d{2}-\d{8}-\d{1})'
            ],
            'razon_social_comprador': [
                r'DNI:\s*[^A]+?Apellido y Nombre / Razón Social:\s*([A-ZÁÉÍÓÚÑ][a-záéíóúñ\s]+?)(?=\s+Domicilio)',
                r'Apellido y Nombre / Razón Social:\s*([A-ZÁÉÍÓÚÑ][a-záéíóúñ\s]+?)(?=\s+Domicilio)',
                r'Cliente:\s*([A-ZÁÉÍÓÚÑ][a-záéíóúñ\s]+?)(?=\s+Domicilio)',
                r'Comprador:\s*([A-ZÁÉÍÓÚÑ][a-záéíóúñ\s]+?)(?=\s+Domicilio)',
                r'([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)(?=\s+Domicilio)',  # Nombre Apellido
                r'DNI:\s*\d{2}-\d{8}-\d{1}\s+Apellido y Nombre / Razón Social:\s*([A-ZÁÉÍÓÚÑ][a-záéíóúñ\s]+?)(?=\s+Domicilio)'
            ],
            'cuit_comprador': [
                r'DNI:\s*(\d{2}-\d{8}-\d{1})',
                r'DNI\s*(\d{2}-\d{8}-\d{1})',
                r'CUIT Comprador:\s*(\d{2}-\d{8}-\d{1})'
            ],
            'condicion_iva_comprador': [
                r'Apellido y Nombre / Razón Social:\s*[^C]+?Condición frente al IVA:\s*([A-Z][a-z]+)(?=\s+Condici)',
                r'Domicilio:\s*[^C]+?Condición frente al IVA:\s*([A-Z][a-z]+)(?=\s+Condici)',
                r'DNI:\s*[^C]+?Condición frente al IVA:\s*([A-Z][a-z]+)(?=\s+Condici)',
                r'CUIT Comprador[^C]+?Condición frente al IVA:\s*([A-Z][a-z]+)(?=\s+Condici)'
            ],
            'condicion_venta': [
                r'Condici[oó]n de venta:\s*([A-Z][a-z\s]+)',
                r'Condici[oó]n venta:\s*([A-Z][a-z\s]+)',
                r'Venta:\s*([A-Z][a-z\s]+)'
            ],
            'fecha_emision': [
                r'Fecha de Emisión:\s*(\d{2}/\d{2}/\d{4})',
                r'Fecha:\s*(\d{2}/\d{2}/\d{4})',
                r'(\d{2}/\d{2}/\d{4})'
            ],
            'subtotal': [
                r'Subtotal:\s*\$([\d.,]+)',
                r'Subtotal\s*\$([\d.,]+)',
                r'Subtotal\s+([\d.,]+)'
            ],
            'importe_total': [
                r'Importe Total:\s*\$([\d.,]+)',
                r'Total:\s*\$([\d.,]+)',
                r'Importe Total\s+([\d.,]+)'
            ],
            'iva': [
                r'IVA:\s*\$([\d.,]+)',
                r'Impuesto IVA:\s*\$([\d.,]+)',
                r'IVA\s+([\d.,]+)'
            ],
            # Campos adicionales útiles
            'numero_factura': [
                r'Comp\. Nro:\s*(\d+)',
                r'Factura Nro:\s*(\d+)',
                r'Nro:\s*(\d+)',
                r'(\d{8,})'
            ],
            'punto_venta': [
                r'Punto de Venta:\s*(\d{4})',
                r'PV:\s*(\d{4})',
                r'Punto:\s*(\d{4})'
            ],
            # Patrones para items
            'items': [
                r'(\d+)\s+([^\d]+)\s+(\d+)\s+unidad\s+([\d.,]+)\s+(\d+%)\s+([\d.,]+)\s+([\d.,]+)',
                r'(\d+)\s+([^\d]+)\s+([\d.,]+)\s+([\d.,]+)'
            ]
        }
    
    def parse_invoice(self, text: str) -> Dict[str, Any]:
        """Extrae campos específicos de una factura"""
        try:
            # Limpiar el texto
            cleaned_text = self._clean_text(text)
            
            # Extraer campos
            extracted_fields = {}
            
            for field_name, patterns in self.patterns.items():
                value = self._extract_field(cleaned_text, patterns, field_name)
                if value:
                    extracted_fields[field_name] = value
            
            # Procesar items por separado
            items = self._extract_items(cleaned_text)
            if items:
                extracted_fields['items'] = items
            
            # Calcular deuda impositiva (importe_total - subtotal)
            logger.info(f"Campos extraídos para cálculo: {list(extracted_fields.keys())}")
            
            if 'importe_total' in extracted_fields and 'subtotal' in extracted_fields:
                try:
                    # Limpiar y convertir valores numéricos
                    importe_total_str = extracted_fields['importe_total'].replace('$', '').strip()
                    subtotal_str = extracted_fields['subtotal'].replace('$', '').strip()
                    
                    # Función para convertir cualquier formato a float
                    def parse_number(number_str):
                        # Remover espacios
                        number_str = number_str.strip()
                        
                        # Detectar formato automáticamente
                        if '.' in number_str and ',' in number_str:
                            # Tiene ambos separadores
                            # Determinar cuál es el separador decimal
                            last_dot = number_str.rfind('.')
                            last_comma = number_str.rfind(',')
                            
                            if last_comma > last_dot:
                                # Coma está después del último punto: 26.667,60 (formato argentino)
                                return float(number_str.replace('.', '').replace(',', '.'))
                            else:
                                # Punto está después de la última coma: 26,667.60 (formato americano)
                                return float(number_str.replace(',', ''))
                        elif ',' in number_str:
                            # Solo coma: 26667,60 (formato argentino)
                            return float(number_str.replace(',', '.'))
                        elif '.' in number_str:
                            # Solo punto: 26667.60 (formato americano)
                            return float(number_str)
                        else:
                            # Sin separadores: 26667
                            return float(number_str)
                    
                    importe_total = parse_number(importe_total_str)
                    subtotal = parse_number(subtotal_str)
                    deuda_impositiva = importe_total - subtotal
                    
                    # Formatear con comas como separador de miles (formato argentino)
                    extracted_fields['deuda_impositiva'] = f"{deuda_impositiva:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
                    
                    logger.info(f"Cálculo deuda impositiva: {importe_total} - {subtotal} = {deuda_impositiva}")
                    logger.info(f"Strings procesados: importe_total='{importe_total_str}' -> {importe_total}, subtotal='{subtotal_str}' -> {subtotal}")
                except (ValueError, AttributeError) as e:
                    logger.error(f"Error calculando deuda impositiva: {e}")
                    logger.error(f"Valores problemáticos: importe_total='{extracted_fields.get('importe_total')}', subtotal='{extracted_fields.get('subtotal')}'")
                    extracted_fields['deuda_impositiva'] = "0.00"
            else:
                logger.warning("No se encontraron importe_total o subtotal para calcular deuda impositiva")
                logger.warning(f"Campos disponibles: {list(extracted_fields.keys())}")
                extracted_fields['deuda_impositiva'] = "0.00"
            
            return {
                'success': True,
                'extracted_fields': extracted_fields,
                'raw_text': text,
                'parsing_confidence': self._calculate_confidence(extracted_fields)
            }
            
        except Exception as e:
            logger.error(f"Error parseando factura: {e}")
            return {
                'success': False,
                'error': str(e),
                'raw_text': text,
                'extracted_fields': {}
            }
    
    def _clean_text(self, text: str) -> str:
        """Limpia el texto para mejor parsing"""
        # Normalizar espacios y saltos de línea
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n+', '\n', text)
        return text.strip()
    
    def _extract_field(self, text: str, patterns: List[str], field_name: str) -> Optional[str]:
        """Extrae un campo específico usando múltiples patrones"""
        for pattern in patterns:
            try:
                match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
                if match:
                    value = match.group(1).strip()
                    
                    # Limpiar el valor extraído según el tipo de campo
                    if field_name in ['empresa', 'cliente', 'razon_social_vendedor', 'razon_social_comprador']:
                        # Para nombres y razones sociales, mantener letras (incluyendo acentos), espacios y algunos caracteres especiales
                        value = re.sub(r'[^a-zA-ZÁÉÍÓÚÑáéíóúñ\s]', '', value)
                        value = re.sub(r'\s+', ' ', value).strip()
                        # Limitar longitud para evitar texto extra
                        if len(value) > 50:
                            value = value[:50].strip()
                    elif field_name == 'domicilio_cliente':
                        # Para domicilios, mantener letras, números y espacios
                        value = re.sub(r'[^\w\s0-9]', '', value)
                        value = re.sub(r'\s+', ' ', value).strip()
                        # Limitar longitud
                        if len(value) > 40:
                            value = value[:40].strip()
                    else:
                        # Para otros campos, limpieza básica (mantener acentos)
                        value = re.sub(r'[^a-zA-ZÁÉÍÓÚÑáéíóúñ0-9\s\-.,/$%]', '', value)
                        value = re.sub(r'\s+', ' ', value).strip()
                    
                    if value and len(value) > 2:  # Filtrar valores muy cortos
                        return value
            except Exception as e:
                logger.debug(f"Error con patrón {pattern} para {field_name}: {e}")
                continue
        
        return None
    
    def _extract_items(self, text: str) -> List[Dict[str, str]]:
        """Extrae información de items de la factura según modelo ItemFactura"""
        items = []
        
        # Buscar patrones de productos en todo el texto
        # Formato: número descripción cantidad unidad precio porcentaje impuesto subtotal
        # Ejemplo: "1 Servicio de consultoria 1 unidad 10.000,00 14% 1.400,00 8.600,00"
        pattern = r'(\d+)\s+([A-Za-záéíóúñÁÉÍÓÚÑ\s]+?)\s+(\d+)\s+unidad\s+([\d.,]+)\s+(\d+%)\s+([\d.,]+)\s+([\d.,]+)'
        
        matches = re.findall(pattern, text)
        
        for match in matches:
            # Limpiar descripción
            descripcion = match[1].strip()
            # Remover palabras comunes que no son parte del nombre del producto
            descripcion = re.sub(r'\s+(de|del|la|el|y|con|para|en|por)\s+', ' ', descripcion, flags=re.IGNORECASE)
            descripcion = descripcion.strip()
            
            # Determinar código (usar número de línea como código si no hay código específico)
            codigo = match[0]  # Usar el número de línea como código
            
            items.append({
                'codigo': codigo,
                'descripcion': descripcion,
                'cantidad': match[2],
                'unidad_medida': 'unidad',
                'precio_unitario': match[3],
                'importe_bonificacion': match[5],  # impuesto_bonif
                'subtotal': match[6]
            })
        
        return items
    
    def _calculate_confidence(self, extracted_fields: Dict[str, Any]) -> float:
        """Calcula la confianza del parsing basado en campos extraídos"""
        if not extracted_fields:
            return 0.0
        
        # Campos críticos para facturas
        critical_fields = ['empresa', 'numero_factura', 'fecha', 'importe_total']
        found_critical = sum(1 for field in critical_fields if field in extracted_fields)
        
        # Campos adicionales
        additional_fields = ['cuit', 'cliente', 'iva', 'subtotal']
        found_additional = sum(1 for field in additional_fields if field in extracted_fields)
        
        # Calcular confianza
        confidence = (found_critical * 0.4 + found_additional * 0.15) / len(extracted_fields)
        return min(confidence, 1.0)
    
    def get_supported_fields(self) -> List[str]:
        """Retorna la lista de campos que puede extraer"""
        return list(self.patterns.keys()) + ['items', 'deuda_impositiva']
