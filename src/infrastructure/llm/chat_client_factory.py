"""
Factory para clientes de chat del Agent Framework.

Crea el cliente de chat apropiado (OpenAI o Azure) según
la configuración del entorno.
"""

from typing import Union
from loguru import logger

from ...config.settings import settings


def get_chat_client():
    """
    Factory que retorna el cliente de chat según LLM_PROVIDER.
    
    Soporta:
    - OpenAI directo (gpt-5-mini, gpt-4o, etc.)
    - Azure OpenAI (deployments en Azure)
    
    Returns:
        ChatClient configurado según el proveedor
        
    Raises:
        ValueError: Si el proveedor no está configurado correctamente
    """
    provider = settings.llm_provider.lower()
    
    if provider == "openai":
        if not settings.is_openai_configured():
            raise ValueError(
                "OpenAI seleccionado pero no configurado. "
                "Verifica OPENAI_API_KEY en .env"
            )
        
        # Importar aquí para evitar error si no está instalado
        from agent_framework.openai import OpenAIChatClient
        
        client = OpenAIChatClient(
            api_key=settings.openai_api_key,
            model_id=settings.openai_model,
        )
        logger.info(f"✓ OpenAIChatClient inicializado (model_id: {settings.openai_model})")
        return client
        
    elif provider == "azure":
        if not settings.is_azure_configured():
            raise ValueError(
                "Azure OpenAI seleccionado pero no configurado. "
                "Verifica AZURE_OPENAI_ENDPOINT y AZURE_OPENAI_API_KEY en .env"
            )
        
        from agent_framework.azure import AzureOpenAIChatClient
        
        client = AzureOpenAIChatClient(
            deployment_name=settings.azure_openai_deployment_name,
            api_key=settings.azure_openai_api_key,
            endpoint=settings.azure_openai_endpoint,
            api_version=settings.azure_openai_api_version,
        )
        logger.info(f"✓ AzureOpenAIChatClient inicializado (deployment: {settings.azure_openai_deployment_name})")
        return client
        
    else:
        raise ValueError(
            f"Proveedor LLM no reconocido: {provider}. "
            "Usa 'azure' o 'openai'"
        )
