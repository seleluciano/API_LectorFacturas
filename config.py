import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class Settings:
    """Configuración de la aplicación"""
    
    # Configuración de la API
    API_TITLE = "API de Procesamiento de Imágenes con OCR"
    API_VERSION = "1.0.0"
    API_DESCRIPTION = "API para procesar imágenes usando LayoutParser y Tesseract OCR"
    
    # Configuración del servidor
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8000))
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
    
    # Configuración de archivos
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", "temp_uploads")
    MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 10 * 1024 * 1024))  # 10MB
    ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".pdf"}
    
    # Configuración de Tesseract
    TESSERACT_PATH = os.getenv("TESSERACT_PATH", r"C:\Program Files\Tesseract-OCR\tesseract.exe")  # Ruta a tesseract.exe en Windows
    
    # Configuración de LayoutParser
    LAYOUT_MODEL_CONFIG = {
        "model_name": "lp://PubLayNet/faster_rcnn_R_50_FPN_3x/config",
        "confidence_threshold": 0.5,
        "nms_threshold": 0.5
    }
    
    # Configuración de scikit-image
    SKIMAGE_CONFIG = {
        "bilateral_sigma_color": 0.05,
        "bilateral_sigma_spatial": 15,
        "gaussian_sigma": 0.5,
        "morphology_disk_size": 1
    }
    
    # Configuración de OCR
    OCR_CONFIG = {
        "lang": "spa",  # Solo español
        "config": "--psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.,;:!?()[]{}'\"-+*/=<>@#$%&"
    }

# Instancia global de configuración
settings = Settings()
