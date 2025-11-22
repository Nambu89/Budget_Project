"""
Cliente para OpenAI directo.

Implementa la conexión con la API de OpenAI
para usar modelos de lenguaje directamente.
"""

from typing import Optional
from openai import OpenAI
from loguru import logger

from ...config.settings import settings


class OpenAIClient:
    """
    Cliente para interactuar con OpenAI directamente.
    
    Proporciona una interfaz simplificada para hacer
    llamadas a la API de OpenAI.
    
    Attributes:
        client: Cliente de OpenAI
        model: Modelo a usar
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
    ):
        """
        Inicializa el cliente de OpenAI.
        
        Args:
            api_key: API Key de OpenAI (opcional, usa settings)
            model: Modelo a usar (opcional, usa settings)
        """
        self.api_key = api_key or settings.openai_api_key
        self.model = model or settings.openai_model
        
        # Validar configuración
        if not self.api_key:
            raise ValueError(
                "OpenAI no está configurado. "
                "Configura OPENAI_API_KEY en .env"
            )
        
        # Crear cliente
        self.client = OpenAI(api_key=self.api_key)
        
        logger.info(f"✓ OpenAI Client inicializado (model: {self.model})")
    
    def chat_completion(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> str:
        """
        Realiza una llamada de chat completion.
        
        Args:
            messages: Lista de mensajes del chat
            temperature: Temperatura de generación (0-2)
            max_tokens: Máximo de tokens a generar
            **kwargs: Argumentos adicionales para la API
            
        Returns:
            str: Respuesta del modelo
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_completion_tokens=max_tokens,
                **kwargs
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error en OpenAI chat completion: {e}")
            raise
    
    def simple_completion(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> str:
        """
        Realiza una llamada simple con un prompt.
        
        Args:
            prompt: Prompt del usuario
            system_prompt: Prompt del sistema (opcional)
            temperature: Temperatura de generación
            max_tokens: Máximo de tokens
            
        Returns:
            str: Respuesta del modelo
        """
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        return self.chat_completion(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
    
    def is_available(self) -> bool:
        """
        Verifica si el servicio está disponible.
        
        Returns:
            bool: True si está disponible
        """
        try:
            # Hacer una llamada mínima de prueba
            self.simple_completion(
                prompt="test",
                max_tokens=5,
            )
            return True
        except Exception as e:
            logger.warning(f"OpenAI no disponible: {e}")
            return False