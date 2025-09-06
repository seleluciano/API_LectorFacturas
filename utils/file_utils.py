"""
Utilidades para manejo de archivos
"""
import os
import uuid
from typing import Optional
from fastapi import UploadFile
import logging

logger = logging.getLogger(__name__)

def generate_unique_filename(original_filename: str) -> str:
    """
    Generar un nombre de archivo único
    
    Args:
        original_filename: Nombre original del archivo
        
    Returns:
        Nombre de archivo único
    """
    # Obtener extensión del archivo
    _, ext = os.path.splitext(original_filename)
    
    # Generar UUID único
    unique_id = str(uuid.uuid4())
    
    return f"{unique_id}{ext}"

def validate_file_type(file: UploadFile, allowed_extensions: set) -> bool:
    """
    Validar el tipo de archivo
    
    Args:
        file: Archivo a validar
        allowed_extensions: Extensiones permitidas
        
    Returns:
        True si el archivo es válido, False en caso contrario
    """
    if not file.filename:
        return False
    
    # Obtener extensión del archivo
    _, ext = os.path.splitext(file.filename.lower())
    
    return ext in allowed_extensions

def validate_file_size(file: UploadFile, max_size: int) -> bool:
    """
    Validar el tamaño del archivo
    
    Args:
        file: Archivo a validar
        max_size: Tamaño máximo en bytes
        
    Returns:
        True si el archivo es válido, False en caso contrario
    """
    # Leer el contenido para obtener el tamaño
    content = file.file.read()
    file.file.seek(0)  # Resetear posición del archivo
    
    return len(content) <= max_size

def save_upload_file(file: UploadFile, upload_dir: str) -> Optional[str]:
    """
    Guardar archivo subido en el directorio especificado
    
    Args:
        file: Archivo a guardar
        upload_dir: Directorio donde guardar el archivo
        
    Returns:
        Ruta del archivo guardado o None si hubo error
    """
    try:
        # Crear directorio si no existe
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generar nombre único
        unique_filename = generate_unique_filename(file.filename)
        file_path = os.path.join(upload_dir, unique_filename)
        
        # Guardar archivo
        with open(file_path, "wb") as buffer:
            content = file.file.read()
            buffer.write(content)
        
        logger.info(f"Archivo guardado: {file_path}")
        return file_path
        
    except Exception as e:
        logger.error(f"Error guardando archivo: {str(e)}")
        return None

def cleanup_file(file_path: str) -> bool:
    """
    Eliminar archivo del sistema
    
    Args:
        file_path: Ruta del archivo a eliminar
        
    Returns:
        True si se eliminó correctamente, False en caso contrario
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Archivo eliminado: {file_path}")
            return True
        return False
        
    except Exception as e:
        logger.error(f"Error eliminando archivo: {str(e)}")
        return False
