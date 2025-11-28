"""Script para inicializar base de datos limpia"""

import sys
from pathlib import Path

root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

from src.infrastructure.database import init_db

print("🔄 Inicializando base de datos limpia...")
init_db()
print("✅ Base de datos creada: data/budget.db")
print("\n💡 Ahora puedes registrar usuarios desde Streamlit")
