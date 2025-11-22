"""
Tests de conexión con Azure AI Foundry / OpenAI.

Verifica que la conexión con el LLM esté funcionando
correctamente y que las respuestas sean válidas.
"""

import pytest
import os
import sys
from pathlib import Path

# Añadir el directorio raíz al path
ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.config.settings import settings
from src.infrastructure.llm import (
    AzureOpenAIClient,
    OpenAIClient,
    LLMFactory,
    get_llm_client,
)


class TestAzureConnection:
    """Tests de conexión con Azure OpenAI."""
    
    @pytest.mark.skipif(
        not os.getenv("AZURE_OPENAI_API_KEY"),
        reason="AZURE_OPENAI_API_KEY no configurada"
    )
    def test_azure_client_initialization(self):
        """Test: El cliente Azure se inicializa correctamente."""
        client = AzureOpenAIClient()
        
        assert client is not None
        assert client.client is not None
        assert client.deployment is not None
        print(f"✅ Cliente Azure inicializado: deployment={client.deployment}")
    
    @pytest.mark.skipif(
        not os.getenv("AZURE_OPENAI_API_KEY"),
        reason="AZURE_OPENAI_API_KEY no configurada"
    )
    def test_azure_simple_completion(self):
        """Test: Azure responde a un prompt simple."""
        client = AzureOpenAIClient()
        
        response = client.simple_completion(
            prompt="Responde solo con la palabra 'OK'",
            temperature=0,
            max_tokens=10,
        )
        
        assert response is not None
        assert len(response) > 0
        print(f"✅ Respuesta Azure: {response}")
    
    @pytest.mark.skipif(
        not os.getenv("AZURE_OPENAI_API_KEY"),
        reason="AZURE_OPENAI_API_KEY no configurada"
    )
    def test_azure_chat_completion(self):
        """Test: Azure responde a una conversación."""
        client = AzureOpenAIClient()
        
        messages = [
            {"role": "system", "content": "Eres un asistente útil."},
            {"role": "user", "content": "¿Cuánto es 2+2? Responde solo el número."},
        ]
        
        response = client.chat_completion(
            messages=messages,
            temperature=0,
            max_tokens=10,
        )
        
        assert response is not None
        assert "4" in response
        print(f"✅ Chat completion Azure: {response}")
    
    @pytest.mark.skipif(
        not os.getenv("AZURE_OPENAI_API_KEY"),
        reason="AZURE_OPENAI_API_KEY no configurada"
    )
    def test_azure_is_available(self):
        """Test: Verificar disponibilidad del servicio Azure."""
        client = AzureOpenAIClient()
        
        available = client.is_available()
        
        assert available is True
        print("✅ Servicio Azure disponible")


class TestOpenAIConnection:
    """Tests de conexión con OpenAI directo."""
    
    @pytest.mark.skipif(
        not os.getenv("OPENAI_API_KEY"),
        reason="OPENAI_API_KEY no configurada"
    )
    def test_openai_client_initialization(self):
        """Test: El cliente OpenAI se inicializa correctamente."""
        client = OpenAIClient()
        
        assert client is not None
        assert client.client is not None
        assert client.model is not None
        print(f"✅ Cliente OpenAI inicializado: model={client.model}")
    
    @pytest.mark.skipif(
        not os.getenv("OPENAI_API_KEY"),
        reason="OPENAI_API_KEY no configurada"
    )
    def test_openai_simple_completion(self):
        """Test: OpenAI responde a un prompt simple."""
        client = OpenAIClient()
        
        response = client.simple_completion(
            prompt="Responde solo con la palabra 'OK'",
            temperature=0,
            max_tokens=10,
        )
        
        assert response is not None
        assert len(response) > 0
        print(f"✅ Respuesta OpenAI: {response}")


class TestLLMFactory:
    """Tests del factory de LLM."""
    
    def test_factory_get_provider_info(self):
        """Test: Factory retorna información del proveedor."""
        info = LLMFactory.get_provider_info()
        
        assert "provider" in info
        assert "azure_configured" in info
        # Verificar que al menos uno está en el dict (compatibilidad)
        assert "azure_configured" in info or "openai_configured" in info
        print(f"✅ Provider info: {info}")
    
    @pytest.mark.skipif(
        not (os.getenv("AZURE_OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")),
        reason="Ningún LLM configurado"
    )
    def test_factory_creates_client(self):
        """Test: Factory crea el cliente correcto."""
        # Reset singleton
        LLMFactory.reset()
        
        client = LLMFactory.create()
        
        assert client is not None
        print(f"✅ Factory creó cliente: {type(client).__name__}")
    
    @pytest.mark.skipif(
        not (os.getenv("AZURE_OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")),
        reason="Ningún LLM configurado"
    )
    def test_factory_singleton(self):
        """Test: Factory retorna la misma instancia (singleton)."""
        LLMFactory.reset()
        
        client1 = LLMFactory.create()
        client2 = LLMFactory.create()
        
        assert client1 is client2
        print("✅ Factory singleton funciona correctamente")
    
    @pytest.mark.skipif(
        not (os.getenv("AZURE_OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")),
        reason="Ningún LLM configurado"
    )
    def test_get_llm_client_convenience(self):
        """Test: Función de conveniencia get_llm_client."""
        LLMFactory.reset()
        
        client = get_llm_client()
        
        assert client is not None
        print(f"✅ get_llm_client retorna: {type(client).__name__}")


class TestConnectionIntegration:
    """Tests de integración de conexión."""
    
    @pytest.mark.skipif(
        not (os.getenv("AZURE_OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")),
        reason="Ningún LLM configurado"
    )
    def test_llm_responds_about_construction(self):
        """Test: LLM responde preguntas sobre construcción."""
        client = get_llm_client()
        
        response = client.simple_completion(
            prompt="¿Cuál es el precio aproximado por m2 de alicatar un baño en España? Responde brevemente.",
            system_prompt="Eres un experto en reformas en España.",
            temperature=0.3,
            max_tokens=100,
        )
        
        assert response is not None
        assert len(response) > 20
        # Debería mencionar euros o €
        assert "€" in response or "euro" in response.lower() or "eur" in response.lower()
        print(f"✅ LLM responde sobre construcción:\n{response[:200]}...")
    
    @pytest.mark.skipif(
        not (os.getenv("AZURE_OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")),
        reason="Ningún LLM configurado"
    )
    def test_llm_structured_response(self):
        """Test: LLM puede generar respuestas estructuradas."""
        client = get_llm_client()
        
        response = client.simple_completion(
            prompt="""
            Genera un JSON con la siguiente estructura para un presupuesto de baño:
            {"partidas": [{"nombre": "...", "precio": 0}], "total": 0}
            
            Incluye 3 partidas básicas. Solo responde con el JSON, nada más.
            """,
            temperature=0,
            max_tokens=200,
        )
        
        assert response is not None
        assert "{" in response and "}" in response
        print(f"✅ LLM genera respuesta estructurada:\n{response}")


# ============================================
# Ejecutar tests directamente
# ============================================

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 Tests de Conexión LLM")
    print("=" * 60)
    
    # Verificar configuración
    print(f"\n📋 Configuración detectada:")
    print(f"   LLM Provider: {settings.llm_provider}")
    print(f"   Azure configurado: {settings.is_azure_configured()}")
    print(f"   OpenAI configurado: {settings.is_openai_configured()}")
    
    # Ejecutar pytest
    pytest.main([__file__, "-v", "-s"])