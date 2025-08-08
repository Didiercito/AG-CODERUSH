# api/routes/problemas.py
"""
Rutas para gestión de problemas
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Optional
from database.database import get_db_session
from database.crud import crud_problema
from api.dependencies import (
    validar_problema_existe, 
    validar_paginacion,
    respuesta_exito,
    respuesta_error
)

router = APIRouter()

# ============================================================================
# CRUD PROBLEMAS
# ============================================================================

@router.post("/problemas", status_code=201, tags=["problemas"])
async def crear_problema(problema_data: dict, db: Session = Depends(get_db_session)):
    """Crear nuevo problema"""
    try:
        problema = crud_problema.create(db, problema_data)
        return respuesta_exito(
            "Problema creado exitosamente", 
            {"id": problema.id, "nombre": problema.nombre}
        )
    except Exception as e:
        raise respuesta_error(f"Error creando problema: {str(e)}")

@router.get("/problemas/{problema_id}", tags=["problemas"])
async def obtener_problema(problema_id: int, db: Session = Depends(get_db_session)):
    """Obtener problema por ID"""
    problema = validar_problema_existe(problema_id, db)
    
    return {
        "exito": True,
        "problema": {
            "id": problema.id,
            "nombre": problema.nombre,
            "descripcion": problema.descripcion,
            "tipo": problema.tipo,
            "nivel_dificultad": problema.nivel_dificultad,
            "puntos_base": problema.puntos_base,
            "multiplicador_dificultad": problema.multiplicador_dificultad,
            "bonus_tiempo": problema.bonus_tiempo,
            "habilidades_requeridas": problema.habilidades_requeridas,
            "tiempo_limite": problema.tiempo_limite,
            "memoria_limite": problema.memoria_limite,
            "fuente": problema.fuente,
            "año_competencia": problema.año_competencia,
            "tasa_resolucion_historica": problema.tasa_resolucion_historica,
            "url_problema": problema.url_problema,
            "tags": problema.tags,
            "problemas_prerequisito": problema.problemas_prerequisito,
            "problemas_relacionados": problema.problemas_relacionados,
            "created_at": problema.created_at.isoformat() if problema.created_at else None
        }
    }

@router.get("/problemas", tags=["problemas"])
async def listar_problemas(
    skip: int = 0, 
    limit: int = 100, 
    tipo: Optional[str] = None, 
    dificultad: Optional[str] = None, 
    db: Session = Depends(get_db_session)
):
    """Listar problemas con filtros opcionales"""
    try:
        skip, limit = validar_paginacion(skip, limit)
        
        if tipo:
            problemas = crud_problema.get_by_tipo(db, tipo)
        elif dificultad:
            problemas = crud_problema.get_by_dificultad(db, dificultad)
        else:
            problemas = crud_problema.get_all(db, skip, limit)
        
        problemas_data = []
        for p in problemas:
            problemas_data.append({
                "id": p.id,
                "nombre": p.nombre,
                "descripcion": p.descripcion,
                "tipo": p.tipo,
                "nivel_dificultad": p.nivel_dificultad,
                "puntos_base": p.puntos_base,
                "multiplicador_dificultad": p.multiplicador_dificultad,
                "bonus_tiempo": p.bonus_tiempo,
                "habilidades_requeridas": p.habilidades_requeridas,
                "tiempo_limite": p.tiempo_limite,
                "memoria_limite": p.memoria_limite,
                "fuente": p.fuente,
                "año_competencia": p.año_competencia,
                "tasa_resolucion_historica": p.tasa_resolucion_historica,
                "url_problema": p.url_problema,
                "tags": p.tags,
                "problemas_prerequisito": p.problemas_prerequisito,
                "problemas_relacionados": p.problemas_relacionados,
                "created_at": p.created_at.isoformat() if p.created_at else None
            })
        
        filtros_aplicados = {}
        if tipo:
            filtros_aplicados["tipo"] = tipo
        if dificultad:
            filtros_aplicados["dificultad"] = dificultad
        
        return respuesta_exito(
            f"Se encontraron {len(problemas_data)} problemas",
            {
                "total": len(problemas_data),
                "problemas": problemas_data,
                "filtros": filtros_aplicados,
                "paginacion": {"skip": skip, "limit": limit}
            }
        )
    except Exception as e:
        raise respuesta_error(f"Error listando problemas: {str(e)}")

@router.put("/problemas/{problema_id}", tags=["problemas"])
async def actualizar_problema(
    problema_id: int, 
    update_data: dict, 
    db: Session = Depends(get_db_session)
):
    """Actualizar problema"""
    try:
        validar_problema_existe(problema_id, db)
        problema = crud_problema.update(db, problema_id, update_data)
        
        if not problema:
            raise respuesta_error("Error actualizando problema")
            
        return respuesta_exito(
            "Problema actualizado exitosamente",
            {"id": problema.id, "nombre": problema.nombre}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise respuesta_error(f"Error actualizando problema: {str(e)}")

@router.delete("/problemas/{problema_id}", tags=["problemas"])
async def eliminar_problema(problema_id: int, db: Session = Depends(get_db_session)):
    """Eliminar problema"""
    try:
        validar_problema_existe(problema_id, db)
        
        if not crud_problema.delete(db, problema_id):
            raise respuesta_error("Error eliminando problema")
        
        return respuesta_exito(f"Problema {problema_id} eliminado exitosamente")
    except HTTPException:
        raise
    except Exception as e:
        raise respuesta_error(f"Error eliminando problema: {str(e)}")

# ============================================================================
# ANÁLISIS DE PROBLEMAS
# ============================================================================

@router.get("/problemas/{problema_id}/estadisticas", tags=["problemas"])
async def estadisticas_problema(problema_id: int, db: Session = Depends(get_db_session)):
    """Obtiene estadísticas de un problema específico"""
    problema = validar_problema_existe(problema_id, db)
    
    puntos_totales = problema.puntos_base * problema.multiplicador_dificultad
    
    return respuesta_exito(
        "Estadísticas de problema obtenidas",
        {
            'problema': {
                'id': problema_id,
                'nombre': problema.nombre,
                'descripcion': problema.descripcion
            },
            'metricas': {
                'dificultad': problema.nivel_dificultad,
                'tipo': problema.tipo,
                'puntos_base': problema.puntos_base,
                'multiplicador_dificultad': problema.multiplicador_dificultad,
                'puntos_totales': int(puntos_totales),
                'tiempo_limite': problema.tiempo_limite,
                'memoria_limite': problema.memoria_limite,
                'tasa_resolucion_historica': f"{problema.tasa_resolucion_historica:.1%}",
                'fuente': problema.fuente,
                'año_competencia': problema.año_competencia
            },
            'habilidades_requeridas': list(problema.habilidades_requeridas.keys()) if problema.habilidades_requeridas else [],
            'tags': problema.tags or [],
            'complejidad': {
                'tiempo_estimado': problema.tiempo_limite,
                'memoria_requerida': problema.memoria_limite,
                'num_habilidades_requeridas': len(problema.habilidades_requeridas) if problema.habilidades_requeridas else 0,
                'nivel_complejidad': _calcular_nivel_complejidad(problema)
            },
            'recomendaciones': [
                f"Requiere nivel {problema.nivel_dificultad} de dificultad",
                f"Tipo de problema: {problema.tipo}",
                f"Tiempo límite: {problema.tiempo_limite} minutos",
                f"Puntuación máxima: {int(puntos_totales)} puntos",
                f"Tasa de resolución histórica: {problema.tasa_resolucion_historica:.1%}"
            ]
        }
    )

def _calcular_nivel_complejidad(problema) -> str:
    """Calcula nivel de complejidad basado en múltiples factores"""
    score = 0
    
    # Puntos por dificultad
    dificultad_scores = {
        'facil': 1, 'medio': 2, 'dificil': 3
    }
    score += dificultad_scores.get(problema.nivel_dificultad, 2)
    
    # Puntos por tiempo límite
    if problema.tiempo_limite > 180:
        score += 2
    elif problema.tiempo_limite > 120:
        score += 1
    
    # Puntos por habilidades requeridas
    if problema.habilidades_requeridas:
        score += len(problema.habilidades_requeridas)
    
    # Clasificar
    if score <= 3:
        return "Básico"
    elif score <= 6:
        return "Intermedio"
    else:
        return "Avanzado"
    
    
#from fastapi.responses import JSONResponse