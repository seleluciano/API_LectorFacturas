# API de Procesamiento de Imágenes con OCR

API desarrollada con FastAPI para procesar imágenes usando LayoutParser y Tesseract OCR.

## Características

- **Procesamiento de imágenes y PDFs**: Detección de layout y extracción de texto
- **LayoutParser**: Detección automática de elementos (texto, tablas, figuras)
- **Tesseract OCR**: Extracción de texto en español
- **Soporte para PDFs**: Conversión automática de PDF a imagen para procesamiento
- **API REST**: Endpoints para subir y procesar archivos
- **Respuesta estructurada**: JSON con campos extraídos organizados
- **Procesador avanzado**: scikit-image con algoritmos modernos de preprocesamiento

## Estructura del Proyecto

```
├── main.py                 # Aplicación principal FastAPI
├── config.py              # Configuración de la aplicación
├── models.py              # Modelos Pydantic para validación
├── requirements.txt       # Dependencias del proyecto
├── services/
│   ├── __init__.py
│   ├── image_processor.py # Servicio de procesamiento con PIL (alternativo)
│   └── advanced_image_processor.py # Servicio principal con scikit-image
├── utils/
│   ├── __init__.py
│   └── file_utils.py      # Utilidades para manejo de archivos
├── temp_uploads/          # Directorio temporal para archivos
└── README.md
```

## Instalación

1. **Clonar el repositorio**:
   ```bash
   git clone <url-del-repositorio>
   cd api-ocr
   ```

2. **Crear entorno virtual**:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # source venv/bin/activate  # Linux/Mac
   ```

3. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Instalar Tesseract OCR**:
   - **Windows**: Descargar desde [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)
   - **Linux**: `sudo apt-get install tesseract-ocr`
   - **Mac**: `brew install tesseract`

5. **Configurar variables de entorno** (opcional):
   ```bash
   cp env_example.txt .env
   # Editar .env con tus configuraciones
   ```

## Uso

### Iniciar el servidor

```bash
python main.py
```

La API estará disponible en `http://localhost:8000`

### Documentación interactiva

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Endpoints

#### 1. Verificar estado de la API
```http
GET /health
```

#### 2. Procesar imagen o PDF
```http
POST /process-image
Content-Type: multipart/form-data

file: [archivo de imagen (.jpg, .jpeg, .png) o PDF]
```

**Respuesta**:
```json
{
  "filename": "imagen.jpg",
  "file_size": 123456,
  "content_type": "image/jpeg",
  "processing_time": 2.5,
  "status": "success",
  "text_blocks": [
    {
      "text": "Texto extraído",
      "confidence": 0.95,
      "bbox": [100, 200, 300, 250],
      "block_type": "text"
    }
  ],
  "tables": [
    {
      "rows": [["Col1", "Col2"], ["Val1", "Val2"]],
      "headers": ["Col1", "Col2"],
      "bbox": [50, 100, 400, 200],
      "confidence": 0.9
    }
  ],
  "figures": [
    {
      "caption": "Pie de figura",
      "bbox": [200, 300, 500, 400],
      "figure_type": "image",
      "confidence": 0.85
    }
  ],
  "raw_text": "Texto completo extraído...",
  "metadata": {
    "layout_elements_count": 5,
    "text_blocks_count": 3,
    "tables_count": 1,
    "figures_count": 1
  }
}
```

## Configuración

### Variables de entorno

- `HOST`: Host del servidor (default: 0.0.0.0)
- `PORT`: Puerto del servidor (default: 8000)
- `DEBUG`: Modo debug (default: True)
- `UPLOAD_DIR`: Directorio para archivos temporales (default: temp_uploads)
- `MAX_FILE_SIZE`: Tamaño máximo de archivo en bytes (default: 10MB)
- `TESSERACT_PATH`: Ruta a tesseract.exe (Windows)

### Configuración de OCR

- **Idioma**: Solo español
- **PSM**: Modo de segmentación de página (default: 6)
- **Confianza**: Filtrado por nivel de confianza

### Archivos Soportados

- **Imágenes**: .jpg, .jpeg, .png
- **Documentos**: .pdf (se convierte automáticamente a imagen)

### Procesador de Imágenes

#### **scikit-image (Principal)**
- ✅ **Ventajas**: Algoritmos modernos, mejor calidad de preprocesamiento
- ✅ **Ideal para**: Documentos complejos, imágenes con mucho ruido
- ✅ **Preprocesamiento avanzado**:
  - Normalización de intensidad
  - Filtro bilateral (reduce ruido preservando bordes)
  - Equalización adaptativa de histograma
  - Filtro gaussiano suave
  - Umbralización de Otsu
  - Operaciones morfológicas (apertura y cierre)

#### **PIL/Pillow (Alternativo)**
- ✅ **Ventajas**: Rápido, simple, buena integración con Tesseract
- ✅ **Ideal para**: Documentos simples, procesamiento en tiempo real
- ✅ **Preprocesamiento**: Mejora de contraste, nitidez, filtros básicos

#### **Comparar Rendimiento**
```bash
python benchmark_processors.py
```

## Desarrollo

### Estructura de la API

1. **main.py**: Punto de entrada de la aplicación
2. **config.py**: Configuración centralizada
3. **models.py**: Modelos de datos con Pydantic
4. **services/**: Lógica de negocio
5. **utils/**: Utilidades y helpers

### Agregar nuevas funcionalidades

1. **Nuevos endpoints**: Agregar en `main.py`
2. **Nuevos modelos**: Definir en `models.py`
3. **Nueva lógica**: Implementar en `services/`
4. **Nuevas utilidades**: Agregar en `utils/`

## Troubleshooting

### Error: Tesseract no encontrado
- Verificar instalación de Tesseract
- Configurar `TESSERACT_PATH` en variables de entorno

### Error: Modelo de LayoutParser no carga
- Verificar conexión a internet para descarga del modelo
- El procesamiento continuará sin detección de layout

### Error: Memoria insuficiente
- Reducir tamaño de archivos de entrada
- Ajustar configuración de LayoutParser

## Contribuir

1. Fork el proyecto
2. Crear rama para feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT.
# API_LectorFacturas
