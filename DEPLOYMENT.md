# Guía de Despliegue - API de Procesamiento de Imágenes

Esta guía te ayudará a desplegar tu API de procesamiento de imágenes con OCR en un servidor.

## 📋 Requisitos Previos

### En tu máquina local:
- Docker Desktop instalado
- Docker Compose instalado
- Git instalado

### En el servidor:
- Ubuntu 20.04+ o CentOS 8+ (recomendado)
- Docker instalado
- Docker Compose instalado
- Nginx (opcional, para proxy reverso)

## 🚀 Opciones de Despliegue

### Opción 1: Despliegue Local con Docker (Desarrollo)

```bash
# Clonar el repositorio
git clone <tu-repositorio>
cd Api

# Ejecutar script de despliegue
./deploy.sh desarrollo
# O en Windows:
.\deploy.ps1 desarrollo
```

### Opción 2: Despliegue en Servidor (Producción)

#### Paso 1: Preparar el servidor

```bash
# Conectar al servidor
ssh usuario@tu-servidor.com

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Reiniciar sesión para aplicar cambios
exit
ssh usuario@tu-servidor.com
```

#### Paso 2: Subir el código

```bash
# Clonar en el servidor
git clone <tu-repositorio>
cd Api

# O subir archivos manualmente
scp -r . usuario@tu-servidor.com:/ruta/destino/
```

#### Paso 3: Configurar variables de entorno

```bash
# Copiar archivo de producción
cp env.production .env

# Editar configuración si es necesario
nano .env
```

#### Paso 4: Desplegar

```bash
# Hacer ejecutable el script
chmod +x deploy.sh

# Desplegar en producción
./deploy.sh produccion
```

## 🔧 Configuración Avanzada

### Variables de Entorno Importantes

```bash
# En el archivo .env
HOST=0.0.0.0                    # Host de la API
PORT=8000                       # Puerto de la API
DEBUG=False                     # Modo debug (False en producción)
MAX_FILE_SIZE=10485760          # Tamaño máximo de archivo (10MB)
TESSERACT_PATH=/usr/bin/tesseract  # Ruta a Tesseract en Linux
```

### Configuración de Nginx (Opcional)

Si quieres usar Nginx como proxy reverso:

```bash
# Instalar Nginx
sudo apt update
sudo apt install nginx

# Configurar Nginx
sudo cp nginx.conf /etc/nginx/sites-available/api
sudo ln -s /etc/nginx/sites-available/api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Configuración de SSL (Producción)

```bash
# Generar certificados SSL (usando Let's Encrypt)
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d tu-dominio.com

# O usar certificados propios
mkdir ssl
# Copiar cert.pem y key.pem a la carpeta ssl/
```

## 📊 Monitoreo y Logs

### Ver logs de la aplicación

```bash
# Ver logs en tiempo real
./deploy.sh logs

# Ver estado de servicios
./deploy.sh status
```

### Logs importantes

- **Aplicación**: `docker-compose logs api`
- **Nginx**: `/var/log/nginx/access.log` y `/var/log/nginx/error.log`
- **Sistema**: `journalctl -u docker`

## 🔄 Actualizaciones

### Actualizar la aplicación

```bash
# Parar servicios
./deploy.sh stop

# Actualizar código
git pull origin main

# Reconstruir y desplegar
./deploy.sh produccion
```

### Backup de datos

```bash
# Backup de archivos temporales
tar -czf backup-$(date +%Y%m%d).tar.gz temp_uploads/

# Backup de logs
tar -czf logs-backup-$(date +%Y%m%d).tar.gz logs/
```

## 🛠️ Comandos Útiles

### Script de despliegue

```bash
# Desarrollo
./deploy.sh desarrollo

# Producción
./deploy.sh produccion

# Parar servicios
./deploy.sh stop

# Ver estado
./deploy.sh status

# Ver logs
./deploy.sh logs

# Limpiar sistema
./deploy.sh cleanup

# Ayuda
./deploy.sh help
```

### Docker Compose directo

```bash
# Construir imagen
docker-compose build

# Ejecutar en background
docker-compose up -d

# Ver logs
docker-compose logs -f

# Parar servicios
docker-compose down

# Limpiar volúmenes
docker-compose down -v
```

## 🚨 Solución de Problemas

### Error: Puerto ya en uso

```bash
# Ver qué proceso usa el puerto
sudo netstat -tulpn | grep :8000

# Matar proceso
sudo kill -9 <PID>
```

### Error: Permisos de Docker

```bash
# Agregar usuario al grupo docker
sudo usermod -aG docker $USER

# Reiniciar sesión
exit
ssh usuario@servidor
```

### Error: Memoria insuficiente

```bash
# Ver uso de memoria
docker stats

# Limpiar sistema Docker
docker system prune -a
```

### Error: Tesseract no encontrado

```bash
# Verificar instalación en contenedor
docker-compose exec api tesseract --version

# Reconstruir imagen
docker-compose build --no-cache
```

## 📈 Optimización de Rendimiento

### Configuración de recursos

```yaml
# En docker-compose.yml
services:
  api:
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
        reservations:
          memory: 1G
          cpus: '0.5'
```

### Configuración de Nginx

```nginx
# En nginx.conf
worker_processes auto;
worker_connections 1024;

# Cache de archivos estáticos
location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

## 🔒 Seguridad

### Configuración de firewall

```bash
# Permitir solo puertos necesarios
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
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

1. Revisa los logs: `./deploy.sh logs`
2. Verifica el estado: `./deploy.sh status`
3. Consulta la documentación de Docker
4. Revisa los issues del repositorio

## 🎯 URLs Importantes

- **API**: http://localhost:8080
- **Documentación**: http://localhost:8080/docs
- **Health Check**: http://localhost:8080/health
- **Nginx** (si está configurado): http://localhost
