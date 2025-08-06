# api/dependencies.py
"""
Dependencias compartidas para todas las rutas
"""

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from database.database import get_db_session
from database.crud import crud_participante, crud_problema, crud_asignacion
from datetime import datetime
import uuid
import time

def get_database() -> Session:
    return Depends(get_db_session)

def generar_uuid() -> str:
    return str(uuid.uuid4())

def timestamp_actual() -> str:
    return datetime.now().isoformat()

def medir_tiempo_ejecucion():
    def decorator(func):
        def wrapper(*args, **kwargs):
            inicio = time.time()
            resultado = func(*args, **kwargs)
            tiempo_ejecucion = time.time() - inicio
            
            if isinstance(resultado, dict):
                resultado['tiempo_ejecucion_segundos'] = tiempo_ejecucion
            
            return resultado
        return wrapper
    return decorator

def validar_participante_existe(participante_id: int, db: Session):
    participante = crud_participante.get(db, participante_id)
    if not participante:
        raise HTTPException(
            status_code=404, 
            detail=f"Participante con ID {participante_id} no encontrado"
        )
    return participante

def validar_problema_existe(problema_id: int, db: Session):
    """Valida que un problema existe"""
    problema = crud_problema.get(db, problema_id)
    if not problema:
        raise HTTPException(
            status_code=404, 
            detail=f"Problema con ID {problema_id} no encontrado"
        )
    return problema

def validar_asignacion_existe(asignacion_id: int, db: Session):
    asignacion = crud_asignacion.get(db, asignacion_id)
    if not asignacion:
        raise HTTPException(
            status_code=404, 
            detail=f"Asignación con ID {asignacion_id} no encontrada"
        )
    return asignacion

def respuesta_exito(mensaje: str, data: dict = None) -> dict:
    respuesta = {
        "exito": True,
        "mensaje": mensaje,
        "timestamp": timestamp_actual()
    }
    if data:
        respuesta.update(data)
    return respuesta

def respuesta_error(mensaje: str, status_code: int = 400) -> HTTPException:
    raise HTTPException(status_code=status_code, detail=mensaje)

def validar_paginacion(skip: int = 0, limit: int = 100):
    if skip < 0:
        raise HTTPException(status_code=400, detail="skip debe ser >= 0")
    if limit <= 0 or limit > 1000:
        raise HTTPException(status_code=400, detail="limit debe estar entre 1 y 1000")
    return skip, limit