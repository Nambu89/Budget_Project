"""
Módulo de infraestructura - LLM y PDF.
"""

from .llm import (
    AzureOpenAIClient,
    OpenAIClient,
    LLMFactory,
    get_llm_client,
)
from .pdf import PDFGenerator, generar_pdf_presupuesto

__all__ = [
    # LLM
    "AzureOpenAIClient",
    "OpenAIClient",
    "LLMFactory",
    "get_llm_client",
    # PDF
    "PDFGenerator",
    "generar_pdf_presupuesto",
]