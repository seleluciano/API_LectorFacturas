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

class SingleInvoiceResult(BaseModel):
    """Modelo para una factura individual parseada"""
    success: bool = Field(..., description="Si el parsing fue exitoso")
    invoice_number: Optional[int] = Field(None, description="Número de factura (1, 2, 3...)")
    extracted_fields: Dict[str, Any] = Field(default={}, description="Campos extraídos de la factura")
    raw_text: str = Field(default="", description="Texto de esta factura específica")
    parsing_confidence: float = Field(default=0.0, description="Confianza del parsing")
    text_range: Optional[Dict[str, int]] = Field(None, description="Rango de texto en el documento original")
    error: Optional[str] = Field(None, description="Error si el parsing falló")

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

class InvoiceFields(BaseModel):
    """Modelo para campos específicos de facturas según modelo Django"""
    # Campos principales de Factura
    tipo_factura: Optional[str] = Field(None, description="Tipo de factura (A, B, C)")
    razon_social_vendedor: Optional[str] = Field(None, description="Razón social del vendedor")
    cuit_vendedor: Optional[str] = Field(None, description="CUIT del vendedor")
    razon_social_comprador: Optional[str] = Field(None, description="Razón social del comprador")
    cuit_comprador: Optional[str] = Field(None, description="CUIT del comprador")
    condicion_iva_comprador: Optional[str] = Field(None, description="Condición frente al IVA del comprador")
    condicion_venta: Optional[str] = Field(None, description="Condición de venta (Contado/Crédito)")
    fecha_emision: Optional[str] = Field(None, description="Fecha de emisión")
    subtotal: Optional[str] = Field(None, description="Subtotal")
    deuda_impositiva: Optional[str] = Field(None, description="Deuda impositiva (total - subtotal)")
    importe_total: Optional[str] = Field(None, description="Importe total")
    
    # Campos adicionales útiles
    numero_factura: Optional[str] = Field(None, description="Número de factura")
    punto_venta: Optional[str] = Field(None, description="Punto de venta")
    
    # Items de la factura
    items: Optional[List[Dict[str, str]]] = Field(None, description="Items de la factura")

class StructuredInvoiceResponse(BaseModel):
    """Modelo para respuesta estructurada de facturas"""
    filename: str = Field(..., description="Nombre del archivo procesado")
    file_size: int = Field(..., description="Tamaño del archivo en bytes")
    content_type: str = Field(..., description="Tipo de contenido del archivo")
    processing_time: float = Field(..., description="Tiempo de procesamiento en segundos")
    status: ProcessingStatus = Field(..., description="Estado del procesamiento")
    
    # Campos estructurados de la factura
    invoice_fields: InvoiceFields = Field(..., description="Campos específicos de la factura")
    
    # Datos originales
    raw_text: str = Field(..., description="Texto completo extraído")
    text_blocks: List[TextBlock] = Field(default=[], description="Bloques de texto extraídos")
    
    # Metadatos
    metadata: Dict[str, Any] = Field(default={}, description="Metadatos adicionales")
    error_message: Optional[str] = Field(None, description="Mensaje de error si ocurrió alguno")

class ErrorResponse(BaseModel):
    """Modelo para respuestas de error"""
    error: str = Field(..., description="Tipo de error")
    message: str = Field(..., description="Mensaje descriptivo del error")
    details: Optional[Dict[str, Any]] = Field(None, description="Detalles adicionales del error")
