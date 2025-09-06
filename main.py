from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
from typing import Dict, Any
import logging

from config import settings
from models import ProcessingResult, ErrorResponse
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
            "process_image": "/process-image"
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

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
