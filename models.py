from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from enum import Enum

class ProcessingStatus(str, Enum):
    """Estados del procesamiento"""
    SUCCESS = "success"
    ERROR = "error"
    PENDING = "pending"

class TextBlock(BaseModel):
    """Modelo para bloques de texto extraídos"""
    text: str = Field(..., description="Texto extraído")
    confidence: float = Field(..., description="Confianza del OCR (0-1)")
    bbox: List[int] = Field(..., description="Coordenadas del bounding box [x1, y1, x2, y2]")
    block_type: str = Field(..., description="Tipo de bloque (text, title, list, etc.)")

class Table(BaseModel):
    """Modelo para tablas extraídas"""
    rows: List[List[str]] = Field(..., description="Filas de la tabla")
    headers: Optional[List[str]] = Field(None, description="Encabezados de la tabla")
    bbox: List[int] = Field(..., description="Coordenadas del bounding box [x1, y1, x2, y2]")
    confidence: float = Field(..., description="Confianza de la detección")

class Figure(BaseModel):
    """Modelo para figuras/imágenes detectadas"""
    caption: Optional[str] = Field(None, description="Pie de figura si existe")
    bbox: List[int] = Field(..., description="Coordenadas del bounding box [x1, y1, x2, y2]")
    figure_type: str = Field(..., description="Tipo de figura (image, chart, diagram, etc.)")
    confidence: float = Field(..., description="Confianza de la detección")

class ProcessingResult(BaseModel):
    """Modelo para el resultado del procesamiento"""
    filename: str = Field(..., description="Nombre del archivo procesado")
    file_size: int = Field(..., description="Tamaño del archivo en bytes")
    content_type: str = Field(..., description="Tipo de contenido del archivo")
    processing_time: float = Field(..., description="Tiempo de procesamiento en segundos")
    status: ProcessingStatus = Field(..., description="Estado del procesamiento")
    
    # Campos extraídos
    text_blocks: List[TextBlock] = Field(default=[], description="Bloques de texto extraídos")
    tables: List[Table] = Field(default=[], description="Tablas extraídas")
    figures: List[Figure] = Field(default=[], description="Figuras detectadas")
    raw_text: str = Field(default="", description="Texto completo extraído")
    
    # Metadatos adicionales
    metadata: Dict[str, Any] = Field(default={}, description="Metadatos adicionales")
    error_message: Optional[str] = Field(None, description="Mensaje de error si ocurrió alguno")

class ErrorResponse(BaseModel):
    """Modelo para respuestas de error"""
    error: str = Field(..., description="Tipo de error")
    message: str = Field(..., description="Mensaje descriptivo del error")
    details: Optional[Dict[str, Any]] = Field(None, description="Detalles adicionales del error")
