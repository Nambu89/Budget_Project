"""
Cliente para OpenAI directo.

Implementa la conexión con la API de OpenAI
para usar modelos de lenguaje directamente.

NOTA: gpt-5-mini y otros modelos de razonamiento:
- NO soportan el parámetro 'temperature' (debe ser 1)
- Usan 'max_completion_tokens' en lugar de 'max_tokens'
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
    
    Soporta modelos de razonamiento como gpt-5-mini.
    
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
        
        # Detectar si es modelo de razonamiento (no soporta temperature)
        self.is_reasoning_model = "gpt-5" in self.model.lower() or "o1" in self.model.lower()
        
        # Validar configuración
        if not self.api_key:
            raise ValueError(
                "OpenAI no está configurado. "
                "Configura OPENAI_API_KEY en .env"
            )
        
        # Crear cliente
        self.client = OpenAI(api_key=self.api_key)
        
        logger.info(f"✓ OpenAI Client inicializado (model: {self.model}, reasoning: {self.is_reasoning_model})")
    
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
            temperature: Temperatura de generación (IGNORADA en modelos de razonamiento)
            max_tokens: Máximo de tokens a generar
            **kwargs: Argumentos adicionales para la API
            
        Returns:
            str: Respuesta del modelo
        """
        try:
            # Preparar parámetros base
            # IMPORTANTE: Modelos de razonamiento (gpt-5-mini) usan tokens para
            # "pensar" internamente (~64+ tokens para prompts simples, más para complejos).
            # Necesitan mínimo 1000 tokens para producir respuestas útiles en prompts complejos.
            effective_tokens = max_tokens
            if self.is_reasoning_model and max_tokens < 1000:
                effective_tokens = 1000
            
            params = {
                "model": self.model,
                "messages": messages,
                "max_completion_tokens": effective_tokens,
            }
            
            # Solo añadir temperature si NO es modelo de razonamiento
            if not self.is_reasoning_model:
                params["temperature"] = temperature
            
            # Añadir kwargs (excluyendo temperature para modelos de razonamiento)
            for key, value in kwargs.items():
                if self.is_reasoning_model and key == "temperature":
                    continue  # Ignorar temperature para modelos de razonamiento
                params[key] = value
            
            response = self.client.chat.completions.create(**params)
            
            # Manejar respuesta None
            content = response.choices[0].message.content
            return content or ""
            
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
            temperature: Temperatura de generación (IGNORADA en modelos de razonamiento)
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
            response = self.simple_completion(
                temperature=1,
                prompt="Responde OK",
                max_completion_tokens=10,
            )
            return len(response) > 0
        except Exception as e:
            logger.warning(f"OpenAI no disponible: {e}")
            return False