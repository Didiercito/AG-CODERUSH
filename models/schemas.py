from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class ConfiguracionCompetencia(BaseModel):
    nombre: str = Field(description="Nombre descriptivo de la competencia.")
    tiempo_total_minutos: int = Field(default=300, gt=0, description="Duración total de la competencia en minutos.")
    tamanio_equipo: int = Field(default=3, gt=0, description="Número de miembros que formarán el equipo final.")

    class Config:
        from_attributes = True

class AsignacionRequest(BaseModel):
    participantes: List[Dict[str, Any]]
    problemas: List[Dict[str, Any]]
    configuracion: ConfiguracionCompetencia