"""
Configuración centralizada de la aplicación usando Pydantic Settings.

Este módulo gestiona todas las variables de entorno y configuración
del sistema de manera type-safe con validación automática.
"""

from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from functools import lru_cache


class Settings(BaseSettings):
    """
    Configuración principal de la aplicación.
    
    Lee automáticamente las variables del archivo .env
    y proporciona valores por defecto seguros.
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    # ==========================================
    # Proveedor LLM
    # ==========================================
    llm_provider: Literal["azure", "openai"] = Field(
        default="azure",
        description="Proveedor de LLM a utilizar"
    )
    
    # ==========================================
    # Azure OpenAI
    # ==========================================
    azure_openai_endpoint: str = Field(
        default="",
        description="Endpoint de Azure OpenAI"
    )
    azure_openai_api_key: str = Field(
        default="",
        description="API Key de Azure OpenAI"
    )
    azure_openai_api_version: str = Field(
        default="2024-02-15-preview",
        description="Versión de la API de Azure OpenAI"
    )
    azure_openai_deployment_name: str = Field(
        default="gpt-4o-mini",
        description="Nombre del deployment en Azure"
    )
    
    # ==========================================
    # OpenAI Directo
    # ==========================================
    openai_api_key: str = Field(
        default="",
        description="API Key de OpenAI"
    )
    openai_model: str = Field(
        default="gpt-4o-mini",
        description="Modelo de OpenAI a usar"
    )
    
    # ==========================================
    # Configuración de la aplicación
    # ==========================================
    environment: Literal["development", "staging", "production"] = Field(
        default="development",
        description="Entorno de ejecución"
    )
    debug: bool = Field(
        default=True,
        description="Modo debug activado"
    )
    
    # ==========================================
    # Configuración de negocio
    # ==========================================
    iva_general: int = Field(
        default=21,
        description="IVA general (%)",
        ge=0,
        le=100
    )
    iva_reducido: int = Field(
        default=10,
        description="IVA reducido para vivienda habitual (%)",
        ge=0,
        le=100
    )
    markup_partidas_individuales: int = Field(
        default=15,
        description="Markup para partidas individuales vs paquetes (%)",
        ge=0,
        le=100
    )
    redondeo_alza: int = Field(
        default=5,
        description="Redondeo al alza sobre el total (%)",
        ge=0,
        le=100
    )
    validez_presupuesto_dias: int = Field(
        default=30,
        description="Días de validez del presupuesto",
        ge=1
    )
    
    # ==========================================
    # Configuración PDF
    # ==========================================
    logos_path: str = Field(
        default="./assets/logos/",
        description="Ruta para logos de clientes"
    )
    empresa_nombre: str = Field(
        default="Easy Obras",
        description="Nombre de la empresa"
    )
    empresa_telefono: str = Field(
        default="+34 900 000 000",
        description="Teléfono de la empresa"
    )
    empresa_email: str = Field(
        default="info@easyobras.es",
        description="Email de la empresa"
    )
    empresa_web: str = Field(
        default="www.easyobras.es",
        description="Web de la empresa"
    )
    
    # ==========================================
    # Métodos de validación
    # ==========================================
    def is_azure_configured(self) -> bool:
        """Verifica si Azure OpenAI está correctamente configurado."""
        return bool(
            self.azure_openai_endpoint and 
            self.azure_openai_api_key and
            self.azure_openai_deployment_name
        )
    
    def is_openai_configured(self) -> bool:
        """Verifica si OpenAI directo está correctamente configurado."""
        return bool(self.openai_api_key)
    
    def get_active_llm_config(self) -> dict:
        """
        Retorna la configuración del LLM activo.
        
        Returns:
            dict: Configuración del proveedor LLM seleccionado
        """
        if self.llm_provider == "azure":
            return {
                "provider": "azure",
                "endpoint": self.azure_openai_endpoint,
                "api_key": self.azure_openai_api_key,
                "api_version": self.azure_openai_api_version,
                "deployment": self.azure_openai_deployment_name,
            }
        else:
            return {
                "provider": "openai",
                "api_key": self.openai_api_key,
                "model": self.openai_model,
            }


@lru_cache()
def get_settings() -> Settings:
    """
    Obtiene la instancia de configuración (singleton cacheado).
    
    Returns:
        Settings: Instancia única de configuración
    """
    return Settings()


# Instancia global para importación directa
settings = get_settings()