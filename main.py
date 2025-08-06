from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime

# Rutas modulares
from api.routes import participantes, problemas, asignaciones, sistema

from config import settings
from database import init_database, check_database_connection

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manejo del ciclo de vida de la aplicación"""
    print("🚀 Iniciando CODERUSH - Sistema de Optimización Genética")
    
    # Inicializar base de datos
    try:
        await init_database()
        print("✅ Base de datos inicializada correctamente")
    except Exception as e:
        print(f"❌ Error inicializando base de datos: {e}")
    
    # ✅ ELIMINADO: No genera datos automáticamente
    # Los datos se cargan solo mediante CSV o endpoint manual
    print("📊 Base de datos lista - sin datos precargados")
    print("💡 Usa /api/generar-datos-ejemplo o carga CSV para empezar")
    
    print(f"🌐 Servidor disponible en: http://localhost:{settings.port}")
    print("📖 Documentación: /docs")
    
    yield
    print("👋 Cerrando CODERUSH...")

app = FastAPI(
    title="CODERUSH",
    description="Sistema avanzado de optimización con algoritmo genético para competencias de programación",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# RUTAS MODULARES
# ============================================================================

app.include_router(participantes.router, prefix="/api", tags=["participantes"])
app.include_router(problemas.router, prefix="/api", tags=["problemas"])
app.include_router(asignaciones.router, prefix="/api", tags=["asignaciones", "algoritmo-genetico"])
app.include_router(sistema.router, prefix="/api", tags=["sistema"])

# ============================================================================
# ENDPOINTS PRINCIPALES
# ============================================================================

@app.get("/")
async def root():
    """Información del sistema"""
    return {
        'sistema': 'CODERUSH',
        'version': '2.0.0',
        'descripcion': 'Sistema de optimización con algoritmo genético para competencias de programación',
        'endpoints_principales': [
            '/api/asignar - Algoritmo genético para asignación de equipo',
            '/api/participantes - Gestión de participantes',
            '/api/problemas - Gestión de problemas',
            '/api/asignaciones - Gestión de asignaciones',
            '/api/generar-datos-ejemplo - Generar datos de prueba (MANUAL)',
            '/docs - Documentación API'
        ],
        'rutas_activas': ['participantes', 'problemas', 'asignaciones', 'sistema'],
        'base_datos': 'PostgreSQL',
        'datos_precargados': False,  # ✅ INDICADOR DE QUE NO HAY DATOS AUTOMÁTICOS
        'instrucciones': 'Usa /api/generar-datos-ejemplo o carga CSV para empezar'
    }

@app.get("/api/health")
async def health_check():
    """Health check del sistema"""
    db_status = check_database_connection()
    
    return {
        'status': 'healthy' if db_status else 'degraded',
        'timestamp': datetime.now(),
        'database': 'connected' if db_status else 'disconnected',
        'version': '2.0.0',
        'components': {
            'api': 'running',
            'algorithm': 'ready',
            'database': 'connected' if db_status else 'error'
        },
        'datos_precargados': False  # ✅ CONFIRMACIÓN
    }

@app.get("/api/info")
async def system_info():
    """Información detallada del sistema"""
    return {
        'sistema': 'CODERUSH',
        'version': '2.0.0',
        'algoritmo': 'Genético Avanzado',
        'configuracion': {
            'poblacion_default': getattr(settings, 'population_size', 100),
            'generaciones_default': getattr(settings, 'max_generations', 200),
            'debug': getattr(settings, 'debug', False),
            'datos_automaticos': False  # ✅ DESHABILITADO
        },
        'base_datos': {
            'tipo': 'PostgreSQL',
            'host': getattr(settings, 'db_host', 'localhost'),
            'puerto': getattr(settings, 'db_port', 5432)
        },
        'endpoints': {
            'algoritmo_genetico': 'POST /api/asignar',
            'participantes': 'GET,POST,PUT,DELETE /api/participantes',
            'problemas': 'GET,POST,PUT,DELETE /api/problemas',
            'asignaciones': 'GET,DELETE /api/asignaciones',
            'sistema': 'POST /api/generar-datos-ejemplo, DELETE /api/limpiar-datos'
        },
        'modo_operacion': 'CSV_MANUAL',  # ✅ MODO MANUAL
        'instrucciones': [
            'Base de datos iniciada sin datos precargados',
            'Usa POST /api/generar-datos-ejemplo para datos de prueba',
            'O carga datos desde CSV en el frontend'
        ]
    }

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=getattr(settings, 'host', '0.0.0.0'), 
        port=getattr(settings, 'port', 8000),
        reload=getattr(settings, 'debug', False),
        log_level="info"
    )