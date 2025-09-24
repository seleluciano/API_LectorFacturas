#!/usr/bin/env python3
"""
Script para actualizar la URL de callback cuando cambie el túnel
"""
import os
import sys
import requests
import json

def update_callback_url(new_url):
    """
    Actualizar la URL de callback en el archivo .env
    
    Args:
        new_url: Nueva URL del túnel (ej: https://abc123.serveo.net)
    """
    try:
        # Leer archivo .env actual
        env_file = ".env"
        env_content = {}
        
        if os.path.exists(env_file):
            with open(env_file, 'r') as f:
                for line in f:
                    if '=' in line and not line.strip().startswith('#'):
                        key, value = line.strip().split('=', 1)
                        env_content[key] = value
        
        # Actualizar URL de callback
        env_content['CALLBACK_BASE_URL'] = new_url
        
        # Escribir archivo .env actualizado
        with open(env_file, 'w') as f:
            for key, value in env_content.items():
                f.write(f"{key}={value}\n")
        
        print(f"✅ URL de callback actualizada a: {new_url}")
        
        # Verificar que la API esté funcionando
        try:
            response = requests.get(f"{new_url}/callback-urls", timeout=5)
            if response.status_code == 200:
                print("✅ API responde correctamente")
                print(f"📋 URLs de callback:")
                data = response.json()
                print(f"   - Callback: {data['callback_url']}")
                print(f"   - Status: {data['status_url']}")
            else:
                print("⚠️ API no responde correctamente")
        except Exception as e:
            print(f"⚠️ No se pudo verificar la API: {e}")
        
    except Exception as e:
        print(f"❌ Error actualizando URL: {e}")

def main():
    if len(sys.argv) != 2:
        print("Uso: python update_callback_url.py <nueva_url>")
        print("Ejemplo: python update_callback_url.py https://abc123.serveo.net")
        sys.exit(1)
    
    new_url = sys.argv[1]
    update_callback_url(new_url)

if __name__ == "__main__":
    main()
