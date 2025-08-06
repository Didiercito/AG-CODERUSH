from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from models.participante import PerfilParticipante
    from models.problema import ProblemaCompleto

class ConfiguracionCompetencia(BaseModel):
    nombre: str
    duracion_total: int = Field(gt=0, default=300)  
    max_participantes: int = Field(gt=0, default=3)
    penalizacion_tiempo: float = Field(ge=0.0, default=0.1)
    bonus_resolucion_rapida: bool = True
    permitir_colaboracion: bool = False
    
    peso_puntuacion: float = Field(ge=0.0, le=1.0, default=0.4)
    peso_compatibilidad: float = Field(ge=0.0, le=1.0, default=0.25)
    peso_balance_carga: float = Field(ge=0.0, le=1.0, default=0.2)
    peso_probabilidad_exito: float = Field(ge=0.0, le=1.0, default=0.15)
    
    @validator('peso_probabilidad_exito')  
    @classmethod
    def validar_suma_pesos(cls, v, values):
        peso_puntuacion = values.get('peso_puntuacion', 0)
        peso_compatibilidad = values.get('peso_compatibilidad', 0)
        peso_balance_carga = values.get('peso_balance_carga', 0)
        peso_probabilidad_exito = v
        
        suma_pesos = peso_puntuacion + peso_compatibilidad + peso_balance_carga + peso_probabilidad_exito
        
        if abs(suma_pesos - 1.0) > 0.05:
            raise ValueError(f"Los pesos deben sumar aproximadamente 1.0, suma actual: {suma_pesos}")
        
        return v

class AsignacionRequest(BaseModel):
    problemas: List[dict] 
    participantes: List[dict]  
    configuracion_competencia: Optional[ConfiguracionCompetencia] = None
    parametros_ag: Optional[Dict] = None

class AsignacionResponse(BaseModel):
    exito: bool
    mensaje: str
    matriz_asignacion: List[List[int]]
    fitness_final: float
    asignaciones_detalle: List[Dict]
    estadisticas: Dict
    evolucion: Dict
    tiempo_ejecucion: float

class SimulacionResponse(BaseModel):
    simulacion_completada: bool
    asignacion_original: AsignacionResponse
    simulacion: Dict
    eficiencia_asignacion: float