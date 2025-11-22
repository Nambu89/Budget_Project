"""
Módulo de agentes CrewAI.
"""

from .data_collector_agent import DataCollectorAgent
from .calculator_agent import CalculatorAgent
from .document_agent import DocumentAgent

__all__ = [
    "DataCollectorAgent",
    "CalculatorAgent",
    "DocumentAgent",
]