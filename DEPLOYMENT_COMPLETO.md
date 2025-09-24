# 🚀 Guía Completa de Despliegue - API de Procesamiento de Imágenes

Esta guía te explica paso a paso cómo desplegar tu API de procesamiento de imágenes con Jupyter en un servidor y acceder desde una red pública.

## 📋 Requisitos Previos

### En el servidor:
- Ubuntu 20.04+ o CentOS 8+ (recomendado)
- Python 3.8+ instalado
- Tesseract OCR instalado
- Acceso a internet

### En tu máquina local:
- Navegador web
- Conexión a internet

## 🔧 Instalación y Configuración

### Paso 1: Preparar el servidor

```bash
# Instalar dependencias del sistema
sudo apt update
sudo apt install python3 python3-pip python3-venv

# Instalar Tesseract OCR
sudo apt install tesseract-ocr tesseract-ocr-spa tesseract-ocr-eng

# Instalar dependencias adicionales
sudo apt install libgl1-mesa-glx libglib2.0-0 libsm6 libxext6 libxrender-dev
```

### Paso 2: Configurar el proyecto

```bash
# Clonar o subir el proyecto
cd /ruta/del/proyecto

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
python install_jupyter_dependencies.py
```

### Paso 3: Configurar Jupyter

```bash
# Generar configuración
jupyter notebook --generate-config

# Crear contraseña
jupyter server password

# Editar configuración
nano ~/.jupyter/jupyter_notebook_config.py
```

Agregar al final del archivo:
```python
c.NotebookApp.ip = '0.0.0.0'
c.NotebookApp.port = 8083
c.NotebookApp.open_browser = False
c.NotebookApp.allow_root = True
```

## 🚀 Ejecución de Servicios

### Terminal 1: Jupyter Lab

```bash
# Activar entorno virtual
source venv/bin/activate

# Ir al directorio del proyecto
cd API_LectorFacturas

# Iniciar Jupyter
jupyter notebook --ip=0.0.0.0 --no-browser --port=8083
```

**Salida esperada:**
```
[I] Jupyter Server 2.17.0 is running at:
[I] http://localhost.localdomain:8083/tree
[I] http://127.0.0.1:8083/tree
```

### Terminal 2: API FastAPI

```bash
# Activar entorno virtual
source venv/bin/activate

# Ir al directorio del proyecto
cd API_LectorFacturas

# Iniciar la API
python -c "
import uvicorn
from main import app
uvicorn.run(app, host='0.0.0.0', port=8080, reload=False)
"
```

**Salida esperada:**
```
INFO:     Started server process [PID]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8080
```

## 🌐 Configuración de Túneles (Port Forwarding)

### Terminal 3: Túnel para Jupyter

```bash
# Crear túnel para Jupyter (puerto 8083)
ssh -R 80:localhost:8083 serveo.net
```

**Salida esperada:**
```
Forwarding HTTP traffic from https://abc123.serveo.net
```

### Terminal 4: Túnel para API

```bash
# Crear túnel para API (puerto 8080)
ssh -R 80:localhost:8080 serveo.net
```

**Salida esperada:**
```
Forwarding HTTP traffic from https://def456.serveo.net
```

## 📱 Acceso desde Máquina Local

### URLs de Acceso:

- **Jupyter Lab**: `https://abc123.serveo.net`
- **API**: `https://def456.serveo.net`
- **Documentación API**: `https://def456.serveo.net/docs`
- **Health Check**: `https://def456.serveo.net/health`

### Pasos para Acceder:

1. **Abrir navegador** en tu máquina local
2. **Ir a la URL de Jupyter** (ej: `https://abc123.serveo.net`)
3. **Ingresar contraseña** configurada con `jupyter server password`
4. **Abrir el notebook** `api_jupyter.ipynb`
5. **Ejecutar las celdas** para iniciar la API desde Jupyter

## 🔧 Comandos de Verificación

### Verificar que los servicios estén corriendo:

```bash
# Verificar Jupyter
netstat -tulpn | grep :8083

# Verificar API
netstat -tulpn | grep :8080

# Verificar procesos
ps aux | grep jupyter
ps aux | grep python
```

### Verificar conectividad local:

```bash
# Probar Jupyter localmente
curl http://localhost:8083

# Probar API localmente
curl http://localhost:8080/health
```

## 🛠️ Solución de Problemas

### Error: Puerto ocupado

```bash
# Ver qué está usando el puerto
sudo netstat -tulpn | grep :8080

# Matar proceso
sudo kill -9 <PID>

# O usar puerto diferente
python -c "
import uvicorn
from main import app
uvicorn.run(app, host='0.0.0.0', port=8081, reload=False)
"
```

### Error: Tesseract no encontrado

```bash
# Verificar instalación
tesseract --version

# Verificar ruta
which tesseract

# Configurar en .env
echo "TESSERACT_PATH=/usr/bin/tesseract" >> .env
```

### Error: Dependencias faltantes

```bash
# Reinstalar dependencias
pip install -r requirements.txt
python install_jupyter_dependencies.py

# Verificar instalación
python -c "import fastapi, uvicorn, jupyter; print('✅ OK')"
```

### Error: Túnel no funciona

```bash
# Probar con puerto diferente
ssh -R 80:localhost:8080 serveo.net

# O usar ngrok
./ngrok http 8080

# O usar localtunnel
lt --port 8080
```

## 🔄 Comandos de Mantenimiento

### Iniciar todo el sistema:

```bash
# Terminal 1: Jupyter
source venv/bin/activate
cd API_LectorFacturas
jupyter notebook --ip=0.0.0.0 --no-browser --port=8083

# Terminal 2: API
source venv/bin/activate
cd API_LectorFacturas
python -c "
import uvicorn
from main import app
uvicorn.run(app, host='0.0.0.0', port=8080, reload=False)
"

# Terminal 3: Túnel Jupyter
ssh -R 80:localhost:8083 serveo.net

# Terminal 4: Túnel API
ssh -R 80:localhost:8080 serveo.net
```

### Detener servicios:

```bash
# Detener Jupyter (Ctrl+C en Terminal 1)
# Detener API (Ctrl+C en Terminal 2)
# Detener túneles (Ctrl+C en Terminal 3 y 4)
```

### Actualizar el sistema:

```bash
# Parar servicios
pkill -f jupyter
pkill -f python

# Actualizar código
git pull origin main

# Actualizar dependencias
pip install -r requirements.txt

# Reiniciar servicios
# (Seguir comandos de "Iniciar todo el sistema")
```

## 📊 Monitoreo

### Ver logs en tiempo real:

```bash
# Logs de Jupyter
tail -f ~/.local/share/jupyter/runtime/jupyter-*.log

# Logs de la API
# (Ver salida directa en Terminal 2)

# Ver procesos activos
ps aux | grep -E "(jupyter|python|uvicorn)"
```

### Verificar estado de túneles:

```bash
# Ver conexiones SSH activas
ps aux | grep ssh

# Ver puertos en uso
netstat -tulpn | grep -E "(8080|8083)"
```

## 🎯 URLs Importantes

- **Jupyter Lab**: `https://abc123.serveo.net`
- **API**: `https://def456.serveo.net`
- **Documentación**: `https://def456.serveo.net/docs`
- **Health Check**: `https://def456.serveo.net/health`
- **Swagger UI**: `https://def456.serveo.net/docs`
- **ReDoc**: `https://def456.serveo.net/redoc`

## 💡 Consejos

1. **Mantén las 4 terminales abiertas** mientras uses el sistema
2. **Guarda las URLs** de los túneles en un archivo de texto
3. **Verifica el estado** de los servicios regularmente
4. **Usa contraseñas seguras** para Jupyter
5. **Monitorea los logs** para detectar problemas

## 🔒 Seguridad

- **Cambia la contraseña** de Jupyter regularmente
- **No compartas las URLs** de los túneles
- **Detén los servicios** cuando no los uses
- **Usa HTTPS** (serveo.net proporciona SSL automático)

## 📞 Soporte

Si tienes problemas:

1. **Revisa los logs** de cada terminal
2. **Verifica el estado** de los servicios
3. **Comprueba la conectividad** de red
4. **Reinicia los servicios** si es necesario

---

**¡Tu API de procesamiento de imágenes está lista para usar!** 🎉
