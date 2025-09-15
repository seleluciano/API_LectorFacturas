"""
Procesador avanzado de imágenes usando scikit-image
Alternativa más moderna a OpenCV con algoritmos mejorados
"""
import numpy as np
import pytesseract
import layoutparser as lp
from layoutparser.models import Detectron2LayoutModel
from PIL import Image
import time
import logging
from typing import List, Dict, Any, Tuple
import os
from pdf2image import convert_from_path

# Importaciones de scikit-image
from skimage import filters, morphology, exposure, restoration
from skimage.filters import threshold_otsu, gaussian
from skimage.morphology import disk, opening, closing
from skimage.restoration import denoise_bilateral

from models import TextBlock, Table, Figure, ProcessingResult, ProcessingStatus
from config import settings
from services.invoice_parser import InvoiceParser

logger = logging.getLogger(__name__)

class AdvancedImageProcessor:
    """Procesador avanzado de imágenes usando scikit-image"""
    
    def __init__(self):
        """Inicializar el procesador avanzado"""
        self.layout_model = None
        self.invoice_parser = InvoiceParser()
        self._setup_tesseract()
        self._load_layout_model()
    
    def _setup_tesseract(self):
        """Configurar Tesseract OCR"""
        try:
            if settings.TESSERACT_PATH:
                pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_PATH
                
                # Configurar TESSDATA_PREFIX para encontrar los archivos de idioma
                tesseract_dir = os.path.dirname(settings.TESSERACT_PATH)
                tessdata_dir = os.path.join(tesseract_dir, "tessdata")
                
                if os.path.exists(tessdata_dir):
                    os.environ['TESSDATA_PREFIX'] = tessdata_dir
                    logger.info(f"TESSDATA_PREFIX configurado: {tessdata_dir}")
                else:
                    logger.warning(f"Directorio tessdata no encontrado: {tessdata_dir}")
            
            pytesseract.get_tesseract_version()
            logger.info("Tesseract OCR configurado correctamente")
            
        except Exception as e:
            logger.error(f"Error configurando Tesseract: {str(e)}")
            raise
    
    def _load_layout_model(self):
        """Cargar el modelo de LayoutParser"""
        try:
            self.layout_model = Detectron2LayoutModel(
                config_path=settings.LAYOUT_MODEL_CONFIG["model_name"],
                threshold=settings.LAYOUT_MODEL_CONFIG["confidence_threshold"],
                label_map={0: "Text", 1: "Title", 2: "List", 3: "Table", 4: "Figure"}
            )
            logger.info("Modelo de LayoutParser cargado correctamente")
            
        except Exception as e:
            logger.error(f"Error cargando modelo de LayoutParser: {str(e)}")
            self.layout_model = None
    
    def convert_pdf_to_image(self, pdf_path: str) -> str:
        """Convertir PDF a imagen"""
        try:
            images = convert_from_path(pdf_path, first_page=1, last_page=1, dpi=300)
            
            if not images:
                raise ValueError("No se pudo convertir el PDF a imagen")
            
            image_path = pdf_path.replace('.pdf', '_converted.jpg')
            images[0].save(image_path, 'JPEG', quality=95)
            
            logger.info(f"PDF convertido a imagen: {image_path}")
            return image_path
            
        except Exception as e:
            logger.error(f"Error convirtiendo PDF: {str(e)}")
            raise

    def preprocess_image_advanced(self, image_path: str) -> np.ndarray:
        """
        Preprocesamiento avanzado usando scikit-image
        
        Args:
            image_path: Ruta a la imagen
            
        Returns:
            Imagen preprocesada como array de numpy
        """
        try:
            # Verificar si es un PDF y convertirlo
            if image_path.lower().endswith('.pdf'):
                image_path = self.convert_pdf_to_image(image_path)
            
            # Cargar imagen
            image = Image.open(image_path)
            if image.mode != 'L':
                image = image.convert('L')
            
            # Mantener tamaño original de la imagen para preservar calidad
            logger.info(f"Procesando imagen con tamaño original: {image.size}")
            
            # Convertir a array de numpy
            image_array = np.array(image, dtype=np.float64)
            
            # Preprocesamiento simple para preservar texto
            if settings.SKIMAGE_CONFIG.get("use_simple_preprocessing", False):
                # Preprocesamiento mínimo - solo normalización
                image_array = exposure.rescale_intensity(image_array)
                processed_image = (image_array * 255).astype(np.uint8)
                logger.info("Usando preprocesamiento simple para preservar texto")
            else:
                # Preprocesamiento completo
                # Normalizar imagen (rápido)
                image_array = exposure.rescale_intensity(image_array)
                
                # Aplicar filtro bilateral solo si está habilitado
                if settings.SKIMAGE_CONFIG.get("enable_bilateral", True):
                    image_array = denoise_bilateral(
                        image_array, 
                        sigma_color=settings.SKIMAGE_CONFIG["bilateral_sigma_color"], 
                        sigma_spatial=settings.SKIMAGE_CONFIG["bilateral_sigma_spatial"]
                    )
                
                # Mejorar contraste solo si está habilitado
                if settings.SKIMAGE_CONFIG.get("enable_adaptive_hist", True):
                    image_array = exposure.equalize_adapthist(image_array, clip_limit=0.03)
                
                # Aplicar filtro gaussiano suave (siempre, es rápido)
                image_array = gaussian(image_array, sigma=settings.SKIMAGE_CONFIG["gaussian_sigma"])
                
                # Aplicar umbralización de Otsu (rápido)
                threshold = threshold_otsu(image_array)
                binary = image_array > threshold
                
                # Operaciones morfológicas solo si están habilitadas
                if settings.SKIMAGE_CONFIG.get("enable_morphology", True):
                    selem = disk(settings.SKIMAGE_CONFIG["morphology_disk_size"])
                    binary = opening(binary, selem)
                    binary = closing(binary, selem)
                
                # Convertir de vuelta a uint8
                processed_image = (binary * 255).astype(np.uint8)
            
            return processed_image
            
        except Exception as e:
            logger.error(f"Error en preprocesamiento avanzado: {str(e)}")
            # Fallback a PIL
            try:
                image = Image.open(image_path).convert('L')
                return np.array(image)
            except:
                raise ValueError(f"No se pudo procesar la imagen: {image_path}")
    
    def detect_layout(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """Detectar layout usando LayoutParser"""
        layout_elements = []
        
        try:
            if self.layout_model is None:
                logger.warning("Modelo de LayoutParser no disponible")
                return layout_elements
            
            pil_image = Image.fromarray(image)
            layout = self.layout_model.detect(pil_image)
            
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
        """Extraer texto de una región específica con múltiples intentos"""
        try:
            x1, y1, x2, y2 = bbox
            
            # Extraer región de interés
            roi = image[y1:y2, x1:x2]
            
            if roi.size == 0:
                return "", 0.0
            
            # Intentar diferentes configuraciones de OCR
            ocr_configs = [
                settings.OCR_CONFIG["config"],  # Configuración principal
                "--psm 6 --oem 3",              # PSM 6 (bloque uniforme)
                "--psm 8 --oem 3",              # PSM 8 (palabra única)
                "--psm 13 --oem 3",             # PSM 13 (línea de texto cruda)
                "--psm 3 --oem 3"               # PSM 3 (detección automática)
            ]
            
            best_text = ""
            best_confidence = 0.0
            
            for config in ocr_configs:
                try:
                    # Aplicar OCR con configuración específica
                    data = pytesseract.image_to_data(
                        roi, 
                        lang=settings.OCR_CONFIG["lang"],
                        config=config,
                        output_type=pytesseract.Output.DICT
                    )
                    
                    # Extraer texto y calcular confianza
                    text_parts = []
                    confidences = []
                    
                    for i in range(len(data['text'])):
                        if int(data['conf'][i]) > 0:
                            text_parts.append(data['text'][i])
                            confidences.append(int(data['conf'][i]) / 100.0)
                    
                    text = ' '.join(text_parts).strip()
                    avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
                    
                    # Mantener el mejor resultado
                    if len(text) > len(best_text) or (len(text) == len(best_text) and avg_confidence > best_confidence):
                        best_text = text
                        best_confidence = avg_confidence
                        
                except Exception as e:
                    logger.warning(f"Error con configuración OCR {config}: {str(e)}")
                    continue
            
            return best_text, best_confidence
            
        except Exception as e:
            logger.error(f"Error extrayendo texto de región: {str(e)}")
            return "", 0.0
    
    def process_image(self, image_path: str) -> ProcessingResult:
        """Procesar imagen completa con scikit-image"""
        start_time = time.time()
        converted_image_path = None
        
        try:
            filename = os.path.basename(image_path)
            file_size = os.path.getsize(image_path)
            
            # Preprocesamiento avanzado
            processed_image = self.preprocess_image_advanced(image_path)
            
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
            
            # Extraer tablas (implementación simplificada)
            tables = []
            table_elements = [elem for elem in layout_elements if elem["type"] == "Table"]
            for table_elem in table_elements:
                text, confidence = self.extract_text_from_region(processed_image, table_elem["bbox"])
                if text.strip():
                    rows = [row.strip().split() for row in text.split('\n') if row.strip()]
                    if rows:
                        tables.append(Table(
                            rows=rows,
                            bbox=table_elem["bbox"],
                            confidence=confidence
                        ))
            
            # Extraer figuras
            figures = []
            figure_elements = [elem for elem in layout_elements if elem["type"] == "Figure"]
            for fig_elem in figure_elements:
                figures.append(Figure(
                    bbox=fig_elem["bbox"],
                    figure_type="image",
                    confidence=fig_elem["confidence"]
                ))
            
            # Extraer texto completo (fallback si no hay elementos detectados)
            full_text, full_confidence = self.extract_text_from_region(processed_image, [0, 0, processed_image.shape[1], processed_image.shape[0]])
            
            # Si no se detectaron elementos de layout, crear un bloque de texto con todo el contenido
            if not layout_elements and full_text.strip():
                logger.info("No se detectaron elementos de layout, creando bloque de texto completo")
                text_blocks.append(TextBlock(
                    text=full_text.strip(),
                    confidence=full_confidence,
                    bbox=[0, 0, processed_image.shape[1], processed_image.shape[0]],
                    block_type="text"
                ))
            
            # Parsear campos específicos de la factura
            invoice_data = self.invoice_parser.parse_invoice(full_text)
            
            processing_time = time.time() - start_time
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
                    "is_pdf": image_path.lower().endswith('.pdf'),
                    "processor": "scikit-image",
                    "invoice_parsing": invoice_data
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
            if converted_image_path and os.path.exists(converted_image_path):
                try:
                    os.remove(converted_image_path)
                    logger.info(f"Imagen convertida eliminada: {converted_image_path}")
                except Exception as e:
                    logger.warning(f"No se pudo eliminar imagen convertida: {str(e)}")
