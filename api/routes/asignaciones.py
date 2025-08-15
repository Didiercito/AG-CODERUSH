from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import logging
import numpy as np
from models.schemas import AsignacionRequest
from core.algoritmo_genetico import AlgoritmoGeneticoCoderush
from core.visualizaciones import procesar_datos_algoritmo, crear_visualizador

logger = logging.getLogger(__name__)
router = APIRouter()

cache_metricas = {}

@router.post("/optimizar")
async def optimizar_asignaciones(request: AsignacionRequest):
    try:
        global cache_metricas
        cache_metricas.clear() 
        
        config = request.configuracion
        participantes_originales = request.participantes
        problemas_originales = request.problemas
        
        logger.info("Iniciando optimización con algoritmo genético puro.")
        
        # Validación básica
        if config.tamanio_equipo > len(participantes_originales):
            raise HTTPException(
                status_code=400, 
                detail="El tamaño del equipo no puede ser mayor que el número de participantes."
            )

        # Seleccionar equipo basado en tasa de éxito histórica
        participantes_originales.sort(
            key=lambda p: float(p['tasa_exito_historica']), 
            reverse=True
        )
        equipo_seleccionado = participantes_originales[:config.tamanio_equipo]
        
        logger.info(f"Equipo seleccionado: {[p['nombre'] for p in equipo_seleccionado]}")
        logger.info(f"Problemas a resolver: {len(problemas_originales)}")

        # ALGORITMO GENÉTICO PURO
        logger.info(f"Configurando algoritmo con {len(equipo_seleccionado)} participantes")
        
        algoritmo = AlgoritmoGeneticoCoderush(
            problemas=problemas_originales,
            participantes=equipo_seleccionado,
            configuracion_competencia=config
        )
        
        resultado = algoritmo.iniciar_optimizacion()
        
        if not resultado.get('exito'):
            error_msg = resultado.get('mensaje', 'No se pudo generar una solución válida.')
            raise HTTPException(status_code=500, detail=error_msg)

        mejores_soluciones = resultado['mejores_soluciones']

        # Calcular estadísticas para cada solución
        for solucion_key, solucion in mejores_soluciones.items():
            asignaciones = solucion.get('asignaciones_detalle', [])
            if asignaciones:
                puntuacion = sum(float(a['puntuacion_esperada']) for a in asignaciones)
                
                # Calcular tiempo en paralelo, no secuencial
                tiempo_por_participante = {}
                for asig in asignaciones:
                    participante = asig['participante_nombre']
                    if participante not in tiempo_por_participante:
                        tiempo_por_participante[participante] = 0
                    tiempo_por_participante[participante] += float(asig['tiempo_estimado'])
                
                # Tiempo total = máximo tiempo de cualquier participante (trabajo en paralelo)
                tiempo_total_paralelo = max(tiempo_por_participante.values()) if tiempo_por_participante else 0
                
                compatibilidades = [a['compatibilidad'] for a in asignaciones]
                compatibilidad_prom = np.mean(compatibilidades) * 100
                
                estadisticas = {
                    'puntuacion_total_esperada': round(puntuacion, 2),
                    'tiempo_total_estimado': int(tiempo_total_paralelo),
                    'compatibilidad_promedio': round(compatibilidad_prom, 1),
                    'participantes_utilizados': len(set(a['participante_nombre'] for a in asignaciones))
                }
                solucion['estadisticas'] = estadisticas

        # ✅ NUEVO: Procesar datos para visualizaciones
        # Obtener población final para análisis adicional
        try:
            # Intentar obtener población final del algoritmo si está disponible
            poblacion_final = getattr(algoritmo, '_poblacion_final', [])
        except:
            poblacion_final = []

        # Procesar datos de visualización una sola vez
        datos_visualizacion = procesar_datos_algoritmo(
            historial_basico=resultado.get('historial', []),
            poblacion_final=poblacion_final
        )

        # CORRECCIÓN: Guardar métricas para CADA una de las 3 soluciones
        for i, (solucion_key, solucion) in enumerate(mejores_soluciones.items(), 1):
            cache_metricas[i] = {
                'historial_fitness': resultado.get('historial', []),
                'estadisticas_finales': resultado.get('estadisticas_finales', {}),
                'mejores_soluciones': {solucion_key: solucion},
                'parametros': {
                    'poblacion': algoritmo.poblacion_size,
                    'generaciones': algoritmo.generaciones_max,
                    'tasa_cruce': algoritmo.prob_cruce,
                    'tasa_mutacion': algoritmo.prob_mutacion,
                    'elitismo': algoritmo.elite_size
                },
                # ✅ NUEVO: Agregar datos de visualización procesados
                'datos_visualizacion': datos_visualizacion
            }

        logger.info(f"Optimización completada exitosamente. {len(mejores_soluciones)} soluciones generadas.")
        logger.info(f"Métricas guardadas para soluciones: {list(cache_metricas.keys())}")

        return JSONResponse(content={
            'success': True,
            'mensaje': f'Optimización completada. {len(mejores_soluciones)} mejores estrategias encontradas.',
            'top_3_soluciones': mejores_soluciones,
            'historial': resultado.get('historial', []),
            'estadisticas_finales': resultado.get('estadisticas_finales', {}),
        })
        
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error crítico en la optimización: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.get("/metricas/{solucion_id}")
async def obtener_metricas(solucion_id: int):
    """
    Devuelve las métricas de una ejecución de optimización específica
    que han sido guardadas en la caché.
    """
    global cache_metricas
    
    if solucion_id not in cache_metricas:
        # Log para debugging
        logger.warning(f"Métricas solicitadas para solución {solucion_id}, disponibles: {list(cache_metricas.keys())}")
        raise HTTPException(
            status_code=404, 
            detail=f"Métricas no encontradas para solución {solucion_id}. Ejecuta primero la optimización."
        )
    
    return JSONResponse(content={
        "success": True,
        "solucion_id": solucion_id,
        "metricas": cache_metricas[solucion_id]
    })


@router.get("/metricas/{solucion_id}/grafica")
async def obtener_datos_grafica(solucion_id: int):
    """
    ✅ NUEVO ENDPOINT: Devuelve datos procesados para gráficas Chart.js
    Incluye mejor, promedio y peor fitness por generación
    """
    global cache_metricas
    
    if solucion_id not in cache_metricas:
        logger.warning(f"Gráfica solicitada para solución {solucion_id}, disponibles: {list(cache_metricas.keys())}")
        raise HTTPException(
            status_code=404, 
            detail=f"Datos de gráfica no encontrados para solución {solucion_id}. Ejecuta primero la optimización."
        )
    
    try:
        # Obtener datos de visualización procesados
        datos_cache = cache_metricas[solucion_id]
        datos_visualizacion = datos_cache.get('datos_visualizacion', {})
        
        if not datos_visualizacion:
            # Si no hay datos procesados, generar on-the-fly
            historial_basico = datos_cache.get('historial_fitness', [])
            datos_visualizacion = procesar_datos_algoritmo(historial_basico, [])
        
        # Crear visualizador y generar datos para Chart.js
        visualizador = crear_visualizador()
        datos_chartjs = visualizador.generar_datos_chartjs(datos_visualizacion)
        resumen_metricas = visualizador.generar_resumen_metricas(datos_visualizacion)
        
        # ✅ FORMATO ESPECÍFICO PARA TU FRONTEND
        # Extraer datos de la gráfica para formato simplificado
        datos_grafica = datos_visualizacion.get('datos_grafica', [])
        
        if datos_grafica:
            # Generar datos para Chart.js compatible con tu componente
            generaciones = [d['generacion'] for d in datos_grafica]
            fitness_mejor = [d['mejor_fitness'] for d in datos_grafica]
            fitness_promedio = [d['fitness_promedio'] for d in datos_grafica]
            fitness_peor = [d.get('peor_fitness', d['fitness_promedio'] * 0.7) for d in datos_grafica]
            
            # ✅ DATOS EXACTOS PARA TU COMPONENTE MetricsPanel
            datos_para_frontend = {
                'labels': generaciones,
                'datasets': [
                    {
                        'label': 'Fitness Máximo',
                        'data': fitness_mejor,
                        'borderColor': 'rgb(34, 197, 94)',  # Verde
                        'backgroundColor': 'rgba(34, 197, 94, 0.1)',
                        'borderWidth': 2.5,
                        'fill': False,
                        'tension': 0.2,
                        'pointRadius': 0,
                        'pointHoverRadius': 5
                    },
                    {
                        'label': 'Fitness Promedio',
                        'data': fitness_promedio,
                        'borderColor': 'rgb(59, 130, 246)',  # Azul
                        'backgroundColor': 'rgba(59, 130, 246, 0.1)',
                        'borderWidth': 2,
                        'fill': False,
                        'tension': 0.2,
                        'pointRadius': 0,
                        'pointHoverRadius': 5
                    },
                    {
                        'label': 'Fitness Mínimo',
                        'data': fitness_peor,
                        'borderColor': 'rgb(239, 68, 68)',  # Rojo
                        'backgroundColor': 'rgba(239, 68, 68, 0.1)',
                        'borderWidth': 1.5,
                        'borderDash': [5, 5],
                        'fill': False,
                        'tension': 0.2,
                        'pointRadius': 0,
                        'pointHoverRadius': 5
                    }
                ]
            }
        else:
            # Datos vacíos si no hay información
            datos_para_frontend = {
                'labels': [],
                'datasets': []
            }
        
        return JSONResponse(content={
            "success": True,
            "solucion_id": solucion_id,
            "datos_grafica": datos_para_frontend,  # ✅ EXACTO PARA TU Chart.js
            "chartjs_completo": datos_chartjs,     # Datos completos con opciones
            "resumen_metricas": resumen_metricas,  # Métricas adicionales
            "estadisticas": {
                "total_generaciones": len(datos_grafica),
                "fitness_maximo": max(fitness_mejor) if fitness_mejor else 0,
                "fitness_final": fitness_mejor[-1] if fitness_mejor else 0,
                "mejora_porcentual": resumen_metricas.get('rendimiento', {}).get('mejora_porcentual', 0)
            }
        })
        
    except Exception as e:
        logger.error(f"Error generando datos de gráfica para solución {solucion_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail=f"Error interno generando gráfica: {str(e)}"
        )


@router.get("/metricas/general/grafica")
async def obtener_grafica_comparativa():
    """
    ✅ ENDPOINT ADICIONAL: Gráfica comparativa de las 3 soluciones
    Para mostrar todas las soluciones en una sola gráfica
    """
    global cache_metricas
    
    if not cache_metricas:
        raise HTTPException(
            status_code=404, 
            detail="No hay datos disponibles. Ejecuta primero la optimización."
        )
    
    try:
        colores = {
            1: {'border': 'rgb(239, 68, 68)', 'bg': 'rgba(239, 68, 68, 0.1)'},    # Rojo
            2: {'border': 'rgb(34, 197, 94)', 'bg': 'rgba(34, 197, 94, 0.1)'},    # Verde  
            3: {'border': 'rgb(168, 85, 247)', 'bg': 'rgba(168, 85, 247, 0.1)'}   # Púrpura
        }
        
        datasets = []
        
        for solucion_id in [1, 2, 3]:
            if solucion_id in cache_metricas:
                datos_cache = cache_metricas[solucion_id]
                datos_visualizacion = datos_cache.get('datos_visualizacion', {})
                
                if not datos_visualizacion:
                    historial_basico = datos_cache.get('historial_fitness', [])
                    datos_visualizacion = procesar_datos_algoritmo(historial_basico, [])
                
                datos_grafica = datos_visualizacion.get('datos_grafica', [])
                
                if datos_grafica:
                    generaciones = [d['generacion'] for d in datos_grafica]
                    fitness_mejor = [d['mejor_fitness'] for d in datos_grafica]
                    
                    datasets.append({
                        'label': f'Solución {solucion_id}',
                        'data': fitness_mejor,
                        'borderColor': colores[solucion_id]['border'],
                        'backgroundColor': colores[solucion_id]['bg'],
                        'borderWidth': 2,
                        'fill': False,
                        'tension': 0.3,
                        'pointRadius': 0,
                        'pointHoverRadius': 5
                    })
        
        # Usar generaciones de la primera solución disponible
        labels = []
        if cache_metricas:
            primera_solucion = next(iter(cache_metricas.values()))
            datos_viz = primera_solucion.get('datos_visualizacion', {})
            if not datos_viz:
                historial = primera_solucion.get('historial_fitness', [])
                datos_viz = procesar_datos_algoritmo(historial, [])
            
            datos_grafica = datos_viz.get('datos_grafica', [])
            labels = [d['generacion'] for d in datos_grafica]
        
        return JSONResponse(content={
            "success": True,
            "datos_grafica": {
                'labels': labels,
                'datasets': datasets
            },
            "soluciones_incluidas": list(cache_metricas.keys()),
            "tipo": "comparativa_general"
        })
        
    except Exception as e:
        logger.error(f"Error generando gráfica comparativa: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail=f"Error interno: {str(e)}"
        )