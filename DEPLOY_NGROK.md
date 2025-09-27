# Deploy con Ngrok - API de Procesamiento de Imágenes con OCR

## 🚀 Información del Deploy

### URL del Deploy
**URL Principal:** [https://skye-nonsensate-clavately.ngrok-free.dev](https://skye-nonsensate-clavately.ngrok-free.dev)

### Estado del Servicio
- ✅ **API Activa**: Funcionando correctamente
- ✅ **Endpoints Disponibles**: Todos los endpoints están operativos
- ✅ **Procesamiento OCR**: LayoutParser + Tesseract funcionando
- ✅ **API Externa**: Integración con sistema de facturas habilitada

## 📋 Endpoints Disponibles

### 🔍 Endpoints Principales

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/` | GET | Información general de la API |
| `/health` | GET | Estado del servicio y conectividad |
| `/process-image` | POST | **INTELIGENTE** - Detecta facturas automáticamente |
| `/process-multiple-images` | POST | **INTELIGENTE** - Procesa múltiples archivos |
| `/process-invoice` | POST | Solo procesamiento de facturas |
| `/process-invoices-structured` | POST | Solo facturas con datos estructurados |

### 🔄 Endpoints de Integración Externa

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/process-and-send-factura` | POST | Procesar y enviar a API externa |
| `/process-factura-only` | POST | Solo procesar, sin enviar |
| `/api/external/response` | POST | Recibir respuesta de API externa |
| `/api/external/status` | POST | Recibir estado de API externa |
| `/callback-urls` | GET | Obtener URLs de callback actuales |

### 📊 Endpoints de Evaluación

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/evaluate-metrics` | POST | Evaluar métricas del modelo |
| `/batch-benchmark` | POST | Benchmark de lotes |

## 🛠️ Configuración del Deploy

### Servidor Local
- **Host**: `0.0.0.0`
- **Puerto**: `8000`
- **Framework**: FastAPI
- **Workers**: 1 (optimizado para desarrollo)

### Configuración Ngrok
```bash
# Comando utilizado para crear el túnel
ngrok http 8000 --domain=skye-nonsensate-clavately.ngrok-free.dev
```

### Gestión de Procesos con Screen
Para mantener el servidor ejecutándose en segundo plano, se utiliza `screen`:

```bash
# Crear una nueva sesión de screen para el servidor
screen -S server

# Dentro de la sesión, ejecutar el servidor
python start_server.py

# Desconectar de la sesión: Ctrl+A, luego presionar D
# El servidor continúa ejecutándose en segundo plano

# Crear una nueva sesión de screen para ngrok
screen -S ngrok

# Dentro de la sesión, ejecutar ngrok
ngrok http 8000 --domain=skye-nonsensate-clavately.ngrok-free.dev

# Desconectar de la sesión: Ctrl+A, luego presionar D
# Ngrok continúa ejecutándose en segundo plano

# Reconectar a las sesiones
screen -r servidor  # Para el servidor
screen -r ngrok     # Para ngrok

# Listar todas las sesiones activas
screen -ls

# Terminar sesiones específicas
screen -S servidor -X quit
screen -S ngrok -X quit
```

**Ventajas de usar Screen:**
- ✅ **Persistencia**: El servidor continúa ejecutándose aunque se cierre la terminal
- ✅ **Reconexión**: Puedes reconectarte a la sesión en cualquier momento
- ✅ **Múltiples sesiones**: Puedes tener varios procesos ejecutándose simultáneamente
- ✅ **Logs visibles**: Puedes ver los logs del servidor en tiempo real

### Variables de Entorno
```env
HOST=0.0.0.0
PORT=8000
DEBUG=True
WORKERS=1
LOG_LEVEL=info
UPLOAD_DIR=temp_uploads
MAX_FILE_SIZE=52428800  # 50MB
TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe
FAST_MODE=True
```

## 📁 Archivos Soportados

### Formatos de Imagen
- ✅ `.jpg` / `.jpeg`
- ✅ `.png`
- ✅ `.pdf` (conversión automática a imagen)

### Límites
- **Tamaño máximo**: 50MB por archivo
- **Múltiples archivos**: Máximo 10 archivos por request
- **Benchmark**: Máximo 100 archivos

## 🔧 Tecnologías Utilizadas

### Backend
- **FastAPI**: Framework web moderno y rápido
- **Python 3.8+**: Lenguaje principal
- **Uvicorn**: Servidor ASGI

### Procesamiento de Imágenes
- **LayoutParser**: Detección de elementos de layout
- **Tesseract OCR**: Extracción de texto
- **scikit-image**: Preprocesamiento avanzado de imágenes
- **PIL/Pillow**: Procesamiento básico de imágenes

### Modelos de IA
- **PubLayNet**: Modelo de detección de layout
- **Faster R-CNN**: Detección de objetos
- **PSM 3**: Segmentación automática de página completa

## 📊 Capacidades del Sistema

### Procesamiento Inteligente
- 🔍 **Detección Automática**: Identifica facturas vs. documentos generales
- 📄 **Extracción Estructurada**: Campos específicos de facturas argentinas
- 🎯 **Alta Precisión**: Múltiples algoritmos de preprocesamiento
- ⚡ **Procesamiento Rápido**: Optimizado para velocidad

### Campos Extraídos de Facturas
- **Datos del Vendedor**: Razón social, CUIT
- **Datos del Comprador**: Razón social, CUIT, condición IVA
- **Datos de la Factura**: Número, fecha, punto de venta
- **Importes**: Subtotal, IVA, total
- **Items**: Productos/servicios detallados
- **Condiciones**: Condición de venta

### Métricas de Evaluación
- **Precisión de Campos**: Exactitud por campo específico
- **CER/WER**: Caracter Error Rate / Word Error Rate
- **Confianza**: Score de confianza del procesamiento
- **Latencia**: Tiempo de procesamiento
- **Throughput**: Archivos procesados por segundo

## 🔗 Integración Externa

### API de Facturas
- **URL Base**: Configurada en `config_external.py`
- **Callback URL**: `https://d3e7dadb0157c65efb1d427e8d21a9b5.serveo.net`
- **Endpoints de Callback**:
  - `/api/external/response` - Respuestas de procesamiento
  - `/api/external/status` - Actualizaciones de estado

### Flujo de Integración
1. **Procesamiento Local**: Extracción de datos con OCR
2. **Envío a API Externa**: Imagen + datos extraídos
3. **Callback de Respuesta**: Recepción de resultados externos
4. **Callback de Estado**: Actualizaciones de progreso

## 🧪 Testing y Validación

### Endpoints de Prueba
```bash
# Verificar estado
curl https://skye-nonsensate-clavately.ngrok-free.dev/health

# Procesar imagen
curl -X POST https://skye-nonsensate-clavately.ngrok-free.dev/process-image \
  -F "file=@factura.jpg"

# Procesar múltiples archivos
curl -X POST https://skye-nonsensate-clavately.ngrok-free.dev/process-multiple-images \
  -F "files=@factura1.jpg" \
  -F "files=@factura2.pdf"
```

### Documentación Interactiva
- **Swagger UI**: `https://skye-nonsensate-clavately.ngrok-free.dev/docs`
- **ReDoc**: `https://skye-nonsensate-clavately.ngrok-free.dev/redoc`

## 📈 Monitoreo y Logs

### Logs del Sistema
- **Nivel**: INFO
- **Formato**: JSON estructurado
- **Información registrada**:
  - Requests y respuestas
  - Tiempos de procesamiento
  - Errores y excepciones
  - Métricas de rendimiento

### Métricas Disponibles
- Tiempo de procesamiento por archivo
- Número de elementos detectados
- Confianza del OCR
- Estado de conectividad con APIs externas

## 🔒 Seguridad y Configuración

### CORS
- **Orígenes permitidos**: `*` (configurable)
- **Métodos**: GET, POST, PUT, DELETE
- **Headers**: Todos permitidos

### Validación de Archivos
- **Tipos permitidos**: Verificación por extensión y MIME type
- **Tamaño máximo**: 50MB por archivo
- **Limpieza automática**: Archivos temporales eliminados después del procesamiento

## 🚨 Troubleshooting

### Problemas Comunes

#### Error: "Tesseract no encontrado"
```bash
# Verificar instalación
tesseract --version

# Configurar ruta en variables de entorno
TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe
```

#### Error: "Modelo LayoutParser no carga"
- Verificar conexión a internet
- El procesamiento continuará sin detección de layout
- Los resultados serán menos precisos pero funcionales

#### Error: "Memoria insuficiente"
- Reducir tamaño de archivos de entrada
- Procesar archivos individualmente
- Ajustar configuración de workers

### Logs de Debug
```bash
# Activar modo debug
DEBUG=True
LOG_LEVEL=debug
```

## 📞 Soporte

### Contacto
- **Repositorio**: [GitHub del proyecto]
- **Documentación**: README.md
- **Issues**: Usar sistema de issues de GitHub

### Recursos Adicionales
- **Documentación FastAPI**: https://fastapi.tiangolo.com/
- **LayoutParser**: https://layout-parser.readthedocs.io/
- **Tesseract OCR**: https://github.com/tesseract-ocr/tesseract

---

## 🎯 Próximos Pasos

### Mejoras Planificadas
- [ ] Implementar autenticación JWT
- [ ] Agregar rate limiting
- [ ] Optimizar para procesamiento en lotes grandes
- [ ] Implementar cache de resultados
- [ ] Agregar soporte para más idiomas
- [ ] Integrar con más APIs externas

### Deploy en Producción
- [ ] Configurar HTTPS permanente
- [ ] Implementar load balancing
- [ ] Configurar monitoreo avanzado
- [ ] Establecer backup automático
- [ ] Implementar CI/CD pipeline

---

**Última actualización**: $(date)  
**Versión del Deploy**: 1.0.0  
**Estado**: ✅ Activo y Funcional
