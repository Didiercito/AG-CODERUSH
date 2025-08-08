from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

import logging
import numpy as np
import random
from models.schemas import AsignacionRequest
from core.algoritmo_genetico import AlgoritmoGeneticoCoderush

logger = logging.getLogger(__name__)
router = APIRouter()

def ejecutar_estrategia(problemas, participantes, config, pesos):
    algoritmo = AlgoritmoGeneticoCoderush(
        problemas=problemas,
        participantes=participantes,
        configuracion_competencia=config,
        pesos_estrategia=pesos
    )
    return algoritmo.iniciar_optimizacion()

@router.post("/optimizar")
async def optimizar_asignaciones(request: AsignacionRequest):
    try:
        logger.info("Iniciando optimización con diversidad estratégica forzada.")
        
        config = request.configuracion
        participantes_originales = request.participantes
        problemas_originales = request.problemas
        
        if config.tamanio_equipo > len(participantes_originales):
            raise HTTPException(status_code=400, detail="El tamaño del equipo no puede ser mayor que el número de participantes.")

        estrategias = [
            {"nombre": "Solución 1 (Max Puntos)", "pesos": {'puntuacion': 0.7, 'compatibilidad': 0.1, 'tiempo': 0.1, 'balance': 0.1}},
            {"nombre": "Solución 2 (Equilibrada)", "pesos": {'puntuacion': 0.4, 'compatibilidad': 0.3, 'tiempo': 0.2, 'balance': 0.1}},
            {"nombre": "Solución 3 (Eficiente)", "pesos": {'puntuacion': 0.2, 'compatibilidad': 0.2, 'tiempo': 0.5, 'balance': 0.1}}
        ]

        soluciones_finales = []
        participantes_usados_globalmente = set()

        for i, estrategia in enumerate(estrategias):
            logger.info(f"Ejecutando: {estrategia['nombre']}")
            
            participantes_disponibles = [p for p in participantes_originales if p.get('nombre') not in participantes_usados_globalmente]
            if len(participantes_disponibles) < config.tamanio_equipo:
                participantes_disponibles = participantes_originales
            
            # <<< CAMBIO CLAVE: Ordenamiento robusto que convierte a float antes de comparar.
            participantes_disponibles.sort(key=lambda p: float(p.get('tasa_exito_historica', 0.0)), reverse=True)
            equipo_seleccionado = participantes_disponibles[:config.tamanio_equipo]

            resultado = ejecutar_estrategia(problemas_originales, equipo_seleccionado, config, estrategia['pesos'])
            
            if resultado.get('exito') and resultado.get('mejor_solucion'):
                mejor_solucion = resultado['mejor_solucion']
                mejor_solucion['nombre_estrategia'] = estrategia['nombre']
                soluciones_finales.append(mejor_solucion)
                
                if i < len(estrategias) - 1:
                    asignaciones = mejor_solucion.get('asignaciones_detalle', [])
                    asignaciones.sort(key=lambda x: x.get('compatibilidad', 0), reverse=True)
                    for asig in asignaciones[:2]:
                        if asig.get('participante_nombre'):
                            participantes_usados_globalmente.add(asig['participante_nombre'])

        if not soluciones_finales:
            raise HTTPException(status_code=500, detail="Ninguna estrategia pudo generar una solución válida.")

        for solucion in soluciones_finales:
            asignaciones = solucion.get('asignaciones_detalle', [])
            stats = {}
            if asignaciones:
                puntuacion = sum(float(a.get('puntuacion_esperada', 0)) for a in asignaciones)
                tiempo = sum(float(a.get('tiempo_estimado', 120)) for a in asignaciones)
                compatibilidad_prom = np.mean([a.get('compatibilidad', 0.6) for a in asignaciones]) * 100
                stats = {
                    'puntuacion_total_esperada': round(puntuacion, 2),
                    'tiempo_total_estimado': int(tiempo),
                    'compatibilidad_promedio': round(compatibilidad_prom, 1),
                    'participantes_utilizados': len(set(a.get('participante_nombre') for a in asignaciones)),
                }
            solucion['estadisticas'] = stats

        return JSONResponse(content={
            'success': True,
            'mensaje': 'Optimización multi-estrategia completada.',
            'top_3_soluciones': {f'solucion_{i+1}': sol for i, sol in enumerate(soluciones_finales)},
            'analisis_comparativo': {'razon': 'Se presentan las mejores opciones para cada estrategia.'},
        })
    except Exception as e:
        logger.error(f"Error crítico en la optimización: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")