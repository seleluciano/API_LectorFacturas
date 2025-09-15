from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
from typing import Dict, Any
import logging

from config import settings
from models import ProcessingResult, ErrorResponse, StructuredInvoiceResponse, InvoiceFields
from services.advanced_image_processor import AdvancedImageProcessor
from utils.file_utils import validate_file_type, validate_file_size, save_upload_file, cleanup_file

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear la aplicación FastAPI
app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especifica los dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Crear directorio para archivos temporales si no existe
if not os.path.exists(settings.UPLOAD_DIR):
    os.makedirs(settings.UPLOAD_DIR)

# Inicializar procesador avanzado de imágenes con scikit-image
image_processor = AdvancedImageProcessor()

@app.get("/")
async def root():
    """Endpoint de bienvenida"""
    return {
        "message": "API de Procesamiento de Imágenes con OCR",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "process_image": "/process-image",
            "process_invoice": "/process-invoice"
        }
    }

@app.get("/health")
async def health_check():
    """Endpoint para verificar el estado de la API"""
    return {"status": "healthy", "message": "API funcionando correctamente"}

@app.post("/process-image", response_model=ProcessingResult)
async def process_image(file: UploadFile = File(...)):
    """
    Endpoint para procesar imágenes con LayoutParser y Tesseract OCR
    
    Args:
        file: Archivo de imagen a procesar
        
    Returns:
        JSON con los campos extraídos de la imagen
    """
    file_path = None
    try:
        # Validar tipo de archivo
        if not validate_file_type(file, settings.ALLOWED_EXTENSIONS):
            raise HTTPException(
                status_code=400, 
                detail=f"Tipo de archivo no permitido. Extensiones permitidas: {', '.join(settings.ALLOWED_EXTENSIONS)}"
            )
        
        # Validar tamaño de archivo
        if not validate_file_size(file, settings.MAX_FILE_SIZE):
            raise HTTPException(
                status_code=400,
                detail=f"Archivo demasiado grande. Tamaño máximo: {settings.MAX_FILE_SIZE / (1024*1024):.1f}MB"
            )
        
        # Guardar archivo temporalmente
        file_path = save_upload_file(file, settings.UPLOAD_DIR)
        if not file_path:
            raise HTTPException(
                status_code=500,
                detail="Error guardando archivo temporal"
            )
        
        logger.info(f"Procesando archivo: {file_path}")
        
        # Procesar imagen con LayoutParser y Tesseract
        result = image_processor.process_image(file_path)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error procesando imagen: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )
    finally:
        # Limpiar archivo temporal
        if file_path and os.path.exists(file_path):
            cleanup_file(file_path)

@app.post("/process-invoice", response_model=StructuredInvoiceResponse)
async def process_invoice(file: UploadFile = File(...)):
    """
    Endpoint para procesar facturas y extraer campos específicos
    
    Args:
        file: Archivo de imagen/PDF de factura a procesar
        
    Returns:
        JSON con campos estructurados de la factura
    """
    file_path = None
    try:
        # Validar tipo de archivo
        if not validate_file_type(file, settings.ALLOWED_EXTENSIONS):
            raise HTTPException(
                status_code=400, 
                detail=f"Tipo de archivo no permitido. Extensiones permitidas: {', '.join(settings.ALLOWED_EXTENSIONS)}"
            )
        
        # Validar tamaño de archivo
        if not validate_file_size(file, settings.MAX_FILE_SIZE):
            raise HTTPException(
                status_code=400,
                detail=f"Archivo demasiado grande. Tamaño máximo: {settings.MAX_FILE_SIZE / (1024*1024):.1f}MB"
            )
        
        # Guardar archivo temporalmente
        file_path = save_upload_file(file, settings.UPLOAD_DIR)
        if not file_path:
            raise HTTPException(
                status_code=500,
                detail="Error guardando archivo temporal"
            )
        
        logger.info(f"Procesando factura: {file_path}")
        
        # Procesar imagen con LayoutParser y Tesseract
        result = image_processor.process_image(file_path)
        
        # Extraer datos de la factura
        invoice_data = result.metadata.get("invoice_parsing", {})
        
        if invoice_data.get("success", False):
            extracted_fields = invoice_data.get("extracted_fields", {})
            
            # Crear objeto InvoiceFields
            invoice_fields = InvoiceFields(
                # Campos principales según modelo Django
                tipo_factura=extracted_fields.get("tipo_factura"),
                razon_social_vendedor=extracted_fields.get("razon_social_vendedor"),
                cuit_vendedor=extracted_fields.get("cuit_vendedor"),
                razon_social_comprador=extracted_fields.get("razon_social_comprador"),
                cuit_comprador=extracted_fields.get("cuit_comprador"),
                condicion_iva_comprador=extracted_fields.get("condicion_iva_comprador"),
                condicion_venta=extracted_fields.get("condicion_venta"),
                fecha_emision=extracted_fields.get("fecha_emision"),
                subtotal=extracted_fields.get("subtotal"),
                deuda_impositiva=extracted_fields.get("deuda_impositiva"),
                importe_total=extracted_fields.get("importe_total"),
                
                # Campos adicionales útiles
                numero_factura=extracted_fields.get("numero_factura"),
                punto_venta=extracted_fields.get("punto_venta"),
                
                # Items de la factura
                items=extracted_fields.get("items")
            )
        else:
            # Si falla el parsing, crear campos vacíos
            invoice_fields = InvoiceFields()
        
        # Crear respuesta estructurada
        structured_response = StructuredInvoiceResponse(
            filename=result.filename,
            file_size=result.file_size,
            content_type=result.content_type,
            processing_time=result.processing_time,
            status=result.status,
            invoice_fields=invoice_fields,
            raw_text=result.raw_text,
            text_blocks=result.text_blocks,
            metadata=result.metadata,
            error_message=result.error_message
        )
        
        return structured_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error procesando factura: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )
    finally:
        # Limpiar archivo temporal
        if file_path and os.path.exists(file_path):
            cleanup_file(file_path)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
