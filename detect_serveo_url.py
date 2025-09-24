#!/usr/bin/env python3
"""
Script para detectar automáticamente la URL de serveo.net
"""
import subprocess
import re
import requests
import sys

def detect_serveo_url():
    """Detectar URL de serveo.net desde la salida del proceso SSH"""
    try:
        # Buscar procesos SSH que contengan serveo.net
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        
        if 'serveo.net' in result.stdout:
            lines = result.stdout.split('\n')
            for line in lines:
                if 'serveo.net' in line and 'ssh' in line:
                    print(f"🔍 Proceso SSH encontrado: {line}")
                    
                    # Intentar extraer información del proceso
                    # El proceso SSH no muestra la URL directamente
                    # Necesitamos usar otro método
                    
                    # Verificar conexiones de red
                    netstat_result = subprocess.run(['netstat', '-an'], capture_output=True, text=True)
                    if 'serveo.net' in netstat_result.stdout:
                        print("✅ Conexión serveo.net detectada")
                        
                        # Intentar obtener la URL desde la salida del túnel
                        # Esto requiere que el túnel esté activo y mostrando la URL
                        return try_get_url_from_tunnel()
        
        print("❌ No se encontró proceso serveo.net activo")
        return None
        
    except Exception as e:
        print(f"❌ Error detectando serveo.net: {e}")
        return None

def try_get_url_from_tunnel():
    """Intentar obtener URL desde la salida del túnel"""
    try:
        # Buscar en logs del sistema o procesos
        # Este método es limitado porque serveo.net no expone la URL fácilmente
        
        # Alternativa: usar un servicio de detección
        return detect_from_public_services()
        
    except Exception as e:
        print(f"❌ Error obteniendo URL del túnel: {e}")
        return None

def detect_from_public_services():
    """Detectar URL usando servicios públicos"""
    try:
        # Obtener IP pública
        response = requests.get("https://api.ipify.org", timeout=5)
        if response.status_code == 200:
            public_ip = response.text.strip()
            print(f"🌐 IP pública: {public_ip}")
            
            # Probar puertos comunes
            for port in [80, 8080, 8000]:
                test_url = f"http://{public_ip}:{port}"
                try:
                    response = requests.get(f"{test_url}/health", timeout=3)
                    if response.status_code == 200:
                        print(f"✅ API encontrada en: {test_url}")
                        return test_url
                except:
                    continue
        
        return None
        
    except Exception as e:
        print(f"❌ Error detectando desde servicios públicos: {e}")
        return None

def main():
    print("🔍 Detectando URL de serveo.net...")
    
    url = detect_serveo_url()
    
    if url:
        print(f"✅ URL detectada: {url}")
        print(f"💡 Configura con: export CALLBACK_BASE_URL={url}")
        return url
    else:
        print("❌ No se pudo detectar la URL automáticamente")
        print("💡 Configura manualmente con: export CALLBACK_BASE_URL=https://tu-url.serveo.net")
        return None

if __name__ == "__main__":
    main()
