from sqlalchemy import Column, Integer, String, Float, Boolean, Text, JSON, DateTime, Index
from sqlalchemy.sql import func
from database.database import Base

class Participante(Base):
    __tablename__ = "participantes"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    edad = Column(Integer)
    universidad = Column(String(255))
    semestre = Column(Integer)
    habilidades = Column(JSON, default={})
    competencias_participadas = Column(Integer, default=0)
    problemas_resueltos_total = Column(Integer, default=0)
    tasa_exito_historica = Column(Float, default=0.5)
    ranking_promedio = Column(Float)
    tipos_problema_preferidos = Column(JSON, default=[])
    tipos_problema_evitar = Column(JSON, default=[])
    tiempo_maximo_disponible = Column(Integer, default=180)  # 🔧 CAMBIADO: 3 horas máximo para competencias
    nivel_energia = Column(Float, default=0.8)
    nivel_concentracion = Column(Float, default=0.8)
    disponibilidad = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.current_timestamp())
    updated_at = Column(DateTime(timezone=True), onupdate=func.current_timestamp())
    
    def __repr__(self):
        return f"<Participante(id={self.id}, nombre='{self.nombre}')>"

class Problema(Base):
    __tablename__ = "problemas"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(255), nullable=False)
    descripcion = Column(Text)
    tipo = Column(String(100), nullable=False)
    nivel_dificultad = Column(String(50), nullable=False)
    puntos_base = Column(Integer, nullable=False, default=100)
    multiplicador_dificultad = Column(Float, default=1.0)
    bonus_tiempo = Column(Integer, default=50)
    habilidades_requeridas = Column(JSON, default={})
    tiempo_limite = Column(Integer, default=75)  
    memoria_limite = Column(Integer, default=256)
    fuente = Column(String(255))
    año_competencia = Column(Integer)
    tasa_resolucion_historica = Column(Float, default=0.5)
    url_problema = Column(String(500))
    tags = Column(JSON, default=[])
    problemas_prerequisito = Column(JSON, default=[])
    problemas_relacionados = Column(JSON, default=[])
    created_at = Column(DateTime(timezone=True), server_default=func.current_timestamp())
    updated_at = Column(DateTime(timezone=True), onupdate=func.current_timestamp())
    
    def __repr__(self):
        return f"<Problema(id={self.id}, nombre='{self.nombre}', tipo='{self.tipo}')>"

class Asignacion(Base):
    __tablename__ = "asignaciones"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, index=True, nullable=False)
    nombre_asignacion = Column(String(255))
    descripcion = Column(Text)
    problemas_ids = Column(JSON, nullable=False)
    participantes_ids = Column(JSON, nullable=False)
    configuracion_optimizacion = Column(JSON, default={})
    matriz_asignacion = Column(JSON, nullable=False)
    fitness_final = Column(Float, nullable=False)
    fitness_componentes = Column(JSON, default={})
    parametros_algoritmo = Column(JSON, default={})
    generaciones_ejecutadas = Column(Integer)
    tiempo_ejecucion_segundos = Column(Float)
    problemas_asignados = Column(Integer)
    participantes_utilizados = Column(Integer)
    es_solucion_valida = Column(Boolean, default=False)
    violaciones_restricciones = Column(JSON, default=[])
    asignaciones_detalle = Column(JSON, default=[])
    evolucion_algoritmo = Column(JSON, default={})
    puntuacion_total_esperada = Column(Float)
    tiempo_total_estimado = Column(Float)
    compatibilidad_promedio = Column(Float)
    eficiencia_predicha = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.current_timestamp())
    updated_at = Column(DateTime(timezone=True), onupdate=func.current_timestamp())
    
    def __repr__(self):
        return f"<Asignacion(id={self.id}, uuid='{self.uuid}', fitness={self.fitness_final:.3f})>"

Index('idx_participante_email', Participante.email)
Index('idx_participante_disponibilidad', Participante.disponibilidad)
Index('idx_participante_universidad', Participante.universidad)
Index('idx_participante_tasa_exito', Participante.tasa_exito_historica)

Index('idx_problema_tipo', Problema.tipo)
Index('idx_problema_dificultad', Problema.nivel_dificultad)
Index('idx_problema_fuente', Problema.fuente)
Index('idx_problema_puntos', Problema.puntos_base)

Index('idx_asignacion_uuid', Asignacion.uuid)
Index('idx_asignacion_fitness', Asignacion.fitness_final)
Index('idx_asignacion_valida', Asignacion.es_solucion_valida)
Index('idx_asignacion_fecha', Asignacion.created_at)
Index('idx_asignacion_puntuacion', Asignacion.puntuacion_total_esperada)