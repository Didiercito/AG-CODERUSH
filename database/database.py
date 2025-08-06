import psycopg2
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float, Boolean, DateTime, Text, JSON, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
from config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base = declarative_base()

def get_engine():
    database_url = settings.database_url
    
    engine = create_engine(
        database_url,
        echo=settings.db_echo,
        connect_args={
            "client_encoding": "utf8",
            "options": "-c client_encoding=utf8"
        },
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
        pool_recycle=300
    )
    
    return engine

def check_database_connection():
    try:
        connection = psycopg2.connect(
            host=settings.db_host,
            port=settings.db_port,
            user=settings.db_user,
            password=settings.db_password,
            database=settings.db_name,
            client_encoding='utf8'
        )
        
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        cursor.close()
        connection.close()
        
        engine = get_engine()
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            
        logger.info("✅ Conexión a PostgreSQL exitosa")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error conectando a PostgreSQL: {e}")
        return False

async def init_database():
    logger.info("🚀 Inicializando base de datos...")
    
    try:
        if not check_database_connection():
            raise Exception("No se pudo conectar a PostgreSQL")
        
        engine = get_engine()
        metadata = MetaData()
        
        participantes_table = Table(
            'participantes', metadata,
            Column('id', Integer, primary_key=True),
            Column('nombre', String(255), nullable=False),
            Column('email', String(255), unique=True, index=True, nullable=False),
            Column('edad', Integer),
            Column('universidad', String(255)),
            Column('semestre', Integer),
            Column('habilidades', JSON, default={}),
            Column('competencias_participadas', Integer, default=0),
            Column('problemas_resueltos_total', Integer, default=0),
            Column('tasa_exito_historica', Float, default=0.5),
            Column('ranking_promedio', Float),
            Column('tipos_problema_preferidos', JSON, default=[]),
            Column('tipos_problema_evitar', JSON, default=[]),
            Column('tiempo_maximo_disponible', Integer, default=300),
            Column('nivel_energia', Float, default=0.8),
            Column('nivel_concentracion', Float, default=0.8),
            Column('disponibilidad', Boolean, default=True),
            Column('created_at', DateTime(timezone=True), server_default=func.current_timestamp()),
            Column('updated_at', DateTime(timezone=True), onupdate=func.current_timestamp())
        )
        
        problemas_table = Table(
            'problemas', metadata,
            Column('id', Integer, primary_key=True),
            Column('nombre', String(255), nullable=False),
            Column('descripcion', Text),
            Column('tipo', String(100), nullable=False),
            Column('nivel_dificultad', String(50), nullable=False),
            Column('puntos_base', Integer, nullable=False, default=100),
            Column('multiplicador_dificultad', Float, default=1.0),
            Column('bonus_tiempo', Integer, default=50),
            Column('habilidades_requeridas', JSON, default={}),
            Column('tiempo_limite', Integer, default=180),
            Column('memoria_limite', Integer, default=256),
            Column('fuente', String(255)),
            Column('año_competencia', Integer),
            Column('tasa_resolucion_historica', Float, default=0.5),
            Column('url_problema', String(500)),
            Column('tags', JSON, default=[]),
            Column('problemas_prerequisito', JSON, default=[]),
            Column('problemas_relacionados', JSON, default=[]),
            Column('created_at', DateTime(timezone=True), server_default=func.current_timestamp()),
            Column('updated_at', DateTime(timezone=True), onupdate=func.current_timestamp())
        )
        
        asignaciones_table = Table(
            'asignaciones', metadata,
            Column('id', Integer, primary_key=True),
            Column('uuid', String(36), unique=True, index=True, nullable=False),
            Column('nombre_asignacion', String(255)),
            Column('descripcion', Text),
            Column('problemas_ids', JSON, nullable=False),
            Column('participantes_ids', JSON, nullable=False),
            Column('configuracion_optimizacion', JSON, default={}),
            Column('matriz_asignacion', JSON, nullable=False),
            Column('fitness_final', Float, nullable=False),
            Column('fitness_componentes', JSON, default={}),
            Column('parametros_algoritmo', JSON, default={}),
            Column('generaciones_ejecutadas', Integer),
            Column('tiempo_ejecucion_segundos', Float),
            Column('problemas_asignados', Integer),
            Column('participantes_utilizados', Integer),
            Column('es_solucion_valida', Boolean, default=False),
            Column('violaciones_restricciones', JSON, default=[]),
            Column('asignaciones_detalle', JSON, default=[]),
            Column('evolucion_algoritmo', JSON, default={}),
            Column('puntuacion_total_esperada', Float),
            Column('tiempo_total_estimado', Float),
            Column('compatibilidad_promedio', Float),
            Column('eficiencia_predicha', Float),
            Column('created_at', DateTime(timezone=True), server_default=func.current_timestamp()),
            Column('updated_at', DateTime(timezone=True), onupdate=func.current_timestamp())
        )
        
        metadata.create_all(engine)
        logger.info("✅ Tablas creadas/verificadas exitosamente")
        
        with engine.connect() as connection:
            result = connection.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            tables = [row[0] for row in result.fetchall()]
            logger.info(f"📋 Tablas disponibles: {tables}")
        
        # ✅ ELIMINADO: No genera datos automáticamente
        # Solo crea las tablas y está listo para recibir datos via CSV o endpoint manual
        logger.info("📊 Base de datos lista sin datos precargados")
        logger.info("💡 Usa /api/generar-datos-ejemplo o carga CSV para empezar")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error inicializando base de datos: {e}")
        raise e

def get_db_session():
    engine = get_engine()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()

def execute_query(query: str, params: dict = None):
    try:
        engine = get_engine()
        with engine.connect() as connection:
            if params:
                result = connection.execute(text(query), params)
            else:
                result = connection.execute(text(query))
            return result.fetchall()
    except Exception as e:
        logger.error(f"Error ejecutando consulta: {e}")
        return None