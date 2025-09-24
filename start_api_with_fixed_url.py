#!/usr/bin/env python3
"""
Script para iniciar la API con URL fija usando ngrok
"""
import subprocess
import time
import requests
import os
import sys

def start_ngrok(port=8080, subdomain=None):
    """
    Iniciar ngrok con subdominio fijo
    
    Args:
        port: Puerto local
        subdomain: Subdominio fijo (requiere cuenta premium)
    """
    try:
        if subdomain:
            # Usar subdominio fijo (requiere cuenta premium)
            cmd = ["ngrok", "http", str(port), "--subdomain", subdomain]
            print(f"🚀 Iniciando ngrok con subdominio fijo: {subdomain}")
        else:
            # Usar URL aleatoria
            cmd = ["ngrok", "http", str(port)]
            print(f"🚀 Iniciando ngrok con URL aleatoria")
        
        # Iniciar ngrok en background
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Esperar a que ngrok se inicie
        time.sleep(3)
        
        # Obtener URL de ngrok
        try:
            response = requests.get("http://localhost:4040/api/tunnels", timeout=5)
            if response.status_code == 200:
                tunnels = response.json()["tunnels"]
                if tunnels:
                    public_url = tunnels[0]["public_url"]
                    print(f"✅ Ngrok iniciado: {public_url}")
                    return public_url, process
        except:
            pass
        
        print("⚠️ No se pudo obtener URL de ngrok automáticamente")
        return None, process
        
    except Exception as e:
        print(f"❌ Error iniciando ngrok: {e}")
        return None, None

def start_api():
    """Iniciar la API FastAPI"""
    try:
        print("🚀 Iniciando API FastAPI...")
        cmd = [
            sys.executable, "-c",
            "import uvicorn; from main import app; uvicorn.run(app, host='0.0.0.0', port=8080, reload=False)"
        ]
        subprocess.run(cmd)
    except Exception as e:
        print(f"❌ Error iniciando API: {e}")

def main():
    print("=" * 60)
    print("🚀 INICIADOR DE API CON URL FIJA")
    print("=" * 60)
    
    # Verificar si ngrok está instalado
    try:
        subprocess.run(["ngrok", "version"], capture_output=True, check=True)
    except:
        print("❌ Ngrok no está instalado. Instálalo desde: https://ngrok.com/")
        sys.exit(1)
    
    # Verificar autenticación de ngrok
    try:
        subprocess.run(["ngrok", "authtoken", "--help"], capture_output=True, check=True)
        print("✅ Ngrok está configurado")
    except:
        print("⚠️ Configura tu authtoken de ngrok: ngrok authtoken <tu_token>")
    
    # Opciones
    print("\nOpciones:")
    print("1. Usar subdominio fijo (requiere cuenta premium)")
    print("2. Usar URL aleatoria")
    print("3. Solo iniciar API (sin túnel)")
    
    choice = input("\nSelecciona opción (1-3): ").strip()
    
    if choice == "1":
        subdomain = input("Ingresa subdominio fijo: ").strip()
        if not subdomain:
            print("❌ Subdominio requerido")
            sys.exit(1)
        
        public_url, ngrok_process = start_ngrok(8080, subdomain)
        if public_url:
            # Configurar variable de entorno
            os.environ["CALLBACK_BASE_URL"] = public_url
            print(f"✅ URL configurada: {public_url}")
            
            # Iniciar API
            start_api()
        else:
            print("❌ No se pudo iniciar ngrok")
    
    elif choice == "2":
        public_url, ngrok_process = start_ngrok(8080)
        if public_url:
            # Configurar variable de entorno
            os.environ["CALLBACK_BASE_URL"] = public_url
            print(f"✅ URL configurada: {public_url}")
            print("⚠️ Esta URL cambiará cada vez que reinicies")
            
            # Iniciar API
            start_api()
        else:
            print("❌ No se pudo iniciar ngrok")
    
    elif choice == "3":
        print("🚀 Iniciando solo API (sin túnel)")
        start_api()
    
    else:
        print("❌ Opción inválida")

if __name__ == "__main__":
    main()
