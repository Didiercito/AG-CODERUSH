try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseModel as BaseSettings

from dotenv import load_dotenv
from typing import Optional
from pydantic import ConfigDict

# Cargar variables de entorno
load_dotenv()

class Settings(BaseSettings):
    # Configuración de la aplicación
    app_name: str = "CODERUSH"
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Configuración del algoritmo
    default_algorithm: str = "greedy"
    population_size: int = 50
    max_generations: int = 100
    
    # Configuración de Base de Datos PostgreSQL
    db_host: str = "127.0.0.1"
    db_port: int = 5432
    db_user: str = "postgres"
    db_password: str = "password"
    db_name: str = "coderush_db"
    db_echo: bool = True
    
    # Configuración del algoritmo genético
    poblacion_size_default: int = 100
    generaciones_max_default: int = 200
    prob_cruce_default: float = 0.8
    prob_mutacion_default: float = 0.15
    elitismo_porcentaje_default: float = 0.1
    
    # Configuración de optimización
    peso_puntuacion_default: float = 0.4
    peso_compatibilidad_default: float = 0.25
    peso_balance_carga_default: float = 0.2
    peso_probabilidad_exito_default: float = 0.15
    
    # Configuración de competencia
    duracion_competencia_default: int = 300
    max_participantes_default: int = 10
    
    # Configuración de cache
    cache_evaluaciones: bool = True
    max_cache_size: int = 1000
    
    # Configuración de logging
    log_level: str = "INFO"
    log_file: Optional[str] = None
    
    # Configuración para Pydantic v2
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra='ignore'
    )
    
    @property
    def database_url(self) -> str:
        """Construir URL de base de datos desde componentes individuales"""
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
    
    @property
    def database_url_sync(self) -> str:
        """URL síncrona para SQLAlchemy"""
        return self.database_url
    
    @property
    def database_url_async(self) -> str:
        """URL asíncrona para uso futuro"""
        return self.database_url.replace("postgresql://", "postgresql+asyncpg://")

# Crear instancia de settings
settings = Settings()