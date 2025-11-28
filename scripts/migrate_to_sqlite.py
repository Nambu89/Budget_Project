"""
Script de migración de usuarios de JSON a SQLite.

Migra todos los usuarios existentes en data/users.json a la base de datos SQLite.
"""

import json
from pathlib import Path
from datetime import datetime
import sys
import os

# Añadir directorio raíz al path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))
os.chdir(root_dir)

from src.infrastructure.database import init_db, get_db_session
from src.infrastructure.database.models import User as UserModel


def migrate_users_from_json():
    """
    Migra usuarios de JSON a SQLite.
    
    1. Crea las tablas si no existen
    2. Lee usuarios de data/users.json
    3. Inserta en SQLite
    4. Crea backup del JSON
    """
    print("=" * 60)
    print("🔄 Migración de Usuarios: JSON → SQLite")
    print("=" * 60)
    
    # 1. Crear tablas
    print("\n1. Creando tablas en SQLite...")
    init_db()
    print("   ✓ Tablas creadas")
    
    # 2. Verificar si existe JSON
    json_path = Path("data/users.json")
    if not json_path.exists():
        print("\n⚠️  No se encontró data/users.json")
        print("   No hay usuarios para migrar")
        return
    
    # 3. Leer JSON
    print(f"\n2. Leyendo usuarios de {json_path}...")
    with open(json_path, 'r', encoding='utf-8') as f:
        users_json = json.load(f)
    
    print(f"   ✓ {len(users_json)} usuarios encontrados")
    
    # 4. Migrar a SQLite
    print("\n3. Migrando a SQLite...")
    migrated = 0
    skipped = 0
    
    with get_db_session() as session:
        for email, user_data in users_json.items():
            try:
                # Verificar si ya existe
                existing = session.query(UserModel).filter_by(
                    email=email.lower()
                ).first()
                
                if existing:
                    print(f"   ⊘ Saltado (ya existe): {email}")
                    skipped += 1
                    continue
                
                # Convertir fechas si son strings
                if isinstance(user_data.get('fecha_registro'), str):
                    user_data['fecha_registro'] = datetime.fromisoformat(
                        user_data['fecha_registro']
                    )
                
                if user_data.get('ultimo_acceso') and isinstance(user_data['ultimo_acceso'], str):
                    user_data['ultimo_acceso'] = datetime.fromisoformat(
                        user_data['ultimo_acceso']
                    )
                
                # Crear usuario
                user = UserModel(**user_data)
                session.add(user)
                
                print(f"   ✓ Migrado: {email}")
                migrated += 1
                
            except Exception as e:
                print(f"   ✗ Error con {email}: {e}")
                continue
        
        session.commit()
    
    # 5. Crear backup
    print("\n4. Creando backup del JSON...")
    backup_path = json_path.with_suffix('.json.backup')
    
    # Si ya existe backup, añadir timestamp
    if backup_path.exists():
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = json_path.parent / f"users_{timestamp}.json.backup"
    
    json_path.rename(backup_path)
    print(f"   ✓ Backup creado: {backup_path}")
    
    # 6. Resumen
    print("\n" + "=" * 60)
    print("✅ Migración Completada")
    print("=" * 60)
    print(f"   Migrados: {migrated}")
    print(f"   Saltados: {skipped}")
    print(f"   Total:    {len(users_json)}")
    print(f"\n   Base de datos: data/budget.db")
    print(f"   Backup JSON:   {backup_path}")
    print("=" * 60)


def verify_migration():
    """Verifica que la migración fue correcta."""
    print("\n🔍 Verificando migración...")
    
    with get_db_session() as session:
        users = session.query(UserModel).all()
        print(f"   ✓ {len(users)} usuarios en SQLite")
        
        if users:
            print("\n   Primeros 3 usuarios:")
            for user in users[:3]:
                print(f"   - {user.email} ({user.nombre})")


if __name__ == "__main__":
    try:
        migrate_users_from_json()
        verify_migration()
        
        print("\n✅ ¡Migración completada!")
        print("\n💡 Ahora puedes:")
        print("   1. Reiniciar la API: python run_api.py")
        print("   2. Reiniciar Streamlit: streamlit run main.py")
        print("   3. Los usuarios ahora están en SQLite")
        
    except Exception as e:
        print(f"\n❌ Error en migración: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
