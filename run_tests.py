#!/usr/bin/env python
"""
Script para ejecutar todos los tests.

Uso:
    python run_tests.py              # Ejecutar todos los tests
    python run_tests.py --unit       # Solo tests unitarios
    python run_tests.py --integration # Solo tests de integración
    python run_tests.py --llm        # Solo tests de conexión LLM
    python run_tests.py --coverage   # Con reporte de cobertura
"""

import sys
import os
import argparse
from pathlib import Path

# Añadir directorio raíz al path
ROOT_DIR = Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR))


def main():
    parser = argparse.ArgumentParser(description="Ejecutar tests del Budget Calculator")
    
    parser.add_argument("--unit", action="store_true", help="Solo tests unitarios")
    parser.add_argument("--integration", action="store_true", help="Solo tests de integración")
    parser.add_argument("--llm", action="store_true", help="Solo tests de conexión LLM")
    parser.add_argument("--agents", action="store_true", help="Solo tests de agentes")
    parser.add_argument("--pdf", action="store_true", help="Solo tests de PDF")
    parser.add_argument("--coverage", action="store_true", help="Generar reporte de cobertura")
    parser.add_argument("-v", "--verbose", action="store_true", help="Modo verbose")
    parser.add_argument("-s", "--stdout", action="store_true", help="Mostrar prints")
    
    args = parser.parse_args()
    
    # Importar pytest aquí para evitar errores si no está instalado
    try:
        import pytest
    except ImportError:
        print("❌ pytest no está instalado. Ejecuta: pip install pytest pytest-cov")
        sys.exit(1)
    
    # Construir argumentos de pytest
    pytest_args = []
    
    # Determinar qué tests ejecutar
    if args.unit:
        pytest_args.append("tests/unit/")
        print("🧪 Ejecutando tests unitarios...")
    elif args.integration:
        pytest_args.append("tests/integration/")
        print("🧪 Ejecutando tests de integración...")
    elif args.llm:
        pytest_args.append("tests/integration/test_llm_connection.py")
        print("🧪 Ejecutando tests de conexión LLM...")
    elif args.agents:
        pytest_args.append("tests/integration/test_agents_communication.py")
        print("🧪 Ejecutando tests de agentes...")
    elif args.pdf:
        pytest_args.append("tests/unit/test_pdf.py")
        print("🧪 Ejecutando tests de PDF...")
    else:
        pytest_args.append("tests/")
        print("🧪 Ejecutando todos los tests...")
    
    # Opciones adicionales
    if args.verbose:
        pytest_args.append("-v")
    
    if args.stdout:
        pytest_args.append("-s")
    
    if args.coverage:
        pytest_args.extend([
            "--cov=src",
            "--cov-report=term-missing",
            "--cov-report=html:coverage_report",
        ])
        print("📊 Generando reporte de cobertura...")
    
    # Mostrar configuración
    print(f"\n📋 Configuración detectada:")
    
    # Verificar variables de entorno
    azure_key = os.getenv("AZURE_OPENAI_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    
    if azure_key:
        print(f"   ✅ Azure OpenAI configurado")
    else:
        print(f"   ⚠️ Azure OpenAI NO configurado (algunos tests se saltarán)")
    
    if openai_key:
        print(f"   ✅ OpenAI configurado")
    else:
        print(f"   ⚠️ OpenAI NO configurado")
    
    print(f"\n{'=' * 60}")
    
    # Ejecutar pytest
    exit_code = pytest.main(pytest_args)
    
    print(f"\n{'=' * 60}")
    
    if exit_code == 0:
        print("✅ Todos los tests pasaron!")
    else:
        print(f"❌ Algunos tests fallaron (código: {exit_code})")
    
    if args.coverage:
        print("\n📊 Reporte de cobertura generado en: coverage_report/index.html")
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()