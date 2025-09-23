# Script de despliegue para la API de procesamiento de imágenes (PowerShell)
# Uso: .\deploy.ps1 [desarrollo|produccion]

param(
    [Parameter(Position=0)]
    [string]$Mode = "desarrollo"
)

# Función para imprimir mensajes
function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# Verificar que Docker esté instalado
function Test-Docker {
    try {
        $null = Get-Command docker -ErrorAction Stop
        $null = Get-Command docker-compose -ErrorAction Stop
        Write-Info "Docker y Docker Compose están instalados ✓"
        return $true
    }
    catch {
        Write-Error "Docker o Docker Compose no están instalados. Por favor instala Docker Desktop primero."
        return $false
    }
}

# Crear directorios necesarios
function New-RequiredDirectories {
    Write-Info "Creando directorios necesarios..."
    New-Item -ItemType Directory -Force -Path "temp_uploads" | Out-Null
    New-Item -ItemType Directory -Force -Path "logs" | Out-Null
    New-Item -ItemType Directory -Force -Path "ssl" | Out-Null
    Write-Info "Directorios creados ✓"
}

# Desplegar en modo desarrollo
function Deploy-Development {
    Write-Info "Desplegando en modo DESARROLLO..."
    
    # Copiar archivo de entorno
    if (-not (Test-Path ".env")) {
        Copy-Item "env_example.txt" ".env"
        Write-Warning "Archivo .env creado desde env_example.txt"
    }
    
    # Construir imagen
    Write-Info "Construyendo imagen Docker..."
    docker-compose build
    
    # Ejecutar en modo desarrollo
    Write-Info "Iniciando servicios en modo desarrollo..."
    docker-compose up -d
    
    Write-Info "API desplegada en modo desarrollo ✓"
    Write-Info "URL: http://localhost:8080"
    Write-Info "Documentación: http://localhost:8080/docs"
}

# Desplegar en modo producción
function Deploy-Production {
    Write-Info "Desplegando en modo PRODUCCIÓN..."
    
    # Copiar archivo de entorno de producción
    if (-not (Test-Path ".env")) {
        Copy-Item "env.production" ".env"
        Write-Warning "Archivo .env creado desde env.production"
    }
    
    # Construir imagen
    Write-Info "Construyendo imagen Docker para producción..."
    docker-compose build --no-cache
    
    # Ejecutar en modo producción con nginx
    Write-Info "Iniciando servicios en modo producción..."
    docker-compose --profile production up -d
    
    Write-Info "API desplegada en modo producción ✓"
    Write-Info "URL: http://localhost (con nginx)"
    Write-Info "API directa: http://localhost:8080"
}

# Parar servicios
function Stop-Services {
    Write-Info "Deteniendo servicios..."
    docker-compose down
    Write-Info "Servicios detenidos ✓"
}

# Ver estado de los servicios
function Get-ServiceStatus {
    Write-Info "Estado de los servicios:"
    docker-compose ps
}

# Ver logs
function Show-Logs {
    Write-Info "Mostrando logs de la API..."
    docker-compose logs -f api
}

# Limpiar sistema Docker
function Clear-Docker {
    Write-Warning "Limpiando sistema Docker..."
    docker-compose down -v
    docker system prune -f
    Write-Info "Limpieza completada ✓"
}

# Función principal
function Main {
    Write-Info "=== Script de Despliegue API OCR ==="
    
    # Verificar Docker
    if (-not (Test-Docker)) {
        exit 1
    }
    
    # Crear directorios
    New-RequiredDirectories
    
    # Procesar modo
    switch ($Mode.ToLower()) {
        { $_ -in @("desarrollo", "dev", "development") } {
            Deploy-Development
        }
        { $_ -in @("produccion", "prod", "production") } {
            Deploy-Production
        }
        { $_ -in @("stop", "parar") } {
            Stop-Services
        }
        { $_ -in @("status", "estado") } {
            Get-ServiceStatus
        }
        { $_ -eq "logs" } {
            Show-Logs
        }
        { $_ -in @("cleanup", "limpiar") } {
            Clear-Docker
        }
        { $_ -in @("help", "ayuda") } {
            Write-Host "Uso: .\deploy.ps1 [comando]"
            Write-Host ""
            Write-Host "Comandos disponibles:"
            Write-Host "  desarrollo, dev, development  - Desplegar en modo desarrollo (por defecto)"
            Write-Host "  produccion, prod, production  - Desplegar en modo producción"
            Write-Host "  stop, parar                   - Detener servicios"
            Write-Host "  status, estado                - Ver estado de servicios"
            Write-Host "  logs                          - Ver logs en tiempo real"
            Write-Host "  cleanup, limpiar              - Limpiar sistema Docker"
            Write-Host "  help, ayuda                   - Mostrar esta ayuda"
        }
        default {
            Write-Error "Comando no reconocido: $Mode"
            Write-Info "Usa '.\deploy.ps1 help' para ver comandos disponibles"
            exit 1
        }
    }
}

# Ejecutar función principal
Main
