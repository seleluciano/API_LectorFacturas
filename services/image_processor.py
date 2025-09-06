"""
Servicio para procesamiento de imágenes con LayoutParser y Tesseract OCR
"""
import numpy as np
import pytesseract
import layoutparser as lp
from PIL import Image, ImageEnhance, ImageFilter
import time
import logging
from typing import List, Dict, Any, Tuple
import os
from pdf2image import convert_from_path

from models import TextBlock, Table, Figure, ProcessingResult, ProcessingStatus
from config import settings

logger = logging.getLogger(__name__)

class ImageProcessor:
    """Clase para procesar imágenes con LayoutParser y Tesseract OCR"""
    
    def __init__(self):
        """Inicializar el procesador de imágenes"""
        self.layout_model = None
        self._setup_tesseract()
        self._load_layout_model()
    
    def _setup_tesseract(self):
        """Configurar Tesseract OCR"""
        try:
            if settings.TESSERACT_PATH:
                pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_PATH
            
            # Verificar que Tesseract esté disponible
            pytesseract.get_tesseract_version()
            logger.info("Tesseract OCR configurado correctamente")
            
        except Exception as e:
            logger.error(f"Error configurando Tesseract: {str(e)}")
            raise
    
    def _load_layout_model(self):
        """Cargar el modelo de LayoutParser"""
        try:
            # Cargar modelo de detección de layout
            self.layout_model = lp.Detectron2LayoutModel(
                config_path=settings.LAYOUT_MODEL_CONFIG["model_name"],
                threshold=settings.LAYOUT_MODEL_CONFIG["confidence_threshold"],
                label_map={0: "Text", 1: "Title", 2: "List", 3: "Table", 4: "Figure"}
            )
            logger.info("Modelo de LayoutParser cargado correctamente")
            
        except Exception as e:
            logger.error(f"Error cargando modelo de LayoutParser: {str(e)}")
            # En caso de error, continuar sin el modelo de layout
            self.layout_model = None
    
    def convert_pdf_to_image(self, pdf_path: str) -> str:
        """
        Convertir PDF a imagen para procesamiento
        
        Args:
            pdf_path: Ruta al archivo PDF
            
        Returns:
            Ruta a la imagen generada
        """
        try:
            # Convertir PDF a imagen (primera página)
            images = convert_from_path(pdf_path, first_page=1, last_page=1, dpi=300)
            
            if not images:
                raise ValueError("No se pudo convertir el PDF a imagen")
            
            # Guardar imagen temporal
            image_path = pdf_path.replace('.pdf', '_converted.jpg')
            images[0].save(image_path, 'JPEG', quality=95)
            
            logger.info(f"PDF convertido a imagen: {image_path}")
            return image_path
            
        except Exception as e:
            logger.error(f"Error convirtiendo PDF: {str(e)}")
            raise

    def preprocess_image(self, image_path: str) -> np.ndarray:
        """
        Preprocesar la imagen para mejorar la calidad del OCR usando PIL
        
        Args:
            image_path: Ruta a la imagen
            
        Returns:
            Imagen preprocesada como array de numpy
        """
        try:
            # Verificar si es un PDF y convertirlo
            if image_path.lower().endswith('.pdf'):
                image_path = self.convert_pdf_to_image(image_path)
            
            # Cargar imagen con PIL
            image = Image.open(image_path)
            if image is None:
                raise ValueError(f"No se pudo cargar la imagen: {image_path}")
            
            # Convertir a escala de grises
            if image.mode != 'L':
                image = image.convert('L')
            
            # Mejorar contraste
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.5)
            
            # Mejorar nitidez
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(2.0)
            
            # Aplicar filtro para reducir ruido
            image = image.filter(ImageFilter.MedianFilter(size=3))
            
            # Convertir a array de numpy para compatibilidad con LayoutParser
            image_array = np.array(image)
            
            return image_array
            
        except Exception as e:
            logger.error(f"Error en preprocesamiento: {str(e)}")
            # Si falla el preprocesamiento, devolver la imagen original
            try:
                image = Image.open(image_path).convert('L')
                return np.array(image)
            except:
                raise ValueError(f"No se pudo procesar la imagen: {image_path}")
    
    def detect_layout(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """
        Detectar layout de la imagen usando LayoutParser
        
        Args:
            image: Imagen como array de numpy
            
        Returns:
            Lista de elementos de layout detectados
        """
        layout_elements = []
        
        try:
            if self.layout_model is None:
                logger.warning("Modelo de LayoutParser no disponible, saltando detección de layout")
                return layout_elements
            
            # Convertir imagen para LayoutParser
            pil_image = Image.fromarray(image)
            
            # Detectar layout
            layout = self.layout_model.detect(pil_image)
            
            # Procesar elementos detectados
            for element in layout:
                bbox = element.coordinates
                layout_elements.append({
                    "type": element.type,
                    "bbox": [bbox.x_1, bbox.y_1, bbox.x_2, bbox.y_2],
                    "confidence": element.score
                })
            
            logger.info(f"Detectados {len(layout_elements)} elementos de layout")
            
        except Exception as e:
            logger.error(f"Error en detección de layout: {str(e)}")
        
        return layout_elements
    
    def extract_text_from_region(self, image: np.ndarray, bbox: List[int]) -> Tuple[str, float]:
        """
        Extraer texto de una región específica de la imagen
        
        Args:
            image: Imagen como array de numpy
            bbox: Coordenadas del bounding box [x1, y1, x2, y2]
            
        Returns:
            Tupla con (texto_extraído, confianza)
        """
        try:
            x1, y1, x2, y2 = bbox
            
            # Extraer región de interés
            roi = image[y1:y2, x1:x2]
            
            if roi.size == 0:
                return "", 0.0
            
            # Aplicar OCR a la región
            data = pytesseract.image_to_data(
                roi, 
                lang=settings.OCR_CONFIG["lang"],
                config=settings.OCR_CONFIG["config"],
                output_type=pytesseract.Output.DICT
            )
            
            # Extraer texto y calcular confianza promedio
            text_parts = []
            confidences = []
            
            for i in range(len(data['text'])):
                if int(data['conf'][i]) > 0:  # Filtrar elementos con confianza > 0
                    text_parts.append(data['text'][i])
                    confidences.append(int(data['conf'][i]) / 100.0)
            
            text = ' '.join(text_parts).strip()
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            
            return text, avg_confidence
            
        except Exception as e:
            logger.error(f"Error extrayendo texto de región: {str(e)}")
            return "", 0.0
    
    def extract_tables(self, image: np.ndarray, layout_elements: List[Dict[str, Any]]) -> List[Table]:
        """
        Extraer tablas de la imagen usando PIL
        
        Args:
            image: Imagen como array de numpy
            layout_elements: Elementos de layout detectados
            
        Returns:
            Lista de tablas extraídas
        """
        tables = []
        
        try:
            # Buscar elementos de tipo tabla
            table_elements = [elem for elem in layout_elements if elem["type"] == "Table"]
            
            for table_elem in table_elements:
                bbox = table_elem["bbox"]
                x1, y1, x2, y2 = bbox
                
                # Verificar que las coordenadas sean válidas
                if x2 <= x1 or y2 <= y1:
                    continue
                
                # Extraer texto de la región de la tabla
                text, confidence = self.extract_text_from_region(image, bbox)
                
                if text.strip():
                    # Dividir texto en filas (implementación básica)
                    # En una implementación más avanzada, se detectarían las celdas individuales
                    rows = []
                    for row in text.split('\n'):
                        if row.strip():
                            # Dividir por espacios o tabs
                            cells = [cell.strip() for cell in row.split() if cell.strip()]
                            if cells:
                                rows.append(cells)
                    
                    if rows:
                        tables.append(Table(
                            rows=rows,
                            bbox=bbox,
                            confidence=confidence
                        ))
            
            logger.info(f"Extraídas {len(tables)} tablas")
            
        except Exception as e:
            logger.error(f"Error extrayendo tablas: {str(e)}")
        
        return tables
    
    def extract_figures(self, layout_elements: List[Dict[str, Any]]) -> List[Figure]:
        """
        Extraer figuras de la imagen
        
        Args:
            layout_elements: Elementos de layout detectados
            
        Returns:
            Lista de figuras detectadas
        """
        figures = []
        
        try:
            # Buscar elementos de tipo figura
            figure_elements = [elem for elem in layout_elements if elem["type"] == "Figure"]
            
            for fig_elem in figure_elements:
                figures.append(Figure(
                    bbox=fig_elem["bbox"],
                    figure_type="image",
                    confidence=fig_elem["confidence"]
                ))
            
            logger.info(f"Detectadas {len(figures)} figuras")
            
        except Exception as e:
            logger.error(f"Error extrayendo figuras: {str(e)}")
        
        return figures
    
    def process_image(self, image_path: str) -> ProcessingResult:
        """
        Procesar una imagen completa
        
        Args:
            image_path: Ruta a la imagen a procesar
            
        Returns:
            Resultado del procesamiento
        """
        start_time = time.time()
        converted_image_path = None
        
        try:
            # Obtener información del archivo
            filename = os.path.basename(image_path)
            file_size = os.path.getsize(image_path)
            
            # Preprocesar imagen (incluye conversión de PDF si es necesario)
            processed_image = self.preprocess_image(image_path)
            
            # Si se convirtió un PDF, guardar la ruta para limpieza posterior
            if image_path.lower().endswith('.pdf'):
                converted_image_path = image_path.replace('.pdf', '_converted.jpg')
            
            # Detectar layout
            layout_elements = self.detect_layout(processed_image)
            
            # Extraer bloques de texto
            text_blocks = []
            for elem in layout_elements:
                if elem["type"] in ["Text", "Title", "List"]:
                    text, confidence = self.extract_text_from_region(processed_image, elem["bbox"])
                    if text.strip():
                        text_blocks.append(TextBlock(
                            text=text,
                            confidence=confidence,
                            bbox=elem["bbox"],
                            block_type=elem["type"].lower()
                        ))
            
            # Extraer tablas
            tables = self.extract_tables(processed_image, layout_elements)
            
            # Extraer figuras
            figures = self.extract_figures(layout_elements)
            
            # Extraer texto completo
            full_text, _ = self.extract_text_from_region(processed_image, [0, 0, processed_image.shape[1], processed_image.shape[0]])
            
            processing_time = time.time() - start_time
            
            # Determinar tipo de contenido
            content_type = "application/pdf" if image_path.lower().endswith('.pdf') else "image/jpeg"
            
            return ProcessingResult(
                filename=filename,
                file_size=file_size,
                content_type=content_type,
                processing_time=processing_time,
                status=ProcessingStatus.SUCCESS,
                text_blocks=text_blocks,
                tables=tables,
                figures=figures,
                raw_text=full_text,
                metadata={
                    "layout_elements_count": len(layout_elements),
                    "text_blocks_count": len(text_blocks),
                    "tables_count": len(tables),
                    "figures_count": len(figures),
                    "is_pdf": image_path.lower().endswith('.pdf')
                }
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Error procesando imagen: {str(e)}")
            
            return ProcessingResult(
                filename=os.path.basename(image_path),
                file_size=os.path.getsize(image_path) if os.path.exists(image_path) else 0,
                content_type="application/pdf" if image_path.lower().endswith('.pdf') else "image/jpeg",
                processing_time=processing_time,
                status=ProcessingStatus.ERROR,
                error_message=str(e)
            )
        finally:
            # Limpiar imagen convertida de PDF si existe
            if converted_image_path and os.path.exists(converted_image_path):
                try:
                    os.remove(converted_image_path)
                    logger.info(f"Imagen convertida eliminada: {converted_image_path}")
                except Exception as e:
                    logger.warning(f"No se pudo eliminar imagen convertida: {str(e)}")
