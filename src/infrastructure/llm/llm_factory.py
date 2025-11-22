"""
Factory para clientes LLM.

Implementa el patrón Factory para crear el cliente
de LLM apropiado según la configuración.
"""

from typing import Union, Protocol
from loguru import logger

from ...config.settings import settings
from .azure_client import AzureOpenAIClient
from .openai_client import OpenAIClient


class LLMClient(Protocol):
    """
    Protocolo que define la interfaz de un cliente LLM.
    
    Permite usar typing con cualquier cliente que implemente
    los métodos requeridos.
    """
    
    def chat_completion(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> str:
        """Realiza una llamada de chat completion."""
        ...
    
    def simple_completion(
        self,
        prompt: str,
        system_prompt: str = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> str:
        """Realiza una llamada simple con un prompt."""
        ...
    
    def is_available(self) -> bool:
        """Verifica si el servicio está disponible."""
        ...


class LLMFactory:
    """
    Factory para crear clientes LLM.
    
    Crea el cliente apropiado según la configuración
    en las variables de entorno.
    """
    
    # Usar dict para evitar problemas con variables de clase
    _state = {"instance": None}
    
    @classmethod
    def create(cls, force_new: bool = False) -> Union[AzureOpenAIClient, OpenAIClient]:
        """
        Crea o retorna el cliente LLM configurado.
        
        Implementa un singleton para reutilizar la conexión.
        
        Args:
            force_new: Si True, crea una nueva instancia
            
        Returns:
            Cliente LLM configurado (Azure o OpenAI)
            
        Raises:
            ValueError: Si no hay ningún proveedor configurado
        """
        if cls._state["instance"] is not None and not force_new:
            return cls._state["instance"]
        
        provider = settings.llm_provider.lower()
        
        if provider == "azure":
            if not settings.is_azure_configured():
                raise ValueError(
                    "Azure OpenAI seleccionado pero no configurado. "
                    "Verifica AZURE_OPENAI_ENDPOINT y AZURE_OPENAI_API_KEY"
                )
            cls._state["instance"] = AzureOpenAIClient()
            logger.info("✓ Usando Azure OpenAI como proveedor LLM")
            
        elif provider == "openai":
            if not settings.is_openai_configured():
                raise ValueError(
                    "OpenAI seleccionado pero no configurado. "
                    "Verifica OPENAI_API_KEY"
                )
            cls._state["instance"] = OpenAIClient()
            logger.info("✓ Usando OpenAI directo como proveedor LLM")
            
        else:
            raise ValueError(
                f"Proveedor LLM no reconocido: {provider}. "
                "Usa 'azure' o 'openai'"
            )
        
        return cls._state["instance"]
    
    @classmethod
    def get_client(cls) -> Union[AzureOpenAIClient, OpenAIClient]:
        """
        Obtiene el cliente LLM (alias de create para claridad).
        
        Returns:
            Cliente LLM configurado
        """
        return cls.create()
    
    @classmethod
    def reset(cls) -> None:
        """Resetea el singleton (útil para testing)."""
        cls._state["instance"] = None
        logger.debug("LLM Factory reseteado")
    
    @classmethod
    def get_provider_info(cls) -> dict:
        """
        Retorna información del proveedor configurado.
        
        Returns:
            dict: Información del proveedor
        """
        return {
            "provider": settings.llm_provider,
            "azure_configured": settings.is_azure_configured(),
            "openai_configured": settings.is_openai_configured(),
            "active_config": settings.get_active_llm_config(),
        }


def get_llm_client() -> Union[AzureOpenAIClient, OpenAIClient]:
    """
    Función de conveniencia para obtener el cliente LLM.
    
    Returns:
        Cliente LLM configurado
    """
    return LLMFactory.get_client()