#!/bin/bash

echo "🚀 Iniciando API con ngrok..."

# Verificar si ngrok está instalado
if ! command -v ngrok &> /dev/null; then
    echo "❌ Ngrok no está instalado"
    echo "📥 Descargando ngrok..."
    
    # Descargar ngrok
    wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
    tar -xzf ngrok-v3-stable-linux-amd64.tgz
    sudo mv ngrok /usr/local/bin/
    
    echo "✅ Ngrok instalado"
    echo "⚠️ Configura tu authtoken: ngrok authtoken <tu_token>"
fi

# Iniciar ngrok en background
echo "🌐 Iniciando túnel ngrok..."
ngrok http 8080 &
NGROK_PID=$!

# Esperar a que ngrok se inicie
sleep 3

# Obtener URL de ngrok
echo "🔍 Obteniendo URL de ngrok..."
NGROK_URL=$(curl -s http://localhost:4040/api/tunnels | grep -o '"public_url":"[^"]*' | grep -o 'https://[^"]*' | head -1)

if [ -z "$NGROK_URL" ]; then
    echo "❌ No se pudo obtener URL de ngrok"
    kill $NGROK_PID
    exit 1
fi

echo "✅ URL de ngrok: $NGROK_URL"

# Configurar variable de entorno
export CALLBACK_BASE_URL=$NGROK_URL
echo "✅ URL configurada: $CALLBACK_BASE_URL"

# Iniciar API
echo "🚀 Iniciando API FastAPI..."
python -c "
import uvicorn
from main import app
uvicorn.run(app, host='0.0.0.0', port=8080, reload=False)
"

# Limpiar al salir
kill $NGROK_PID
