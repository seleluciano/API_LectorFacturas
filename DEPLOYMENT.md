# Guía de Despliegue - API de Procesamiento de Imágenes

Esta guía te ayudará a desplegar tu API de procesamiento de imágenes con OCR en un servidor usando Jupyter.

## 📋 Requisitos Previos

### En tu máquina local:
- Python 3.8+ instalado
- Git instalado

### En el servidor:
- Ubuntu 20.04+ o CentOS 8+ (recomendado)
- Python 3.8+ instalado
- Tesseract OCR instalado
- Jupyter instalado

## 🚀 Opciones de Despliegue

### Opción 1: Despliegue Local con Jupyter (Desarrollo)

```bash
# Clonar el repositorio
git clone <tu-repositorio>
cd Api

# Instalar dependencias
python install_jupyter_dependencies.py

# Iniciar Jupyter
python start_jupyter.py
```

### Opción 2: Despliegue en Servidor (Producción)

#### Paso 1: Preparar el servidor

```bash
# Conectar al servidor
ssh usuario@tu-servidor.com

# Instalar Python y dependencias del sistema
sudo apt update
sudo apt install python3 python3-pip python3-venv

# Instalar Tesseract OCR
sudo apt install tesseract-ocr tesseract-ocr-spa tesseract-ocr-eng

# Instalar dependencias adicionales
sudo apt install libgl1-mesa-glx libglib2.0-0 libsm6 libxext6 libxrender-dev
```

#### Paso 2: Subir el código

```bash
# Clonar en el servidor
git clone <tu-repositorio>
cd Api

# O subir archivos manualmente
scp -r . usuario@tu-servidor.com:/ruta/destino/
```

#### Paso 3: Configurar entorno virtual

```bash
# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
python install_jupyter_dependencies.py
```

#### Paso 4: Configurar variables de entorno

```bash
# Copiar archivo de configuración
cp env.local .env

# Editar configuración si es necesario
nano .env
```

#### Paso 5: Desplegar

```bash
# Iniciar Jupyter
python start_jupyter.py

# O iniciar directamente la API
python start_server.py
```

## 🔧 Configuración Avanzada

### Variables de Entorno Importantes

```bash
# En el archivo .env
HOST=0.0.0.0                    # Host de la API
PORT=8080                       # Puerto de la API
DEBUG=True                      # Modo debug
MAX_FILE_SIZE=10485760          # Tamaño máximo de archivo (10MB)
TESSERACT_PATH=/usr/bin/tesseract  # Ruta a Tesseract en Linux
FAST_MODE=True                  # Modo rápido para mejor rendimiento
```

### Configuración de Tesseract

```bash
# Verificar instalación
tesseract --version

# Instalar idiomas adicionales
sudo apt install tesseract-ocr-spa tesseract-ocr-eng

# Verificar idiomas disponibles
tesseract --list-langs
```

### Configuración de Jupyter

```bash
# Configurar Jupyter para acceso remoto
jupyter lab --generate-config

# Editar configuración
nano ~/.jupyter/jupyter_lab_config.py

# Agregar estas líneas:
c.ServerApp.ip = '0.0.0.0'
c.ServerApp.port = 8888
c.ServerApp.open_browser = False
c.ServerApp.allow_root = True
```

## 📊 Monitoreo y Logs

### Ver logs de la aplicación

```bash
# Ver logs de Jupyter
jupyter lab --log-level=DEBUG

# Ver logs de la API
python start_server.py

# Ver procesos en ejecución
ps aux | grep python
ps aux | grep jupyter
```

### Logs importantes

- **Aplicación**: Salida directa de `python start_server.py`
- **Jupyter**: `~/.jupyter/jupyter_lab_config.py`
- **Sistema**: `journalctl -u jupyter` (si está como servicio)

## 🔄 Actualizaciones

### Actualizar la aplicación

```bash
# Parar servicios
pkill -f jupyter
pkill -f python

# Actualizar código
git pull origin main

# Actualizar dependencias
pip install -r requirements.txt

# Reiniciar servicios
python start_jupyter.py
```

### Backup de datos

```bash
# Backup de archivos temporales
tar -czf backup-$(date +%Y%m%d).tar.gz temp_uploads/

# Backup de notebooks
tar -czf notebooks-backup-$(date +%Y%m%d).tar.gz *.ipynb
```

## 🛠️ Comandos Útiles

### Comandos de Jupyter

```bash
# Iniciar Jupyter
python start_jupyter.py

# Iniciar directamente la API
python start_server.py

# Instalar dependencias
python install_jupyter_dependencies.py

# Ver procesos en ejecución
ps aux | grep jupyter
ps aux | grep python
```

### Comandos de Python

```bash
# Activar entorno virtual
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar tests
python -m pytest tests/

# Verificar instalación
python -c "import fastapi, uvicorn; print('✅ Dependencias OK')"
```

## 🚨 Solución de Problemas

### Error: Puerto ya en uso

```bash
# Ver qué proceso usa el puerto
sudo netstat -tulpn | grep :8080

# Matar proceso
sudo kill -9 <PID>

# O cambiar puerto en .env
nano .env
# Cambiar PORT=8080 por PORT=3000
```

### Error: Tesseract no encontrado

```bash
# Instalar Tesseract
sudo apt install tesseract-ocr tesseract-ocr-spa

# Verificar instalación
tesseract --version

# Verificar ruta en .env
nano .env
# TESSERACT_PATH=/usr/bin/tesseract
```

### Error: Dependencias faltantes

```bash
# Reinstalar dependencias
pip install -r requirements.txt
python install_jupyter_dependencies.py

# Verificar instalación
python -c "import fastapi, uvicorn, jupyter; print('✅ OK')"
```

### Error: Jupyter no inicia

```bash
# Verificar instalación
jupyter --version

# Reinstalar Jupyter
pip install --upgrade jupyter jupyterlab

# Verificar configuración
jupyter lab --generate-config
```

## 📈 Optimización de Rendimiento

### Configuración de Python

```bash
# En .env
FAST_MODE=True
DEBUG=False
MAX_FILE_SIZE=10485760

# Configuración de Tesseract
OCR_CONFIG={"lang": "spa+eng", "config": "--psm 3 --oem 3"}
```

### Configuración de Jupyter

```bash
# En ~/.jupyter/jupyter_lab_config.py
c.ServerApp.port = 8888
c.ServerApp.ip = '0.0.0.0'
c.ServerApp.open_browser = False
c.ServerApp.allow_root = True
c.ServerApp.token = ''
c.ServerApp.password = ''
```

## 🔒 Seguridad

### Configuración de firewall

```bash
# Permitir solo puertos necesarios
sudo ufw allow 22    # SSH
sudo ufw allow 8888  # Jupyter
sudo ufw allow 8080  # API
sudo ufw enable
```

### Variables de entorno sensibles

```bash
# Nunca subir archivos .env al repositorio
echo ".env" >> .gitignore

# Usar variables de entorno del sistema
export DEBUG=False
export MAX_FILE_SIZE=10485760
```

## 📞 Soporte

Si tienes problemas con el despliegue:

1. Revisa los logs: `python start_server.py`
2. Verifica el estado: `ps aux | grep python`
3. Consulta la documentación de Jupyter
4. Revisa los issues del repositorio

## 🎯 URLs Importantes

- **Jupyter Lab**: http://localhost:8888
- **API**: http://localhost:8080
- **Documentación**: http://localhost:8080/docs
- **Health Check**: http://localhost:8080/health
