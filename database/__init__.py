# database/__init__.py

from .database import (
    init_database,
    check_database_connection,
    get_engine,
    get_db_session,
    execute_query
)

# Funciones CRUD (crear si no existen)
try:
    from .crud import crud_participante, crud_problema, crud_asignacion
except ImportError:
    crud_participante = None
    crud_problema = None
    crud_asignacion = None

try:
    from .dashboard import get_dashboard_stats
except ImportError:
    get_dashboard_stats = None

# Función para obtener sesión de DB - alias para compatibilidad
def get_db():
    """Alias para get_db_session para compatibilidad"""
    return get_db_session()

__all__ = [
    'init_database',
    'check_database_connection', 
    'get_engine',
    'get_db_session',
    'get_db',
    'execute_query',
    'crud_participante',
    'crud_problema', 
    'crud_asignacion',
    'get_dashboard_stats'
]