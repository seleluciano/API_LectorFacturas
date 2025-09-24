#!/usr/bin/env python3
"""
Módulo para descubrir automáticamente la URL pública de la API
"""
import requests
import os
import time
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class URLDiscoverer:
    def __init__(self):
        self.discovered_url = None
        self.external_api_url = "http://127.0.0.1:8000"
        self.register_endpoint = "/api/gestion/facturas/cargar-imagenes/"  # Endpoint que ya existe
    
    def discover_public_url(self) -> Optional[str]:
        """
        Descubrir la URL pública de la API usando diferentes métodos
        """
        # Método 1: Verificar variable de entorno
        env_url = os.getenv("CALLBACK_BASE_URL")
        if env_url and self._test_url(env_url):
            logger.info(f"✅ URL encontrada en variable de entorno: {env_url}")
            return env_url
        
        # Método 2: Intentar detectar serveo.net automáticamente
        serveo_url = self._detect_serveo_url()
        if serveo_url:
            logger.info(f"✅ URL de serveo.net detectada: {serveo_url}")
            return serveo_url
        
        # Método 3: Probar URLs comunes de tunneling
        common_urls = [
            "https://localhost.run",
            "https://ngrok.io",
            "https://serveo.net",
            "https://loca.lt"
        ]
        
        for base_url in common_urls:
            # Intentar descubrir URL automáticamente
            discovered = self._discover_from_service(base_url)
            if discovered:
                logger.info(f"✅ URL descubierta desde {base_url}: {discovered}")
                return discovered
        
        # Método 4: Usar servicios de detección de IP
        public_ip = self._get_public_ip()
        if public_ip:
            # Probar puertos comunes
            for port in [8080, 8000, 3000, 5000]:
                test_url = f"http://{public_ip}:{port}"
                if self._test_url(test_url):
                    logger.info(f"✅ URL descubierta por IP pública: {test_url}")
                    return test_url
        
        logger.warning("⚠️ No se pudo descubrir la URL pública automáticamente")
        return None
    
    def _discover_from_service(self, service: str) -> Optional[str]:
        """Descubrir URL desde un servicio específico"""
        try:
            if service == "localhost.run":
                # localhost.run expone automáticamente
                response = requests.get("https://localhost.run", timeout=5)
                if response.status_code == 200:
                    return "https://localhost.run"
            
            elif service == "ngrok.io":
                # Verificar si ngrok está corriendo
                try:
                    response = requests.get("http://localhost:4040/api/tunnels", timeout=2)
                    if response.status_code == 200:
                        tunnels = response.json().get("tunnels", [])
                        if tunnels:
                            return tunnels[0].get("public_url")
                except:
                    pass
            
            elif service == "serveo.net":
                # serveo.net no tiene API de descubrimiento
                pass
                
        except Exception as e:
            logger.debug(f"Error descubriendo desde {service}: {e}")
        
        return None
    
    def _detect_serveo_url(self) -> Optional[str]:
        """Detectar URL de serveo.net automáticamente"""
        try:
            # Método 1: Verificar procesos SSH activos
            import subprocess
            result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
            if 'serveo.net' in result.stdout:
                # Buscar en la salida del proceso
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'serveo.net' in line and 'ssh' in line:
                        # Extraer URL de la línea
                        # Formato típico: ssh -R 80:localhost:8080 serveo.net
                        # La URL se genera automáticamente
                        logger.info("🔍 Proceso serveo.net detectado, intentando descubrir URL...")
                        return self._try_serveo_urls()
            
            # Método 2: Verificar conexiones de red
            result = subprocess.run(['netstat', '-an'], capture_output=True, text=True)
            if 'serveo.net' in result.stdout:
                logger.info("🔍 Conexión serveo.net detectada, intentando descubrir URL...")
                return self._try_serveo_urls()
            
            return None
            
        except Exception as e:
            logger.debug(f"Error detectando serveo.net: {e}")
            return None
    
    def _try_serveo_urls(self) -> Optional[str]:
        """Intentar descubrir URL de serveo.net probando patrones comunes"""
        try:
            # Obtener IP pública
            public_ip = self._get_public_ip()
            if not public_ip:
                return None
            
            # Probar diferentes patrones de URL de serveo.net
            # serveo.net usa hashes basados en la IP y puerto
            import hashlib
            
            # Generar posibles hashes
            possible_hashes = []
            
            # Hash de IP + puerto
            for port in [80, 8080, 8000]:
                data = f"{public_ip}:{port}"
                hash_obj = hashlib.md5(data.encode())
                possible_hashes.append(hash_obj.hexdigest())
            
            # Hash de timestamp aproximado
            import time
            current_time = int(time.time())
            for offset in range(-3600, 3600, 300):  # ±1 hora en intervalos de 5 min
                data = f"{public_ip}:{current_time + offset}"
                hash_obj = hashlib.md5(data.encode())
                possible_hashes.append(hash_obj.hexdigest())
            
            # Probar URLs
            for hash_val in possible_hashes[:10]:  # Limitar a 10 intentos
                test_url = f"https://{hash_val}.serveo.net"
                if self._test_url(test_url):
                    logger.info(f"✅ URL de serveo.net encontrada: {test_url}")
                    return test_url
            
            return None
            
        except Exception as e:
            logger.debug(f"Error probando URLs de serveo.net: {e}")
            return None
    
    def _get_public_ip(self) -> Optional[str]:
        """Obtener IP pública"""
        try:
            response = requests.get("https://api.ipify.org", timeout=5)
            if response.status_code == 200:
                return response.text.strip()
        except:
            pass
        return None
    
    def _test_url(self, url: str) -> bool:
        """Probar si una URL responde"""
        try:
            response = requests.get(f"{url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def register_with_external_api(self, callback_url: str) -> bool:
        """
        Registrar la URL de callback con la API externa
        
        Args:
            callback_url: URL de callback a registrar
            
        Returns:
            True si se registró exitosamente
        """
        try:
            # Enviar datos de registro como si fuera una factura
            registration_data = {
                "imagen": {
                    "filename": "registration.json",
                    "content_type": "application/json",
                    "data": "REGISTRO_DE_CALLBACK_URL",  # Identificador especial
                    "size": 0
                },
                "callback_url": f"{callback_url}/api/external/response",
                "status_url": f"{callback_url}/api/external/status",
                "registration_info": {
                    "name": "API de Procesamiento de Imágenes",
                    "version": "1.0.0",
                    "endpoints": [
                        "/process-and-send-factura",
                        "/process-factura-only",
                        "/api/external/response",
                        "/api/external/status"
                    ]
                }
            }
            
            logger.info(f"📡 Registrando URL con API externa: {callback_url}")
            
            response = requests.post(
                f"{self.external_api_url}{self.register_endpoint}",
                json=registration_data,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                logger.info("✅ URL registrada exitosamente con API externa")
                return True
            else:
                logger.warning(f"⚠️ API externa respondió con código: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error registrando con API externa: {e}")
            return False
    
    def auto_discover_and_register(self) -> Optional[str]:
        """
        Descubrir URL automáticamente y registrar con API externa
        
        Returns:
            URL descubierta o None si falló
        """
        # Descubrir URL
        discovered_url = self.discover_public_url()
        
        if not discovered_url:
            logger.error("❌ No se pudo descubrir la URL pública")
            return None
        
        # Registrar con API externa
        if self.register_with_external_api(discovered_url):
            self.discovered_url = discovered_url
            logger.info(f"🎉 URL registrada exitosamente: {discovered_url}")
            return discovered_url
        else:
            logger.warning("⚠️ URL descubierta pero no se pudo registrar con API externa")
            return discovered_url

# Instancia global
url_discoverer = URLDiscoverer()
