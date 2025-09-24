"""
Cliente para comunicarse con la API externa de gestión de facturas
"""
import httpx
import os
import asyncio
from typing import Dict, Any, Optional
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FacturasAPIClient:
    def __init__(self):
        self.base_url = "http://127.0.0.1:8000"
        self.endpoint = "/api/gestion/facturas/cargar-imagenes/"
        self.timeout = 30.0
        self.retry_attempts = 3
        self.retry_delay = 1.0  # segundos
    
    async def enviar_factura(self, datos_factura: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Enviar datos de factura procesada a la API externa
        
        Args:
            datos_factura: Diccionario con los datos de la factura procesada
            
        Returns:
            Respuesta de la API externa o None si hay error
        """
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "FacturaProcessor/1.0"
        }
        
        # Agregar URLs de callback en headers
        if "callback_url" in datos_factura:
            headers["X-Callback-URL"] = datos_factura["callback_url"]
        if "status_url" in datos_factura:
            headers["X-Status-URL"] = datos_factura["status_url"]
        
        # Si hay API key configurada, agregar autenticación
        api_key = os.getenv("FACTURAS_API_KEY")
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        
        for attempt in range(self.retry_attempts):
            try:
                async with httpx.AsyncClient() as client:
                    logger.info(f"Enviando factura a API externa (intento {attempt + 1}/{self.retry_attempts})")
                    
                    response = await client.post(
                        f"{self.base_url}{self.endpoint}",
                        json=datos_factura,
                        headers=headers,
                        timeout=self.timeout
                    )
                    
                    response.raise_for_status()
                    logger.info("Factura enviada exitosamente a API externa")
                    return response.json()
                    
            except httpx.TimeoutException:
                logger.warning(f"Timeout al comunicarse con API de facturas (intento {attempt + 1})")
                if attempt < self.retry_attempts - 1:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
                    continue
                return {"error": "Timeout al comunicarse con API externa"}
                
            except httpx.HTTPStatusError as e:
                logger.error(f"Error HTTP {e.response.status_code}: {e.response.text}")
                if attempt < self.retry_attempts - 1:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
                    continue
                return {
                    "error": f"Error HTTP {e.response.status_code}",
                    "details": e.response.text
                }
                
            except Exception as e:
                logger.error(f"Error inesperado: {e}")
                if attempt < self.retry_attempts - 1:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
                    continue
                return {"error": f"Error inesperado: {str(e)}"}
        
        return {"error": "Falló después de todos los intentos"}
    
    async def verificar_conectividad(self) -> bool:
        """
        Verificar si la API externa está disponible
        
        Returns:
            True si está disponible, False en caso contrario
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/health",
                    timeout=5.0
                )
                return response.status_code == 200
        except:
            return False
    
    def configurar_url(self, nueva_url: str):
        """
        Configurar nueva URL para la API externa
        
        Args:
            nueva_url: Nueva URL base de la API
        """
        self.base_url = nueva_url
        logger.info(f"URL de API externa actualizada a: {nueva_url}")

# Instancia global del cliente
facturas_client = FacturasAPIClient()
