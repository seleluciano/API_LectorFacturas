# Instalación y Configuración de la API

## Requisitos del Sistema

### Windows
- Python 3.8 o superior
- Tesseract OCR instalado en `C:\Program Files\Tesseract-OCR\`
- Poppler incluido en el proyecto (directorio `poppler/`)

### Linux/macOS
- Python 3.8 o superior
- Tesseract OCR instalado
- Poppler instalado (ver `requirements_poppler.txt`)

## Instalación

1. **Clonar el repositorio**:
```bash
git clone <repository-url>
cd Api
```

2. **Crear entorno virtual** (recomendado):
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate
```

3. **Instalar dependencias**:
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno** (opcional):
```bash
# Crear archivo .env
HOST=0.0.0.0
PORT=8000
DEBUG=True
LOG_LEVEL=info
```

## Configuración de Tesseract

### Windows
- Descargar e instalar desde: https://github.com/UB-Mannheim/tesseract/wiki
- Instalar en la ruta por defecto: `C:\Program Files\Tesseract-OCR\`
- Descargar paquete de idioma español si es necesario

### Linux
```bash
sudo apt-get install tesseract-ocr tesseract-ocr-spa
```

### macOS
```bash
brew install tesseract tesseract-lang
```

## Configuración de Poppler

### Windows
- Los binarios ya están incluidos en `poppler/poppler-23.08.0/`
- No se requiere instalación adicional

### Linux
```bash
sudo apt-get install poppler-utils
```

### macOS
```bash
brew install poppler
```

## Ejecutar la API

1. **Iniciar el servidor**:
```bash
python start_server.py
```

2. **Verificar que funciona**:
```bash
curl http://localhost:8000/
```

3. **Documentación de la API**:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Endpoints Principales

- `POST /process-multiple-images` - Procesar múltiples archivos (PDFs/imágenes)
- `POST /process-image` - Procesar un solo archivo
- `POST /process-invoice` - Procesar solo facturas
- `GET /health` - Estado de la API

## Solución de Problemas

### Error: "No module named 'fastapi'"
```bash
pip install -r requirements.txt
```

### Error: "Tesseract not found"
- Verificar que Tesseract esté instalado
- Verificar la ruta en `config.py`

### Error: "Poppler not found"
- En Windows: verificar que existe `poppler/poppler-23.08.0/Library/bin/`
- En Linux/macOS: instalar poppler-utils

### Error: "No se encontraron facturas"
- Verificar que el PDF contenga texto (no solo imágenes)
- Verificar que el PDF no esté corrupto
- Revisar logs para más detalles

## Estructura del Proyecto

```
Api/
├── main.py                 # Aplicación FastAPI principal
├── start_server.py         # Script para iniciar el servidor
├── config.py              # Configuración de la aplicación
├── requirements.txt       # Dependencias de Python
├── poppler/              # Binarios de Poppler para Windows
├── services/             # Módulos de procesamiento
│   ├── advanced_image_processor.py
│   └── invoice_parser.py
├── utils/                # Utilidades
└── temp_uploads/         # Directorio temporal para archivos
```
