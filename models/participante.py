from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional, TYPE_CHECKING
import numpy as np
from core.enums import TipoProblema, TipoHabilidad

if TYPE_CHECKING:
    from models.problema import ProblemaCompleto

class Habilidad(BaseModel):
    tipo: TipoHabilidad
    nivel: float = Field(ge=0.0, le=1.0, description="Nivel de 0.0 a 1.0")
    experiencia_anos: float = Field(ge=0.0, description="Años de experiencia")
    certificaciones: List[str] = Field(default_factory=list)
    proyectos_relevantes: int = Field(ge=0, default=0)

class PerfilParticipante(BaseModel):
    id: int
    nombre: str
    email: str
    edad: int = Field(ge=16, le=100)
    universidad: Optional[str] = None
    semestre: Optional[int] = None
    
    # Sistema de habilidades robusto
    habilidades: Dict[TipoHabilidad, Habilidad]
    
    # Estadísticas históricas
    competencias_participadas: int = Field(ge=0, default=0)
    problemas_resueltos_total: int = Field(ge=0, default=0)
    ranking_promedio: Optional[float] = None
    tasa_exito_historica: float = Field(ge=0.0, le=1.0, default=0.5)
    
    # Preferencias y restricciones
    tipos_problema_preferidos: List[TipoProblema] = Field(default_factory=list)
    tipos_problema_evitar: List[TipoProblema] = Field(default_factory=list)
    tiempo_maximo_disponible: int = Field(gt=0, default=300)  # minutos
    
    # Factores dinámicos
    nivel_energia: float = Field(ge=0.0, le=1.0, default=0.8)
    nivel_concentracion: float = Field(ge=0.0, le=1.0, default=0.8)
    disponibilidad: bool = True
    
    @validator('habilidades')
    @classmethod
    def validar_habilidades_minimas(cls, v):
        """Validar que tenga al menos algunas habilidades básicas"""
        if not v:
            raise ValueError("Debe tener al menos una habilidad definida")
        return v
    
    def calcular_compatibilidad_problema(self, problema) -> float:
        """Calcula compatibilidad con un problema específico"""
        if not self.disponibilidad:
            return 0.0
        
        # Evitar tipos de problema no deseados
        if hasattr(problema, 'tipo') and problema.tipo in self.tipos_problema_evitar:
            return 0.1
        
        # Bonificación por preferencias
        bonus_preferencia = 0.0
        if hasattr(problema, 'tipo') and problema.tipo in self.tipos_problema_preferidos:
            bonus_preferencia = 0.2
        
        # Habilidades requeridas para el problema
        compatibilidad_habilidades = 0.0
        if hasattr(problema, 'habilidades_requeridas'):
            habilidades_relevantes = problema.habilidades_requeridas
            
            if habilidades_relevantes:
                compatibilidades = []
                for habilidad_req, peso in habilidades_relevantes.items():
                    if habilidad_req in self.habilidades:
                        habilidad_participante = self.habilidades[habilidad_req]
                        # Considerar nivel, experiencia y proyectos
                        score_habilidad = (
                            0.6 * habilidad_participante.nivel +
                            0.3 * min(habilidad_participante.experiencia_anos / 5.0, 1.0) +
                            0.1 * min(habilidad_participante.proyectos_relevantes / 10.0, 1.0)
                        )
                        compatibilidades.append(score_habilidad * peso)
                    else:
                        compatibilidades.append(0.0)
                
                compatibilidad_habilidades = np.mean(compatibilidades) if compatibilidades else 0.0
        
        # Ajuste por factores dinámicos
        factor_dinamico = (self.nivel_energia + self.nivel_concentracion) / 2.0
        
        # Ajuste por experiencia histórica
        factor_experiencia = min(self.tasa_exito_historica + 0.1, 1.0)
        
        compatibilidad_final = (
            0.5 * compatibilidad_habilidades +
            0.2 * factor_dinamico +
            0.2 * factor_experiencia +
            0.1 * bonus_preferencia
        )
        
        return min(compatibilidad_final, 1.0)
    
    def estimar_tiempo_resolucion(self, problema) -> int:
        """Estima tiempo en minutos para resolver el problema"""
        from core.enums import NivelDificultad
        
        compatibilidad = self.calcular_compatibilidad_problema(problema)
        
        # Tiempo base según dificultad
        tiempo_base = 120  # Tiempo por defecto
        
        if hasattr(problema, 'nivel_dificultad'):
            tiempo_base = {
                NivelDificultad.MUY_FACIL: 30,
                NivelDificultad.FACIL: 60,
                NivelDificultad.MEDIO: 120,
                NivelDificultad.DIFICIL: 180,
                NivelDificultad.MUY_DIFICIL: 240
            }.get(problema.nivel_dificultad, 120)
        
        # Ajustar por compatibilidad
        factor_habilidad = 2.0 - compatibilidad  # Más habilidad = menos tiempo
        
        # Ajustar por energía y concentración
        factor_estado = 2.0 - ((self.nivel_energia + self.nivel_concentracion) / 2.0)
        
        tiempo_estimado = int(tiempo_base * factor_habilidad * factor_estado)
        
        return max(tiempo_estimado, 15)  # Mínimo 15 minutos
    
    def calcular_probabilidad_exito(self, problema) -> float:
        """Calcula probabilidad de resolver exitosamente el problema"""
        from core.enums import NivelDificultad
        
        compatibilidad = self.calcular_compatibilidad_problema(problema)
        
        factor_experiencia = self.tasa_exito_historica
        
        tiempo_estimado = self.estimar_tiempo_resolucion(problema)
        factor_tiempo = min(self.tiempo_maximo_disponible / tiempo_estimado, 1.0)
        
        dificultad_numerica = 0.5  
        
        if hasattr(problema, 'nivel_dificultad'):
            dificultad_numerica = {
                NivelDificultad.MUY_FACIL: 0.1,
                NivelDificultad.FACIL: 0.3,
                NivelDificultad.MEDIO: 0.5,
                NivelDificultad.DIFICIL: 0.7,
                NivelDificultad.MUY_DIFICIL: 0.9
            }.get(problema.nivel_dificultad, 0.5)
        
        factor_dificultad = max(0.1, 1.0 - dificultad_numerica + compatibilidad)
        
        probabilidad = (
            0.4 * compatibilidad +
            0.3 * factor_experiencia +
            0.2 * factor_tiempo +
            0.1 * factor_dificultad
        )
        
        return min(probabilidad, 0.95)  