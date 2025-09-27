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
    
    # Configuración de producción
    WORKERS = int(os.getenv("WORKERS", 1))  # Para Docker, usar 1 worker
    LOG_LEVEL = os.getenv("LOG_LEVEL", "info")
    
    # Configuración de archivos
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", "temp_uploads")
    MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 50 * 1024 * 1024))  # 50MB
    ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".pdf"}
    
    # Configuración de Tesseract
    TESSERACT_PATH = os.getenv("TESSERACT_PATH", r"C:\Program Files\Tesseract-OCR\tesseract.exe")  # Ruta a tesseract.exe en Windows
    
    # Configuración de Poppler para PDFs
    # Poppler path - intentar múltiples ubicaciones
    POPPLER_PATH = os.getenv("POPPLER_PATH", None)
    if not POPPLER_PATH:
        # Intentar ubicaciones comunes
        possible_paths = [
            os.path.join(os.path.dirname(__file__), "poppler", "poppler-23.08.0", "Library", "bin"),
            "/usr/bin",  # Linux
            "/usr/local/bin",  # Linux
            "/opt/homebrew/bin",  # macOS
            "/usr/local/Cellar/poppler/*/bin",  # macOS Homebrew
        ]
        
        for path in possible_paths:
            if os.path.exists(path) and os.path.exists(os.path.join(path, "pdftoppm")):
                POPPLER_PATH = path
                break
        
        # Si no se encuentra, usar None (pdf2image intentará usar PATH del sistema)
        if not POPPLER_PATH:
            POPPLER_PATH = None
    
    # Configuración de LayoutParser (optimizada para detección)
    LAYOUT_MODEL_CONFIG = {
        "model_name": "lp://PubLayNet/faster_rcnn_R_50_FPN_3x/config",
        "confidence_threshold": 0.3,  # Más bajo = detecta más elementos
        "nms_threshold": 0.5
    }
    
    # Configuración de scikit-image (optimizada para velocidad máxima)
    FAST_MODE = os.getenv("FAST_MODE", "True").lower() == "true"  # Modo rápido por defecto
    
    SKIMAGE_CONFIG = {
        "bilateral_sigma_color": 0.1,      # Más alto = más rápido
        "bilateral_sigma_spatial": 5,      # Más bajo = más rápido
        "gaussian_sigma": 0.05,            # Muy bajo para preservar texto y velocidad
        "morphology_disk_size": 1,         # Mantener pequeño
        "enable_bilateral": False,         # Deshabilitar (muy lento)
        "enable_adaptive_hist": False,     # Deshabilitar para velocidad
        "enable_morphology": False,        # Deshabilitar (puede eliminar texto)
        "use_simple_preprocessing": True   # Usar preprocesamiento simple
    }
    
    # Configuración de OCR (optimizada para máxima detección)
    OCR_CONFIG = {
        "lang": "spa+eng",  # Español + inglés como fallback
        "config": "--psm 3 --oem 3"  # PSM 3 = detección automática completa de página
    }

# Instancia global de configuración
settings = Settings()
