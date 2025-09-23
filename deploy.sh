#!/bin/bash

# Script de despliegue para la API de procesamiento de imágenes
# Uso: ./deploy.sh [desarrollo|produccion]

set -e  # Salir si hay algún error

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para imprimir mensajes
print_message() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar que Docker esté instalado
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker no está instalado. Por favor instala Docker primero."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose no está instalado. Por favor instala Docker Compose primero."
        exit 1
    fi
    
    print_message "Docker y Docker Compose están instalados ✓"
}

# Crear directorios necesarios
create_directories() {
    print_message "Creando directorios necesarios..."
    mkdir -p temp_uploads
    mkdir -p logs
    mkdir -p ssl
    print_message "Directorios creados ✓"
}

# Construir y ejecutar en modo desarrollo
deploy_development() {
    print_message "Desplegando en modo DESARROLLO..."
    
    # Copiar archivo de entorno
    if [ ! -f .env ]; then
        cp env_example.txt .env
        print_warning "Archivo .env creado desde env_example.txt"
    fi
    
    # Construir imagen
    print_message "Construyendo imagen Docker..."
    docker-compose build
    
    # Ejecutar en modo desarrollo
    print_message "Iniciando servicios en modo desarrollo..."
    docker-compose up -d
    
    print_message "API desplegada en modo desarrollo ✓"
    print_message "URL: http://localhost:8080"
    print_message "Documentación: http://localhost:8080/docs"
}

# Construir y ejecutar en modo producción
deploy_production() {
    print_message "Desplegando en modo PRODUCCIÓN..."
    
    # Copiar archivo de entorno de producción
    if [ ! -f .env ]; then
        cp env.production .env
        print_warning "Archivo .env creado desde env.production"
    fi
    
    # Construir imagen
    print_message "Construyendo imagen Docker para producción..."
    docker-compose build --no-cache
    
    # Ejecutar en modo producción con nginx
    print_message "Iniciando servicios en modo producción..."
    docker-compose --profile production up -d
    
    print_message "API desplegada en modo producción ✓"
    print_message "URL: http://localhost (con nginx)"
    print_message "API directa: http://localhost:8080"
}

# Parar servicios
stop_services() {
    print_message "Deteniendo servicios..."
    docker-compose down
    print_message "Servicios detenidos ✓"
}

# Ver estado de los servicios
status_services() {
    print_message "Estado de los servicios:"
    docker-compose ps
}

# Ver logs
view_logs() {
    print_message "Mostrando logs de la API..."
    docker-compose logs -f api
}

# Limpiar sistema Docker
cleanup() {
    print_warning "Limpiando sistema Docker..."
    docker-compose down -v
    docker system prune -f
    print_message "Limpieza completada ✓"
}

# Función principal
main() {
    print_message "=== Script de Despliegue API OCR ==="
    
    # Verificar Docker
    check_docker
    
    # Crear directorios
    create_directories
    
    # Procesar argumentos
    case "${1:-desarrollo}" in
        "desarrollo"|"dev"|"development")
            deploy_development
            ;;
        "produccion"|"prod"|"production")
            deploy_production
            ;;
        "stop"|"parar")
            stop_services
            ;;
        "status"|"estado")
            status_services
            ;;
        "logs")
            view_logs
            ;;
        "cleanup"|"limpiar")
            cleanup
            ;;
        "help"|"ayuda"|"-h"|"--help")
            echo "Uso: $0 [comando]"
            echo ""
            echo "Comandos disponibles:"
            echo "  desarrollo, dev, development  - Desplegar en modo desarrollo (por defecto)"
            echo "  produccion, prod, production  - Desplegar en modo producción"
            echo "  stop, parar                   - Detener servicios"
            echo "  status, estado                - Ver estado de servicios"
            echo "  logs                          - Ver logs en tiempo real"
            echo "  cleanup, limpiar              - Limpiar sistema Docker"
            echo "  help, ayuda                   - Mostrar esta ayuda"
            ;;
        *)
            print_error "Comando no reconocido: $1"
            print_message "Usa '$0 help' para ver comandos disponibles"
            exit 1
            ;;
    esac
}

# Ejecutar función principal
main "$@"
