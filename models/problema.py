from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from core.enums import TipoProblema, NivelDificultad, TipoHabilidad

class ProblemaCompleto(BaseModel):
    id: int
    nombre: str
    descripcion: str
    tipo: TipoProblema
    nivel_dificultad: NivelDificultad
    
    puntos_base: int = Field(gt=0)
    multiplicador_dificultad: float = Field(ge=1.0, le=3.0)
    bonus_tiempo: int = Field(ge=0, default=50)  
    
    habilidades_requeridas: Dict[TipoHabilidad, float] = Field(default_factory=dict)
    tiempo_limite: int = Field(gt=0, default=180)  
    memoria_limite: int = Field(gt=0, default=256) 
    
    fuente: Optional[str] = None
    año_competencia: Optional[int] = None
    tasa_resolucion_historica: float = Field(ge=0.0, le=1.0, default=0.5)
    
    problemas_prerequisito: List[int] = Field(default_factory=list)
    problemas_relacionados: List[int] = Field(default_factory=list)
    
    @property
    def puntos_totales(self) -> int:
        return int(self.puntos_base * self.multiplicador_dificultad)
    
    @property
    def dificultad_numerica(self) -> float:
        return {
            NivelDificultad.MUY_FACIL: 0.15,
            NivelDificultad.FACIL: 0.35,
            NivelDificultad.MEDIO: 0.55,
            NivelDificultad.DIFICIL: 0.75,
            NivelDificultad.MUY_DIFICIL: 0.95
        }.get(self.nivel_dificultad, 0.5)