import re
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class InvoiceParser:
    """Parser inteligente para extraer campos específicos de facturas"""
    
    def __init__(self):
        self.patterns = {
            # Campos para Factura según modelo Django - Patrones genéricos
            'tipo_factura': [
                r'FACTU\s*([ABC])',
                r'Factura\s*([ABC])',
                r'Tipo\s*[:\s]*([ABC])',
                r'([ABC])\s*[:\s]*\d+',  # A: 12345678 o A 12345678
                r'Comprobante\s*([ABC])',
                r'([ABC])\s*-\s*\d+',  # A-12345678
                # Patrones específicos para formato "ORIGINAL : A"
                r'ORIGINAL\s*:\s*([ABC])',
                r'ORIGINAL\s+([ABC])',
                # Patrón para detectar en el texto completo
                r'([ABC])\s+[A-Za-z\s]+S[AR]L?\s+coo\.\d+',
                # Patrón más general
                r'([ABC])\s+(?:Soluciones|Global|Network)',
                # Patrones para facturas argentinas - Asumir A por defecto si no se especifica
                r'(?:ORIGINAL|FACTURA|Comprobante)\s*(?:[ABC])?\s*(?:[A-Za-z\s]+S[AR]L?)?',
                # Patrón para detectar "A" después de ORIGINAL
                r'ORIGINAL\s*[:\s]*A\s+[A-Za-z\s]+S[AR]L?'
            ],
            'razon_social_vendedor': [
                # Patrones específicos para formato "ORIGINAL" mejorados
                r'ORIGINAL\s+[ABC]?\s*[:\s]*([A-Za-zÁÉÍÓÚÑáéíóúñ\s\.\,]+?)(?=\s+(?:Le|CUIT|Fecha|coo\.|PAGTURA))',
                r'ORIGINAL\s+[ABC]?\s*[:\s]*([A-Za-zÁÉÍÓÚÑáéíóúñ\s\.\,]+?)(?=\s+coo\.\d+)',
                # Patrones genéricos para razón social del vendedor
                r'Razón\s+Social\s*[:\s]*([A-Za-zÁÉÍÓÚÑáéíóúñ\s\.\,]+?)(?=\s+(?:CUIT|Fecha|Domicilio|Ingresos))',
                r'Empresa\s*[:\s]*([A-Za-zÁÉÍÓÚÑáéíóúñ\s\.\,]+?)(?=\s+(?:CUIT|Fecha|Domicilio))',
                r'Proveedor\s*[:\s]*([A-Za-zÁÉÍÓÚÑáéíóúñ\s\.\,]+?)(?=\s+(?:CUIT|Fecha|Domicilio))',
                r'Vendedor\s*[:\s]*([A-Za-zÁÉÍÓÚÑáéíóúñ\s\.\,]+?)(?=\s+(?:CUIT|Fecha|Domicilio))',
                # Patrones específicos para tipos de empresa
                r'([A-Za-zÁÉÍÓÚÑáéíóúñ\s\.\,]+(?:SRL|SA|LTD|INC|S\.A\.|S\.R\.L\.))(?=\s+(?:CUIT|Fecha|Domicilio))',
                # Patrón para facturas con formato específico argentino
                r'([A-Za-zÁÉÍÓÚÑáéíóúñ\s\.\,]+S[AR]L?)(?=\s+(?:coo\.|Le\s+PAGTURA|CUIT))'
            ],
            'cuit_vendedor': [
                r'CUIT\s*[:\s]*(\d{2}-\d{8}-\d{1})',
                r'CUIT\s+(\d{2}-\d{8}-\d{1})',
                r'C\.U\.I\.T\.\s*[:\s]*(\d{2}-\d{8}-\d{1})',
                r'(\d{2}-\d{8}-\d{1})(?=\s+(?:Ingresos|Fecha|Domicilio))'
            ],
            'razon_social_comprador': [
                # Patrones específicos para formato con DNI mejorados
                r'DNI\s*[:\s]*\d{2}-\d{8}-\d{1}\s+(?:Apellido\s+y\s+Nombre\s*\/\s*)?(?:Razón\s+Social\s*[:\s]*)?([A-Za-zÁÉÍÓÚÑáéíóúñ\s\.\,]+?)(?=\s+(?:Domicilio|Condición|CUIT|Condición\s+frente))',
                r'Apellido\s+y\s+Nombre\s*\/\s*Razón\s+Social\s*[:\s]*([A-Za-zÁÉÍÓÚÑáéíóúñ\s\.\,]+?)(?=\s+(?:Domicilio|Condición|CUIT))',
                # Patrones genéricos para cliente/comprador
                r'Cliente\s*[:\s]*([A-Za-zÁÉÍÓÚÑáéíóúñ\s\.\,]+?)(?=\s+(?:CUIT|DNI|Domicilio|Condición))',
                r'Comprador\s*[:\s]*([A-Za-zÁÉÍÓÚÑáéíóúñ\s\.\,]+?)(?=\s+(?:CUIT|DNI|Domicilio|Condición))',
                r'Adquiriente\s*[:\s]*([A-Za-zÁÉÍÓÚÑáéíóúñ\s\.\,]+?)(?=\s+(?:CUIT|DNI|Domicilio|Condición))',
                # Patrón genérico para nombres propios (mejorado)
                r'([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)(?=\s+(?:Domicilio|Condición|CUIT|Condición\s+frente))',
                # Patrón específico para formato argentino
                r'([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)(?=\s+(?:Condición\s+frente\s+al\s+IVA|Domicilio))'
            ],
            'cuit_comprador': [
                r'DNI\s*[:\s]*(\d{2}-\d{8}-\d{1})',
                r'CUIT\s+(?:Comprador|Cliente)\s*[:\s]*(\d{2}-\d{8}-\d{1})',
                r'C\.U\.I\.T\.\s+(?:Comprador|Cliente)\s*[:\s]*(\d{2}-\d{8}-\d{1})'
            ],
            'condicion_iva_comprador': [
                # Patrones específicos para el comprador (después del DNI)
                r'DNI\s*[:\s]*\d{2}-\d{8}-\d{1}.*?Condici[oó]n\s+(?:frente\s+al\s+)?IVA\s*[:\s]*([A-Za-zÁÉÍÓÚÑáéíóúñ\s]+?)(?=\s+(?:Domicilio|Condición|$))',
                # Patrones más específicos para facturas argentinas
                r'Apellido\s+y\s+Nombre.*?Condici[oó]n\s+(?:frente\s+al\s+)?IVA\s*[:\s]*([A-Za-zÁÉÍÓÚÑáéíóúñ\s]+?)(?=\s+(?:Domicilio|Condición|$))',
                r'Razón\s+Social.*?Condici[oó]n\s+(?:frente\s+al\s+)?IVA\s*[:\s]*([A-Za-zÁÉÍÓÚÑáéíóúñ\s]+?)(?=\s+(?:Domicilio|Condición|$))',
                # Patrones genéricos mejorados
                r'Condici[oó]n\s+(?:frente\s+al\s+)?IVA\s*[:\s]*([A-Za-zÁÉÍÓÚÑáéíóúñ\s]+?)(?=\s+(?:Domicilio|Condición|Fecha|Venta|$))',
                r'IVA\s*[:\s]*([A-Za-zÁÉÍÓÚÑáéíóúñ\s]+?)(?=\s+(?:Domicilio|Condición|Fecha|Venta|$))',
                r'Tipo\s+de\s+IVA\s*[:\s]*([A-Za-zÁÉÍÓÚÑáéíóúñ\s]+?)(?=\s+(?:Domicilio|Condición|Fecha|Venta|$))',
                # Patrones específicos para condiciones comunes
                r'(Responsable\s+Inscripto|Monotributista|Exento|No\s+Responsable|Consumidor\s+Final)(?=\s+(?:Domicilio|Condición|Venta|$))',
                # Patrón para detectar después de datos del comprador
                r'[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+.*?Condici[oó]n\s+(?:frente\s+al\s+)?IVA\s*[:\s]*([A-Za-zÁÉÍÓÚÑáéíóúñ\s]+?)(?=\s+(?:Domicilio|Condición|Venta|$))'
            ],
            'condicion_venta': [
                # Patrones específicos para condición de venta después de datos del comprador
                r'DNI\s*[:\s]*\d{2}-\d{8}-\d{1}.*?Condici[oó]n\s+(?:de\s+)?venta\s*[:\s]*([A-Za-zÁÉÍÓÚÑáéíóúñ\s]+?)(?=\s+(?:\[|Producto|$))',
                r'Apellido\s+y\s+Nombre.*?Condici[oó]n\s+(?:de\s+)?venta\s*[:\s]*([A-Za-zÁÉÍÓÚÑáéíóúñ\s]+?)(?=\s+(?:\[|Producto|$))',
                r'Razón\s+Social.*?Condici[oó]n\s+(?:de\s+)?venta\s*[:\s]*([A-Za-zÁÉÍÓÚÑáéíóúñ\s]+?)(?=\s+(?:\[|Producto|$))',
                # Patrones genéricos mejorados
                r'Condici[oó]n\s+(?:de\s+)?venta\s*[:\s]*([A-Za-zÁÉÍÓÚÑáéíóúñ\s]+?)(?=\s+(?:\[|Producto|$|\n|[A-Z]))',
                r'Forma\s+de\s+pago\s*[:\s]*([A-Za-zÁÉÍÓÚÑáéíóúñ\s]+?)(?=\s+(?:\[|Producto|$|\n|[A-Z]))',
                r'Pago\s*[:\s]*([A-Za-zÁÉÍÓÚÑáéíóúñ\s]+?)(?=\s+(?:\[|Producto|$|\n|[A-Z]))',
                r'Venta\s*[:\s]*([A-Za-zÁÉÍÓÚÑáéíóúñ\s]+?)(?=\s+(?:\[|Producto|$|\n|[A-Z]))',
                # Patrones específicos para condiciones comunes
                r'(Contado|Crédito|Transferencia|Efectivo|Tarjeta|Cheque)(?=\s+(?:\[|Producto|$|\n|[A-Z]))',
                # Patrones más directos
                r'(?:Condición de venta|Condición venta)\s*[:\s]*(Contado|Crédito|Transferencia|Efectivo)',
                # Patrón para detectar después de datos del comprador
                r'[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+.*?Condici[oó]n\s+(?:de\s+)?venta\s*[:\s]*([A-Za-zÁÉÍÓÚÑáéíóúñ\s]+?)(?=\s+(?:\[|Producto|$))'
            ],
            'fecha_emision': [
                r'Fecha\s+(?:de\s+)?(?:Emisión|Factura)\s*[:\s]*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})',
                r'Fecha\s*[:\s]*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})',
                r'Emisión\s*[:\s]*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})',
                r'(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})(?=\s+(?:$|\n|[A-Za-z]))'
            ],
            'subtotal': [
                r'Subtotal\s*[:\s]*\$?\s*([\d.,]+)(?=\s+(?:Importe|Total|$|\n))',
                r'Sub\s+total\s*[:\s]*\$?\s*([\d.,]+)(?=\s+(?:Importe|Total|$|\n))',
                r'Sub\s*[:\s]*\$?\s*([\d.,]+)(?=\s+(?:Importe|Total|$|\n))',
                r'Neto\s*[:\s]*\$?\s*([\d.,]+)(?=\s+(?:Importe|Total|$|\n))',
                r'Base\s+imponible\s*[:\s]*\$?\s*([\d.,]+)(?=\s+(?:Importe|Total|$|\n))',
                # Patrones específicos para formato argentino
                r'Subtotal\s*[:\s]*\$?\s*([\d.,]+)(?=\s+(?:Importe\s+Otros|IVA|Percepción))',
                r'Neto\s*[:\s]*\$?\s*([\d.,]+)(?=\s+(?:Importe\s+Otros|IVA|Percepción))'
            ],
            'importe_total': [
                r'Importe\s+Total\s*[:\s]*\$?\s*([\d.,]+)',
                r'Total\s*[:\s]*\$?\s*([\d.,]+)',
                r'Monto\s+Total\s*[:\s]*\$?\s*([\d.,]+)',
                r'Total\s+a\s+pagar\s*[:\s]*\$?\s*([\d.,]+)',
                r'Importe\s*[:\s]*\$?\s*([\d.,]+)',
                # Patrones específicos para formato argentino
                r'Importe\s+Total\s*[:\s]*\$?\s*([\d.,]+)(?=\s+(?:5165247793596|Fecha\s+de\s+Vto|CAE|$))',
                r'Total\s*[:\s]*\$?\s*([\d.,]+)(?=\s+(?:5165247793596|Fecha\s+de\s+Vto|CAE|$))'
            ],
            'iva': [
                r'IVA\s*[:\s]*\$?\s*([\d.,]+)(?=\s+(?:Subtotal|Total|$|\n))',
                r'Impuesto\s+IVA\s*[:\s]*\$?\s*([\d.,]+)(?=\s+(?:Subtotal|Total|$|\n))',
                r'Impuesto\s+al\s+Valor\s+Agregado\s*[:\s]*\$?\s*([\d.,]+)(?=\s+(?:Subtotal|Total|$|\n))',
                r'Imp\.\s+IVA\s*[:\s]*\$?\s*([\d.,]+)(?=\s+(?:Subtotal|Total|$|\n))',
                r'21%\s*[:\s]*\$?\s*([\d.,]+)(?=\s+(?:Subtotal|Total|$|\n))',
                # Patrones específicos para formato argentino
                r'IVA\s*[:\s]*\$?\s*([\d.,]+)(?=\s+(?:Subtotal|Importe\s+Otros|Percepción|$))',
                r'IVA\s*[:\s]*\$?([\d.,]+)(?=\s+(?:Subtotal|Importe\s+Otros|Percepción|$))'
            ],
            # Campos adicionales útiles - Patrones genéricos
            'numero_factura': [
                r'(?:Comp|Comprobante)\.?\s*(?:Nro|Número|Nº)\s*[:\s]*(\d+)',
                r'Factura\s+(?:Nro|Número|Nº)\s*[:\s]*(\d+)',
                r'Nro\s*[:\s]*(\d+)',
                r'Número\s*[:\s]*(\d+)',
                r'Nº\s*[:\s]*(\d+)',
                r'(\d{6,})'  # Números largos (6+ dígitos)
            ],
            'punto_venta': [
                r'Punto\s+(?:de\s+)?Venta\s*[:\s]*(\d{1,5})',
                r'PV\s*[:\s]*(\d{1,5})',
                r'Punto\s*[:\s]*(\d{1,5})',
                r'Sucursal\s*[:\s]*(\d{1,5})',
                r'(\d{1,5})(?=\s+(?:Comp|Factura|Nro))'
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
            
            # Lógica especial para tipo_factura si no se detecta
            if 'tipo_factura' not in extracted_fields:
                # Si no se detecta el tipo, asumir "A" por defecto para facturas argentinas
                if any(keyword in cleaned_text for keyword in ['ORIGINAL', 'FACTURA', 'Comprobante']):
                    extracted_fields['tipo_factura'] = 'A'
                    logger.info("Tipo de factura no detectado, asumiendo 'A' por defecto")
            
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
                    elif field_name in ['condicion_iva_comprador', 'condicion_venta']:
                        # Para condiciones, limpieza específica
                        value = re.sub(r'[^a-zA-ZÁÉÍÓÚÑáéíóúñ\s]', '', value)
                        value = re.sub(r'\s+', ' ', value).strip()
                        # Normalizar valores comunes
                        if field_name == 'condicion_iva_comprador':
                            # Normalizar condiciones IVA
                            value_lower = value.lower()
                            if 'responsable' in value_lower and 'inscripto' in value_lower:
                                value = 'Responsable Inscripto'
                            elif 'monotributista' in value_lower:
                                value = 'Monotributista'
                            elif 'exento' in value_lower:
                                value = 'Exento'
                            elif 'no responsable' in value_lower:
                                value = 'No Responsable'
                            elif 'consumidor final' in value_lower:
                                value = 'Consumidor Final'
                        elif field_name == 'condicion_venta':
                            # Normalizar condiciones de venta
                            value_lower = value.lower()
                            if 'contado' in value_lower:
                                value = 'Contado'
                            elif 'crédito' in value_lower or 'credito' in value_lower:
                                value = 'Crédito'
                            elif 'transferencia' in value_lower:
                                value = 'Transferencia'
                            elif 'efectivo' in value_lower:
                                value = 'Efectivo'
                            elif 'tarjeta' in value_lower:
                                value = 'Tarjeta'
                            elif 'cheque' in value_lower:
                                value = 'Cheque'
                        # Limitar longitud
                        if len(value) > 30:
                            value = value[:30].strip()
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
        
        # Debug: Log del texto para análisis
        logger.info(f"Extrayendo items del texto: {text[:500]}...")
        
        # Buscar patrones de productos en todo el texto - Patrones genéricos
        # Formatos soportados:
        # 1. "1 Servicio de consultoria 1 unidad 10.000,00 14% 1.400,00 8.600,00"
        # 2. "3 Licencia software unidad 3.000,00 10% 600,00 5.400,00" (sin cantidad visible)
        # 3. "1 Producto $100,00 x 2 = $200,00"
        # 4. "Item 1: Descripción - Cantidad: 5 - Precio: $50,00"
        
        # Patrones para diferentes formatos de items - Optimizados para facturas argentinas
        patterns_items = [
            # Patrón principal completo: código descripción cantidad unidad precio % bonificación importe_bonificación subtotal
            r'(\d+)\s+([A-Za-záéíóúñÁÉÍÓÚÑ\s\-\.]{3,}?)\s+(\d+)\s+unidad\s+([\d.,]+)\s+(\d+%)\s+([\d.,]+)\s+([\d.,]+)',
            # Patrón sin subtotal: código descripción cantidad unidad precio % bonificación importe_bonificación
            r'(\d+)\s+([A-Za-záéíóúñÁÉÍÓÚÑ\s\-\.]{3,}?)\s+(\d+)\s+unidad\s+([\d.,]+)\s+(\d+%)\s+([\d.,]+)',
            # Patrón sin bonificación (0%): código descripción cantidad unidad precio 0% subtotal
            r'(\d+)\s+([A-Za-záéíóúñÁÉÍÓÚÑ\s\-\.]{3,}?)\s+(\d+)\s+unidad\s+([\d.,]+)\s+0%\s+([\d.,]+)',
            # Patrón simple sin unidad: código descripción cantidad precio
            r'(\d+)\s+([A-Za-záéíóúñÁÉÍÓÚÑ\s\-\.]{3,}?)\s+(\d+)\s+([\d.,]+)',
            # Patrón con descripciones más largas (5+ caracteres)
            r'(\d+)\s+([A-Za-záéíóúñÁÉÍÓÚÑ\s\-\.]{5,}?)\s+(\d+)\s+unidad\s+([\d.,]+)\s+(\d+%)\s+([\d.,]+)\s+([\d.,]+)',
            # Patrón alternativo sin "unidad": código descripción cantidad precio % bonificación
            r'(\d+)\s+([A-Za-záéíóúñÁÉÍÓÚÑ\s\-\.]{3,}?)\s+(\d+)\s+([\d.,]+)\s+(\d+%)\s+([\d.,]+)',
            # Patrón muy flexible: código descripción cantidad precio
            r'(\d+)\s+([A-Za-záéíóúñÁÉÍÓÚÑ\s\-\.]{2,}?)\s+(\d+)\s+([\d.,]+)',
            # NUEVO: Patrón para "y unidad" (error de OCR, asumir cantidad = 1)
            r'(\d+)\s+([A-Za-záéíóúñÁÉÍÓÚÑ\s\-\.]{3,}?)\s+y\s+unidad\s+([\d.,]+)\s+(\d+%)\s+([\d.,]+)\s+([\d.,]+)'
        ]
        
        # Procesar cada patrón de items y evitar duplicados
        processed_items = set()
        
        for pattern_idx, pattern in enumerate(patterns_items):
            matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
            logger.info(f"Patrón {pattern_idx + 1}: Encontrados {len(matches)} matches")
            
            for match in matches:
                logger.info(f"Match encontrado: {match}")
                item = self._process_item_match_generic(match, pattern_idx)
                if item:
                    logger.info(f"Item procesado: {item}")
                    if self._is_valid_item(item):
                        # Crear clave única para evitar duplicados
                        item_key = f"{item['codigo']}_{item['descripcion'][:30]}_{item['cantidad']}_{item['precio_unitario']}"
                        if item_key not in processed_items:
                            processed_items.add(item_key)
                            items.append(item)
                            logger.info(f"Item agregado: {item}")
                        else:
                            logger.info(f"Item duplicado, omitido: {item}")
                    else:
                        logger.info(f"Item no válido: {item}")
                else:
                    logger.info(f"No se pudo procesar el match: {match}")
        
        logger.info(f"Total items extraídos: {len(items)}")
        return items
    
    def _process_item_match_generic(self, match, pattern_idx):
        """Procesa un match de item según el patrón usado"""
        try:
            if pattern_idx == 0:  # Patrón completo con todos los campos
                return {
                    'codigo': match[0],
                    'descripcion': self._clean_item_description(match[1]),
                    'cantidad': match[2],
                    'unidad_medida': 'unidad',
                    'precio_unitario': match[3],
                    'bonificacion': match[4],
                    'importe_bonificacion': match[5],
                    'subtotal': match[6]
                }
            elif pattern_idx == 1:  # Patrón sin subtotal
                return {
                    'codigo': match[0],
                    'descripcion': self._clean_item_description(match[1]),
                    'cantidad': match[2],
                    'unidad_medida': 'unidad',
                    'precio_unitario': match[3],
                    'bonificacion': match[4],
                    'importe_bonificacion': match[5],
                    'subtotal': '0.00'
                }
            elif pattern_idx == 2:  # Patrón sin bonificación (0%)
                return {
                    'codigo': match[0],
                    'descripcion': self._clean_item_description(match[1]),
                    'cantidad': match[2],
                    'unidad_medida': 'unidad',
                    'precio_unitario': match[3],
                    'bonificacion': '0%',
                    'importe_bonificacion': '0.00',
                    'subtotal': match[4]
                }
            elif pattern_idx == 3:  # Patrón simple sin unidad
                return {
                    'codigo': match[0],
                    'descripcion': self._clean_item_description(match[1]),
                    'cantidad': match[2],
                    'unidad_medida': 'unidad',
                    'precio_unitario': match[3],
                    'bonificacion': '0%',
                    'importe_bonificacion': '0.00',
                    'subtotal': '0.00'
                }
            elif pattern_idx == 4:  # Patrón con descripciones largas (completo)
                return {
                    'codigo': match[0],
                    'descripcion': self._clean_item_description(match[1]),
                    'cantidad': match[2],
                    'unidad_medida': 'unidad',
                    'precio_unitario': match[3],
                    'bonificacion': match[4],
                    'importe_bonificacion': match[5],
                    'subtotal': match[6]
                }
            elif pattern_idx == 5:  # Patrón sin unidad pero con bonificación
                return {
                    'codigo': match[0],
                    'descripcion': self._clean_item_description(match[1]),
                    'cantidad': match[2],
                    'unidad_medida': 'unidad',
                    'precio_unitario': match[3],
                    'bonificacion': match[4],
                    'importe_bonificacion': match[5],
                    'subtotal': '0.00'
                }
            elif pattern_idx == 6:  # Patrón muy flexible
                return {
                    'codigo': match[0],
                    'descripcion': self._clean_item_description(match[1]),
                    'cantidad': match[2],
                    'unidad_medida': 'unidad',
                    'precio_unitario': match[3],
                    'bonificacion': '0%',
                    'importe_bonificacion': '0.00',
                    'subtotal': '0.00'
                }
            elif pattern_idx == 7:  # Patrón "y unidad" (sin cantidad explícita)
                return {
                    'codigo': match[0],
                    'descripcion': self._clean_item_description(match[1]),
                    'cantidad': '1',  # Asumir cantidad 1 cuando no está explícita
                    'unidad_medida': 'unidad',
                    'precio_unitario': match[2],
                    'bonificacion': match[3],
                    'importe_bonificacion': match[4],
                    'subtotal': match[5]
                }
        except (ValueError, IndexError) as e:
            logger.debug(f"Error procesando item match: {e}")
            return None
        
        return None
    
    def _clean_item_description(self, description):
        """Limpia la descripción del item"""
        # Remover palabras comunes que no son parte del nombre del producto
        description = re.sub(r'\s+(de|del|la|el|y|con|para|en|por)\s+', ' ', description, flags=re.IGNORECASE)
        description = re.sub(r'\s+', ' ', description).strip()
        return description
    
    def _is_valid_item(self, item):
        """Valida que el item tenga información mínima requerida"""
        descripcion = item.get('descripcion', '').strip()
        
        # Validaciones más flexibles para mejorar detección
        return (item.get('codigo') and 
                descripcion and 
                len(descripcion) > 2 and  # Descripción debe tener al menos 3 caracteres
                not descripcion.lower() in ['unidad', 'item', 'producto', 'servicio', 'cantidad', 'medida', 'precio', 'total', 'bonificación', 'subtotal'],  # Evitar palabras genéricas
                item.get('precio_unitario') and
                item.get('cantidad') and
                # Verificar que el código sea un número válido
                item.get('codigo', '').isdigit() and
                # Verificar que la cantidad sea un número válido
                item.get('cantidad', '').isdigit() and
                # Validar que no sea solo números
                not descripcion.isdigit() and
                # Asegurar que la descripción no sea solo espacios o caracteres especiales
                len(descripcion.replace(' ', '').replace('-', '').replace('.', '')) > 2 and
                # Verificar que el precio sea válido (no vacío y no solo caracteres especiales)
                item.get('precio_unitario', '').replace(',', '').replace('.', '').isdigit() and
                # Evitar items que sean solo códigos o números
                not descripcion.lower() in [item.get('codigo', ''), item.get('cantidad', ''), item.get('precio_unitario', '')])
    
    def _process_item_match(self, match, has_quantity=True):
        """Procesa un match de item y retorna el diccionario correspondiente"""
        if has_quantity:
            # Formato: código, descripción, cantidad, precio, porcentaje, impuesto, subtotal
            codigo = match[0]
            descripcion = match[1].strip()
            cantidad = match[2]
            precio_unitario = match[3]
            importe_bonificacion = match[5]
            subtotal = match[6]
        else:
            # Formato: código, descripción, precio, porcentaje, impuesto, subtotal (cantidad = 1)
            codigo = match[0]
            descripcion = match[1].strip()
            cantidad = "1"  # Asumir cantidad 1
            precio_unitario = match[2]
            importe_bonificacion = match[4]
            subtotal = match[5]
        
        # Limpiar descripción
            descripcion = re.sub(r'\s+(de|del|la|el|y|con|para|en|por)\s+', ' ', descripcion, flags=re.IGNORECASE)
            descripcion = descripcion.strip()
            
        return {
                'codigo': codigo,
                'descripcion': descripcion,
            'cantidad': cantidad,
                'unidad_medida': 'unidad',
            'precio_unitario': precio_unitario,
            'importe_bonificacion': importe_bonificacion,
            'subtotal': subtotal
        }
    
    def _calculate_confidence(self, extracted_fields: Dict[str, Any]) -> float:
        """Calcula la confianza del parsing basado en campos extraídos"""
        if not extracted_fields:
            return 0.0
        
        # Campos críticos para facturas (usando nombres correctos del parser)
        critical_fields = ['razon_social_vendedor', 'numero_factura', 'fecha_emision', 'importe_total']
        found_critical = sum(1 for field in critical_fields if field in extracted_fields)
        
        # Campos adicionales (usando nombres correctos del parser)
        additional_fields = ['cuit_vendedor', 'razon_social_comprador', 'subtotal', 'tipo_factura']
        found_additional = sum(1 for field in additional_fields if field in extracted_fields)
        
        # Calcular confianza
        if len(extracted_fields) == 0:
            return 0.0
        
        confidence = (found_critical * 0.4 + found_additional * 0.15) / len(extracted_fields)
        return min(confidence, 1.0)
    
    def parse_multiple_invoices(self, text: str) -> Dict[str, Any]:
        """Extrae múltiples facturas del texto y las procesa por separado"""
        try:
            # Detectar separadores entre facturas
            invoice_separators = self._detect_invoice_separators(text)
            
            if len(invoice_separators) <= 1:
                # Solo hay una factura, procesar normalmente
                single_result = self.parse_invoice(text)
                
                # Verificar si realmente se detectó una factura válida
                if single_result.get('success', False) and single_result.get('extracted_fields'):
                    return {
                        'success': True,
                        'invoices': [single_result],
                        'total_invoices': 1,
                        'raw_text': text
                    }
                else:
                    # No se detectó una factura válida
                    return {
                        'success': False,
                        'invoices': [],
                        'total_invoices': 0,
                        'raw_text': text,
                        'error': 'No se detectó una factura válida en el texto'
                    }
            
            # Procesar múltiples facturas
            invoices = []
            valid_invoices = []
            
            for i, (start, end) in enumerate(invoice_separators):
                invoice_text = text[start:end].strip()
                if invoice_text:
                    result = self.parse_invoice(invoice_text)
                    result['invoice_number'] = i + 1
                    result['text_range'] = {'start': start, 'end': end}
                    invoices.append(result)
                    
                    # Solo contar como válida si tiene campos extraídos
                    if result.get('success', False) and result.get('extracted_fields'):
                        valid_invoices.append(result)
            
            # Solo considerar exitoso si hay al menos una factura válida
            if valid_invoices:
                return {
                    'success': True,
                    'invoices': valid_invoices,
                    'total_invoices': len(valid_invoices),
                    'raw_text': text
                }
            else:
                return {
                    'success': False,
                    'invoices': [],
                    'total_invoices': 0,
                    'raw_text': text,
                    'error': 'No se detectaron facturas válidas en el texto'
                }
            
        except Exception as e:
            logger.error(f"Error parseando múltiples facturas: {e}")
            return {
                'success': False,
                'error': str(e),
                'raw_text': text,
                'invoices': []
            }
    
    def _detect_invoice_separators(self, text: str) -> List[tuple]:
        """Detecta los límites de cada factura en el texto"""
        separators = []
        
        # Patrones más específicos que indican el inicio de una nueva factura
        # Buscar patrones que aparecen al inicio de una factura completa
        invoice_start_patterns = [
            r'ORIGINAL\s+[A-Za-z\s]+S[AR]L?\s+Le\s+PAGTURA\s+Punto de Venta:',
            r'ORIGINAL\s+[A-Za-z\s]+S[AR]L?\s+Le\s+PAGTURA\s+Comp\.',
            r'ORIGINAL\s+[A-Za-z\s]+S[AR]L?\s+coo\.\d+\s+PAGTURA',
            r'FACTURA\s+[ABC]\s+Punto de Venta:',
            r'Comprobante\s+[ABC]\s+Punto de Venta:',
            # Patrones adicionales para diferentes formatos
            r'ORIGINAL\s+[ABC]?\s+[A-Za-z\s]+S[AR]L?',
            r'FACTURA\s+[ABC]\s+\d+',
            r'Comprobante\s+[ABC]\s+\d+'
        ]
        
        # Encontrar todas las posiciones de inicio
        start_positions = []
        for pattern in invoice_start_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                start_positions.append(match.start())
        
        # Ordenar posiciones y eliminar duplicados
        start_positions = sorted(set(start_positions))
        
        # Filtrar posiciones que están muy cerca (menos de 500 caracteres)
        # Esto evita duplicados de la misma factura
        filtered_positions = []
        for pos in start_positions:
            if not filtered_positions or pos - filtered_positions[-1] > 500:
                filtered_positions.append(pos)
        
        if not filtered_positions:
            # Si no se encuentran separadores claros, tratar como una sola factura
            return [(0, len(text))]
        
        # Crear rangos entre posiciones
        for i in range(len(filtered_positions)):
            start = filtered_positions[i]
            end = filtered_positions[i + 1] if i + 1 < len(filtered_positions) else len(text)
            separators.append((start, end))
        
        return separators
    
    def get_supported_fields(self) -> List[str]:
        """Retorna la lista de campos que puede extraer"""
        return list(self.patterns.keys()) + ['items', 'deuda_impositiva']
