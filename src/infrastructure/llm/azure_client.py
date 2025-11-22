"""
Cliente para Azure AI Foundry.

Implementa la conexión con Azure AI Foundry usando la nueva API v1
para modelos como gpt-5-mini, gpt-4.1, etc.
"""

from typing import Optional
from openai import OpenAI
from loguru import logger

from ...config.settings import settings


class AzureOpenAIClient:
    """
    Cliente para interactuar con Azure AI Foundry.
    
    Usa la nueva API v1 que es compatible con el cliente OpenAI estándar.
    Soporta la Responses API para modelos nuevos.
    
    Attributes:
        client: Cliente OpenAI configurado para Azure
        deployment: Nombre del deployment a usar
    """
    
    def __init__(
        self,
        endpoint: Optional[str] = None,
        api_key: Optional[str] = None,
        deployment: Optional[str] = None,
    ):
        """
        Inicializa el cliente de Azure AI Foundry.
        
        Args:
            endpoint: Endpoint de Azure OpenAI (opcional, usa settings)
            api_key: API Key de Azure (opcional, usa settings)
            deployment: Nombre del deployment (opcional, usa settings)
        """
        self.endpoint = endpoint or settings.azure_openai_endpoint
        self.api_key = api_key or settings.azure_openai_api_key
        self.deployment = deployment or settings.azure_openai_deployment_name
        
        # Validar configuración
        if not self.endpoint or not self.api_key:
            raise ValueError(
                "Azure AI Foundry no está configurado. "
                "Configura AZURE_OPENAI_ENDPOINT y AZURE_OPENAI_API_KEY en .env"
            )
        
        # Construir base_url para API v1
        # Asegurar que el endpoint no termine en /
        base_endpoint = self.endpoint.rstrip('/')
        self.base_url = f"{base_endpoint}/openai/v1/"
        
        # Crear cliente usando OpenAI estándar con base_url de Azure
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
        )
        
        logger.info(f"✓ Azure AI Foundry Client inicializado (deployment: {self.deployment})")
    
    def chat_completion(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> str:
        """
        Realiza una llamada usando Responses API.
        
        Args:
            messages: Lista de mensajes del chat
            temperature: Temperatura de generación (ignorado en algunos modelos)
            max_tokens: Máximo de tokens a generar
            **kwargs: Argumentos adicionales para la API
            
        Returns:
            str: Respuesta del modelo
        """
        try:
            # Convertir mensajes a formato de input para Responses API
            if len(messages) == 1:
                input_text = messages[0]["content"]
            else:
                # Construir input con contexto
                parts = []
                for msg in messages:
                    role = msg.get("role", "user")
                    content = msg.get("content", "")
                    if role == "system":
                        parts.append(f"[Sistema]: {content}")
                    elif role == "assistant":
                        parts.append(f"[Asistente]: {content}")
                    else:
                        parts.append(f"[Usuario]: {content}")
                input_text = "\n".join(parts)
            
            # Usar Responses API
            response = self.client.responses.create(
                model=self.deployment,
                input=input_text,
            )
            
            # Obtener texto de respuesta
            if hasattr(response, 'output_text') and response.output_text:
                return response.output_text
            elif hasattr(response, 'output') and response.output:
                return str(response.output)
            
            return ""
            
        except Exception as e:
            logger.error(f"Error en Azure AI Foundry completion: {e}")
            raise
    
    def simple_completion(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> str:
        """
        Realiza una llamada simple con un prompt usando Responses API.
        
        Args:
            prompt: Prompt del usuario
            system_prompt: Prompt del sistema (opcional)
            temperature: Temperatura de generación
            max_tokens: Máximo de tokens
            
        Returns:
            str: Respuesta del modelo
        """
        try:
            # Construir input
            if system_prompt:
                input_text = f"[Instrucciones]: {system_prompt}\n\n{prompt}"
            else:
                input_text = prompt
            
            # Usar Responses API directamente
            response = self.client.responses.create(
                model=self.deployment,
                input=input_text,
            )
            
            # Obtener texto de respuesta
            if hasattr(response, 'output_text') and response.output_text:
                return response.output_text
            elif hasattr(response, 'output') and response.output:
                return str(response.output)
            
            return ""
            
        except Exception as e:
            logger.error(f"Error en Azure AI Foundry simple completion: {e}")
            raise
    
    def is_available(self) -> bool:
        """
        Verifica si el servicio está disponible.
        
        Returns:
            bool: True si está disponible
        """
        try:
            response = self.simple_completion(prompt="Responde OK")
            return len(response) > 0
        except Exception as e:
            logger.warning(f"Azure AI Foundry no disponible: {e}")
            return False