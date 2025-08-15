from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any

class ConfiguracionCompetencia(BaseModel):
    """Configuración básica de la competencia - SOLO esto desde frontend"""
    nombre: str = Field(description="Nombre descriptivo de la competencia.")
    tiempo_total_minutos: int = Field(default=300, gt=0, description="Duración total de la competencia en minutos.")
    tamanio_equipo: int = Field(default=3, gt=0, description="Número de miembros que formarán el equipo final.")
    tipo: Optional[str] = Field(default="Maratón de Código", description="Tipo de competencia")

    class Config:
        from_attributes = True

class AsignacionRequest(BaseModel):
    """Request simplificado - solo datos de competencia, sin parámetros de algoritmo"""
    participantes: List[Dict[str, Any]] = Field(description="Lista de participantes disponibles")
    problemas: List[Dict[str, Any]] = Field(description="Lista de problemas de la competencia")
    configuracion: ConfiguracionCompetencia = Field(description="Configuración de la competencia")

    @validator('participantes')
    def validate_participantes(cls, v):
        if not v or len(v) == 0:
            raise ValueError("Debe haber al menos un participante")
        return v

    @validator('problemas')
    def validate_problemas(cls, v):
        if not v or len(v) == 0:
            raise ValueError("Debe haber al menos un problema")
        return v

    class Config:
        from_attributes = True

# ========================================
# MODELOS PARA RESPUESTAS
# ========================================

class EstadisticasSolucion(BaseModel):
    """Estadísticas calculadas de una solución"""
    puntuacion_total_esperada: float
    tiempo_total_estimado: int
    compatibilidad_promedio: float
    participantes_utilizados: int

class AsignacionDetalle(BaseModel):
    """Detalle de una asignación problema-participante"""
    problema_nombre: str
    participante_nombre: str
    compatibilidad: float
    tiempo_estimado: float
    puntuacion_esperada: float

class MetricaTransparencia(BaseModel):
    """Métricas de transparencia del algoritmo"""
    pesos_utilizados: Dict[str, float]
    num_asignaciones: int
    algoritmo_puro: bool

class SolucionOptimizada(BaseModel):
    """Una solución completa del algoritmo genético"""
    solucion_id: int
    fitness: float
    nombre_estrategia: Optional[str] = None
    asignaciones_detalle: List[AsignacionDetalle]
    estadisticas: Optional[EstadisticasSolucion] = None
    metrica_transparencia: Optional[MetricaTransparencia] = None

class EstadisticasFinales(BaseModel):
    """Estadísticas finales del algoritmo"""
    generaciones_ejecutadas: int
    poblacion_final: int
    mejor_fitness: float
    fitness_promedio: float

class HistorialFitness(BaseModel):
    """Punto en el historial de fitness"""
    generacion: int
    mejor_fitness: float
    fitness_promedio: float

class ResponseOptimizacion(BaseModel):
    """Respuesta completa de la optimización - simplificada"""
    success: bool
    mensaje: str
    mejor_solucion: Optional[SolucionOptimizada] = None
    historial: List[HistorialFitness] = []
    estadisticas_finales: Optional[EstadisticasFinales] = None

    class Config:
        from_attributes = True