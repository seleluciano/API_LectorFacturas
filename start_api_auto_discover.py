#!/usr/bin/env python3
"""
Script para iniciar la API con descubrimiento automático de URL
"""
import subprocess
import time
import sys
import os

def start_tunnel():
    """Iniciar túnel serveo.net"""
    print("🌐 Iniciando túnel serveo.net...")
    
    # Iniciar serveo.net en background
    process = subprocess.Popen(
        ["ssh", "-R", "80:localhost:8080", "serveo.net"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Esperar un poco para que el túnel se establezca
    time.sleep(3)
    
    print("✅ Túnel iniciado")
    return process

def start_api():
    """Iniciar la API FastAPI"""
    print("🚀 Iniciando API FastAPI...")
    
    try:
        # Iniciar la API
        cmd = [
            sys.executable, "-c",
            """
import uvicorn
from main import app
uvicorn.run(app, host='0.0.0.0', port=8080, reload=False)
"""
        ]
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n🛑 Deteniendo API...")
    except Exception as e:
        print(f"❌ Error iniciando API: {e}")

def main():
    print("=" * 60)
    print("🚀 INICIADOR DE API CON DESCUBRIMIENTO AUTOMÁTICO")
    print("=" * 60)
    
    try:
        # Iniciar túnel
        tunnel_process = start_tunnel()
        
        # Iniciar API
        start_api()
        
    except KeyboardInterrupt:
        print("\n🛑 Deteniendo servicios...")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        # Limpiar procesos
        try:
            tunnel_process.terminate()
        except:
            pass

if __name__ == "__main__":
    main()
