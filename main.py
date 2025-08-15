from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime

from api.routes import asignaciones  

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manejo del ciclo de vida de la aplicación"""
    print("🚀 Iniciando CODERUSH - Sistema de Optimización Genética")
    print("📊 Modo: CSV - Sin base de datos")
    print("💡 Carga datos desde CSV en el frontend")
    print(f"🌐 Servidor disponible en: http://localhost:8000")
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
# RUTAS PRINCIPALES
# ============================================================================

# ✅ SOLO la ruta del algoritmo genético (que usa CSV)
app.include_router(asignaciones.router, prefix="/api", tags=["algoritmo-genetico"])

# ============================================================================
# ENDPOINTS BÁSICOS
# ============================================================================

@app.get("/api/health")
async def health_check():
    """Health check del sistema"""
    return {
        'status': 'healthy',
        'timestamp': datetime.now(),
        'mode': 'CSV_ONLY',
        'version': '2.0.0',
        'components': {
            'api': 'running',
            'algorithm': 'ready'
        }
    }

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0", 
        port=8000,
        reload=True,
        log_level="info"
    )