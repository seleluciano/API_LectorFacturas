# 🚀 Guía de Uso con Jupyter

Esta guía te explica cómo usar tu API de procesamiento de imágenes con Jupyter Notebook.

## 📋 Ventajas de usar Jupyter

- ✅ **Interfaz interactiva**: Botones y widgets para controlar la API
- ✅ **Subida de archivos**: Drag & drop para probar imágenes
- ✅ **Visualización**: Ver resultados directamente en el notebook
- ✅ **Desarrollo**: Probar cambios en tiempo real
- ✅ **Documentación**: Todo en un solo lugar

## 🛠️ Instalación

### Paso 1: Instalar dependencias

```bash
# Instalar dependencias de Jupyter
python install_jupyter_dependencies.py

# O instalar manualmente
pip install jupyter jupyterlab ipywidgets requests uvicorn[standard]
```

### Paso 2: Iniciar Jupyter

```bash
# Opción 1: Usar el script automático
python start_jupyter.py

# Opción 2: Iniciar manualmente
jupyter lab --ip=0.0.0.0 --port=8888 --no-browser
```

### Paso 3: Abrir el notebook

1. Ve a `http://localhost:8888`
2. Abre el archivo `api_jupyter.ipynb`
3. Ejecuta las celdas en orden

## 🎯 Uso del Notebook

### 1. **Configuración Inicial**
- Ejecuta las primeras celdas para importar librerías
- Configura las variables de entorno
- Carga la aplicación FastAPI

### 2. **Iniciar el Servidor**
- Haz clic en "🚀 Iniciar API"
- Espera a que aparezca "✅ Servidor iniciado correctamente"
- La API estará disponible en `http://localhost:8080`

### 3. **Verificar Estado**
- Haz clic en "🔍 Verificar Estado"
- Deberías ver "✅ Servidor funcionando correctamente"

### 4. **Probar con Archivos**
- Usa el widget de selección de archivos
- Arrastra y suelta una imagen o PDF
- Ve los resultados directamente en el notebook

### 5. **Acceder a Documentación**
- Haz clic en "🔗 Mostrar Enlaces"
- Accede a Swagger UI, ReDoc, etc.

## 🔧 Configuración Avanzada

### Cambiar Puerto

Si el puerto 8080 está ocupado, cambia la configuración:

```python
# En la celda de configuración
os.environ['PORT'] = '3000'  # Cambiar a otro puerto
```

### Configurar Tesseract

```python
# Para Windows
os.environ['TESSERACT_PATH'] = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Para Linux
os.environ['TESSERACT_PATH'] = '/usr/bin/tesseract'
```

### Modo de Producción

```python
# Cambiar a modo producción
os.environ['DEBUG'] = 'False'
os.environ['FAST_MODE'] = 'True'
```

## 📊 Funcionalidades del Notebook

### **Widgets Interactivos**
- 🚀 Botón para iniciar/detener la API
- 🔍 Verificación de estado del servidor
- 📤 Subida de archivos con drag & drop
- 🔗 Enlaces a documentación

### **Procesamiento de Archivos**
- Detección automática de tipo (factura vs imagen general)
- Extracción de texto con Tesseract
- Análisis de layout con LayoutParser
- Resultados estructurados

### **Visualización de Resultados**
- Información del archivo procesado
- Campos extraídos de facturas
- Texto extraído de imágenes
- Métricas de rendimiento

## 🚨 Solución de Problemas

### Error: Puerto ocupado

```bash
# Ver qué está usando el puerto
sudo netstat -tulpn | grep :8080

# Cambiar puerto en el notebook
os.environ['PORT'] = '3000'
```

### Error: Tesseract no encontrado

```bash
# Instalar Tesseract
sudo apt install tesseract-ocr tesseract-ocr-spa

# Verificar instalación
tesseract --version
```

### Error: Dependencias faltantes

```bash
# Reinstalar dependencias
python install_jupyter_dependencies.py

# O instalar manualmente
pip install -r requirements.txt
```

### Error: Jupyter no inicia

```bash
# Verificar instalación
jupyter --version

# Reinstalar Jupyter
pip install --upgrade jupyter jupyterlab
```

## 🔄 Flujo de Trabajo Recomendado

1. **Desarrollo**: Usa Jupyter para probar cambios
2. **Testing**: Sube archivos de prueba
3. **Debugging**: Verifica logs y resultados
4. **Producción**: Usa Docker para despliegue

## 📝 Comandos Útiles

### Iniciar Jupyter

```bash
# Desarrollo local
python start_jupyter.py

# Con configuración específica
jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root
```

### Verificar Estado

```bash
# Ver procesos de Jupyter
ps aux | grep jupyter

# Ver puertos en uso
netstat -tulpn | grep :8888
```

### Limpiar Recursos

```bash
# Detener Jupyter
pkill -f jupyter

# Limpiar archivos temporales
rm -rf temp_uploads/*
```

## 🎯 URLs Importantes

- **Jupyter Lab**: `http://localhost:8888`
- **API**: `http://localhost:8080`
- **Documentación**: `http://localhost:8080/docs`
- **Health Check**: `http://localhost:8080/health`

## 💡 Consejos

1. **Ejecuta las celdas en orden** para evitar errores
2. **Verifica el estado** antes de subir archivos
3. **Usa archivos pequeños** para pruebas rápidas
4. **Reinicia el kernel** si hay problemas
5. **Guarda el notebook** regularmente

## 🔗 Enlaces Útiles

- [Documentación de Jupyter](https://jupyter.org/documentation)
- [Widgets de Jupyter](https://ipywidgets.readthedocs.io/)
- [FastAPI con Jupyter](https://fastapi.tiangolo.com/)
- [Tesseract OCR](https://tesseract-ocr.github.io/)

¡Disfruta usando tu API con Jupyter! 🚀
