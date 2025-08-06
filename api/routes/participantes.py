from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Optional
from database.database import get_db_session
from database.crud import crud_participante
from api.dependencies import (
    validar_participante_existe, 
    validar_paginacion,
    respuesta_exito,
    respuesta_error
)

router = APIRouter()


@router.post("/participantes", status_code=201, tags=["participantes"])
async def crear_participante(participante_data: dict, db: Session = Depends(get_db_session)):
    """Crear nuevo participante"""
    try:
        participante = crud_participante.create(db, participante_data)
        return respuesta_exito(
            "Participante creado exitosamente", 
            {"id": participante.id, "nombre": participante.nombre}
        )
    except Exception as e:
        raise respuesta_error(f"Error creando participante: {str(e)}")

@router.get("/participantes/{participante_id}", tags=["participantes"])
async def obtener_participante(participante_id: int, db: Session = Depends(get_db_session)):
    """Obtener participante por ID"""
    participante = validar_participante_existe(participante_id, db)
    
    return {
        "exito": True,
        "participante": {
            "id": participante.id,
            "nombre": participante.nombre,
            "email": participante.email,
            "edad": participante.edad,
            "universidad": participante.universidad,
            "semestre": participante.semestre,
            "habilidades": participante.habilidades,
            "competencias_participadas": participante.competencias_participadas,
            "problemas_resueltos_total": participante.problemas_resueltos_total,
            "tasa_exito_historica": participante.tasa_exito_historica,
            "ranking_promedio": participante.ranking_promedio,
            "tipos_problema_preferidos": participante.tipos_problema_preferidos,
            "tipos_problema_evitar": participante.tipos_problema_evitar,
            "tiempo_maximo_disponible": participante.tiempo_maximo_disponible,
            "nivel_energia": participante.nivel_energia,
            "nivel_concentracion": participante.nivel_concentracion,
            "disponibilidad": participante.disponibilidad,
            "created_at": participante.created_at.isoformat() if participante.created_at else None
        }
    }

@router.get("/participantes", tags=["participantes"])
async def listar_participantes(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db_session)
):
    """Listar todos los participantes"""
    try:
        skip, limit = validar_paginacion(skip, limit)
        participantes = crud_participante.get_all(db, skip, limit)
        
        participantes_data = []
        for p in participantes:
            participantes_data.append({
                "id": p.id,
                "nombre": p.nombre,
                "email": p.email,
                "edad": p.edad,
                "universidad": p.universidad,
                "semestre": p.semestre,
                "habilidades": p.habilidades,
                "competencias_participadas": p.competencias_participadas,
                "problemas_resueltos_total": p.problemas_resueltos_total,
                "tasa_exito_historica": p.tasa_exito_historica,
                "ranking_promedio": p.ranking_promedio,
                "tipos_problema_preferidos": p.tipos_problema_preferidos,
                "tipos_problema_evitar": p.tipos_problema_evitar,
                "tiempo_maximo_disponible": p.tiempo_maximo_disponible,
                "nivel_energia": p.nivel_energia,
                "nivel_concentracion": p.nivel_concentracion,
                "disponibilidad": p.disponibilidad,
                "created_at": p.created_at.isoformat() if p.created_at else None
            })
        
        return respuesta_exito(
            f"Se encontraron {len(participantes_data)} participantes",
            {
                "total": len(participantes_data),
                "participantes": participantes_data,
                "paginacion": {"skip": skip, "limit": limit}
            }
        )
    except Exception as e:
        raise respuesta_error(f"Error listando participantes: {str(e)}")

@router.get("/participantes/disponibles", tags=["participantes"])
async def participantes_disponibles(db: Session = Depends(get_db_session)):
    """Obtener participantes disponibles"""
    try:
        participantes = crud_participante.get_available(db)
        
        participantes_data = []
        for p in participantes:
            participantes_data.append({
                "id": p.id,
                "nombre": p.nombre,
                "email": p.email,
                "habilidades": p.habilidades,
                "competencias_participadas": p.competencias_participadas,
                "tasa_exito_historica": p.tasa_exito_historica,
                "disponibilidad": p.disponibilidad,
                "nivel_energia": p.nivel_energia,
                "nivel_concentracion": p.nivel_concentracion
            })
        
        return respuesta_exito(
            f"Se encontraron {len(participantes_data)} participantes disponibles",
            {
                "total_disponibles": len(participantes_data),
                "participantes": participantes_data
            }
        )
    except Exception as e:
        raise respuesta_error(f"Error obteniendo participantes disponibles: {str(e)}")

@router.put("/participantes/{participante_id}", tags=["participantes"])
async def actualizar_participante(
    participante_id: int, 
    update_data: dict, 
    db: Session = Depends(get_db_session)
):
    """Actualizar participante"""
    try:
        validar_participante_existe(participante_id, db)
        participante = crud_participante.update(db, participante_id, update_data)
        
        if not participante:
            raise respuesta_error("Error actualizando participante")
            
        return respuesta_exito(
            "Participante actualizado exitosamente",
            {"id": participante.id, "nombre": participante.nombre}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise respuesta_error(f"Error actualizando participante: {str(e)}")

@router.delete("/participantes/{participante_id}", tags=["participantes"])
async def eliminar_participante(participante_id: int, db: Session = Depends(get_db_session)):
    """Eliminar participante"""
    try:
        validar_participante_existe(participante_id, db)
        
        if not crud_participante.delete(db, participante_id):
            raise respuesta_error("Error eliminando participante")
        
        return respuesta_exito(f"Participante {participante_id} eliminado exitosamente")
    except HTTPException:
        raise
    except Exception as e:
        raise respuesta_error(f"Error eliminando participante: {str(e)}")

# ============================================================================
# ANÁLISIS DE PARTICIPANTES
# ============================================================================

@router.get("/participantes/{participante_id}/analisis", tags=["participantes"])
async def analizar_participante(participante_id: int, db: Session = Depends(get_db_session)):
    """Analiza el perfil de un participante específico"""
    participante = validar_participante_existe(participante_id, db)
    
    habilidades = participante.habilidades or {}
    fortalezas = []
    areas_mejora = []
    
    for habilidad, data in habilidades.items():
        if isinstance(data, dict) and 'nivel' in data:
            if data['nivel'] >= 0.8:
                fortalezas.append(f"Excelente en {habilidad}")
            elif data['nivel'] <= 0.5:
                areas_mejora.append(f"Mejorar {habilidad}")
    
    return respuesta_exito(
        "Análisis de participante completado",
        {
            'participante': {
                'id': participante_id,
                'nombre': participante.nombre,
                'universidad': participante.universidad
            },
            'fortalezas': fortalezas if fortalezas else ['Buen potencial general'],
            'areas_mejora': areas_mejora if areas_mejora else ['Continuar desarrollando habilidades técnicas'],
            'metricas': {
                'competencias_participadas': participante.competencias_participadas,
                'tasa_exito_historica': f"{participante.tasa_exito_historica:.1%}",
                'disponibilidad': "Disponible" if participante.disponibilidad else "No disponible",
                'nivel_experiencia': (
                    'Alto' if participante.competencias_participadas >= 10 
                    else 'Medio' if participante.competencias_participadas >= 5 
                    else 'Básico'
                ),
                'nivel_energia': participante.nivel_energia,
                'nivel_concentracion': participante.nivel_concentracion
            }
        }
    )