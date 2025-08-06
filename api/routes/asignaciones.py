# api/routes/asignaciones.py - CORREGIDO TOP 3 soluciones

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
import logging
import time
import traceback
import numpy as np

# Importar TUS modelos existentes - usando los nombres correctos de tu schemas.py
from models.schemas import (
    ConfiguracionCompetencia,
    AsignacionRequest
)
from core.algoritmo_genetico import AlgoritmoGenetico  # ← Tu adaptador modificado
from core.evaluador import EvaluadorAsignacion
                

logger = logging.getLogger(__name__)

# ============================================================================
# CREAR ROUTER DE FASTAPI
# ============================================================================
router = APIRouter()

# ============================================================================
# MODELOS DE REQUEST PARA LOS ENDPOINTS (usando tus modelos existentes)
# ============================================================================

from pydantic import BaseModel, Field
from typing import List, Dict, Any

# Modelos simples para participantes y problemas (compatibles con tu estructura)
class ParticipanteRequest(BaseModel):
    id: int
    nombre: str
    habilidades: Dict[str, Any] = Field(default_factory=dict)
    experiencia: float = Field(default=0.5, ge=0.0, le=1.0)
    tasa_exito_historica: float = Field(default=0.5, ge=0.0, le=1.0)
    disponibilidad: bool = Field(default=True)
    competencias_participadas: int = Field(default=0, ge=0)
    tipos_problema_preferidos: List[str] = Field(default_factory=list)
    tipos_problema_evitar: List[str] = Field(default_factory=list)
    tiempo_maximo_disponible: int = Field(default=300, ge=1)
    nivel_energia: float = Field(default=0.8, ge=0.0, le=1.0)
    nivel_concentracion: float = Field(default=0.8, ge=0.0, le=1.0)

class ProblemaRequest(BaseModel):
    id: int
    nombre: str
    tipo: str = Field(default="general")
    nivel_dificultad: str = Field(default="medio")
    puntos_base: int = Field(default=100, ge=1)
    tiempo_limite: int = Field(default=120, ge=1)
    multiplicador_dificultad: float = Field(default=1.0, ge=0.1)
    habilidades_requeridas: Dict[str, float] = Field(default_factory=dict)
    tasa_resolucion_historica: float = Field(default=0.5, ge=0.0, le=1.0)

class RequestOptimizacion(BaseModel):
    participantes: List[ParticipanteRequest]
    problemas: List[ProblemaRequest]
    configuracion: Optional[ConfiguracionCompetencia] = None

class RequestComparacion(BaseModel):
    participantes: List[ParticipanteRequest]
    problemas: List[ProblemaRequest]
    configuracion: Optional[ConfiguracionCompetencia] = None

class RequestSeleccionSolucion(BaseModel):
    participantes: List[ParticipanteRequest]
    problemas: List[ProblemaRequest]
    solucion_numero: int = Field(ge=1, le=3)
    configuracion: Optional[ConfiguracionCompetencia] = None

# ============================================================================
# ENDPOINT DE COMPATIBILIDAD CON FRONTEND EXISTENTE
# ============================================================================

@router.post("/asignar")
async def asignar_compatibilidad(request: dict):
    """
    Endpoint de COMPATIBILIDAD con tu frontend existente
    Mantiene la misma estructura de request/response que espera tu frontend
    """
    try:
        logger.info("🚀 Endpoint de compatibilidad /asignar activado...")
        
        # Extraer datos del request (formato antiguo)
        problemas_data = request.get('problemas', [])
        participantes_data = request.get('participantes', [])
        config_data = request.get('configuracion_competencia', {})
        params_ag = request.get('parametros_ag', {})
        
        logger.info(f"📊 Datos compatibilidad: {len(participantes_data)} participantes, {len(problemas_data)} problemas")
        
        # Validaciones básicas
        if not participantes_data or not problemas_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Debe proporcionar al menos un participante y un problema"
            )
        
        if len(problemas_data) > len(participantes_data):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No puede haber más problemas que participantes"
            )
        
        # Configurar parámetros del algoritmo (compatibilidad con formato antiguo)
        parametros_algoritmo = {
            'poblacion_size': params_ag.get('poblacion_size', 50),
            'generaciones': params_ag.get('generaciones_max', 100),
            'tasa_mutacion': params_ag.get('prob_mutacion', 0.15),
            'tasa_cruce': params_ag.get('prob_cruce', 0.8),
            'torneo_size': 5
        }
        
        # Crear evaluador
        evaluador = EvaluadorAsignacion()
        
        # Crear y configurar algoritmo genético
        algoritmo = AlgoritmoGenetico(
            participantes=participantes_data,
            problemas=problemas_data,
            evaluador=evaluador,
            **parametros_algoritmo
        )
        
        # Ejecutar algoritmo
        logger.info("🏃 Ejecutando algoritmo genético (modo compatibilidad)...")
        mejor_solucion, fitness_final, estadisticas = algoritmo.ejecutar()
        
        # Generar resumen compatible
        resumen_asignacion = algoritmo.generar_resumen_asignacion(mejor_solucion)
        
        # Crear cronograma compatible con tu frontend
        cronograma = []
        tiempo_total_calculado = 0  # Para calcular el tiempo correcto
        
        for asignacion in resumen_asignacion:
            tiempo_estimado = asignacion.get('tiempo_estimado', 120)
            cronograma.append({
                'problema_id': asignacion.get('problema_id', 0),
                'problema_nombre': asignacion.get('problema_nombre', 'Problema'),
                'participante_id': asignacion.get('participante_id', 0),
                'participante_nombre': asignacion.get('participante_nombre', 'Participante'),
                'prioridad': asignacion.get('prioridad', 1),
                'compatibilidad': asignacion.get('compatibilidad', 0.5),
                'probabilidad_exito': asignacion.get('probabilidad_exito', 0.5),
                'tiempo_estimado': tiempo_estimado,
                'puntos_esperados': asignacion.get('puntos_esperados', 100)
            })
            # Para competencias, el tiempo total es el máximo (trabajan en paralelo)
            tiempo_total_calculado = max(tiempo_total_calculado, tiempo_estimado)
        
        # Si no hay asignaciones, usar suma (fallback)
        if tiempo_total_calculado == 0 and cronograma:
            tiempo_total_calculado = sum(c['tiempo_estimado'] for c in cronograma)
        
        # Respuesta compatible con tu frontend existente
        respuesta_compatible = {
            'exito': True,
            'mensaje': 'Asignación completada exitosamente',
            'fitness_final': fitness_final,
            'tiempo_ejecucion': estadisticas.get('tiempo_ejecucion', 0),
            'es_solucion_valida': True,
            
            # Estructura que espera tu frontend
            'optimizacion': {
                'fitness_final': fitness_final,
                'tiempo_total_estimado_minutos': tiempo_total_calculado,  # CORREGIDO: usar tiempo calculado
                'puntuacion_total_esperada': estadisticas.get('puntuacion_total', 0),
                'compatibilidad_promedio': estadisticas.get('compatibilidad_promedio', 0),
                'eficiencia_predicha': estadisticas.get('eficiencia', 0)
            },
            
            'cronograma': cronograma,
            
            'algoritmo': {
                'generaciones_ejecutadas': estadisticas.get('generaciones_ejecutadas', 0),
                'poblacion_size': parametros_algoritmo['poblacion_size'],
                'tiempo_ejecucion_segundos': estadisticas.get('tiempo_ejecucion', 0)
            },
            
            'equipo': {
                'participantes_utilizados': len(set(c['participante_id'] for c in cronograma)),
                'total_participantes': len(participantes_data),
                'total_problemas': len(problemas_data),
                'todos_asignados': len(cronograma) == len(problemas_data)
            },
            
            # Estadísticas adicionales
            'estadisticas': {
                'generaciones_ejecutadas': estadisticas.get('generaciones_ejecutadas', 0),
                'tiempo_ejecucion': estadisticas.get('tiempo_ejecucion', 0),
                'fitness_componentes': estadisticas.get('fitness_componentes', {}),
                'puntuacion_total': estadisticas.get('puntuacion_total', 0),
                'tiempo_total': estadisticas.get('tiempo_total', 0),
                'compatibilidad_promedio': estadisticas.get('compatibilidad_promedio', 0),
                'eficiencia': estadisticas.get('eficiencia', 0),
                'evolucion_fitness': estadisticas.get('evolucion_fitness', [])
            },
            
            'matriz_asignacion': mejor_solucion,
            'asignaciones_detalle': resumen_asignacion
        }
        
        logger.info("✅ Respuesta de compatibilidad generada exitosamente")
        logger.info(f"🎯 Fitness: {fitness_final:.3f}, Asignaciones: {len(cronograma)}")
        
        return JSONResponse(content=respuesta_compatible, status_code=200)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error en endpoint de compatibilidad: {e}")
        logger.error(f"📍 Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )


# 2. MODIFICA tu endpoint /optimizar en api/routes/asignaciones.py

@router.post("/optimizar")
async def optimizar_asignaciones(request: RequestOptimizacion):
    """
    Endpoint CORREGIDO que respeta configuración de equipo y elimina N/A
    """
    try:
        logger.info("🚀 Iniciando optimización con TOP 3 soluciones...")
        
        # Convertir modelos Pydantic a diccionarios
        participantes_originales = [participante.dict() for participante in request.participantes]
        problemas_originales = [problema.dict() for problema in request.problemas]
        
        logger.info(f"📊 Datos recibidos: {len(participantes_originales)} participantes, {len(problemas_originales)} problemas")
        
        # ✅ NUEVO: Obtener configuración de tamaño de equipo
        tamanio_equipo_config = None
        if request.configuracion:
            configuracion = request.configuracion.dict()
            tamanio_equipo_config = configuracion.get('tamanio_equipo')
        
        # ✅ CORREGIDO: Aplicar configuración de competencia - RESPETAR EL TAMAÑO DEL EQUIPO
        if tamanio_equipo_config and tamanio_equipo_config < len(participantes_originales):
            logger.info(f"🎯 Tamaño de equipo configurado: {tamanio_equipo_config} (de {len(participantes_originales)} disponibles)")
            
            # Seleccionar los mejores participantes según tasa de éxito
            participantes_con_score = []
            for p in participantes_originales:
                score = p.get('tasa_exito_historica', 0.5) + (p.get('experiencia', 0) * 0.3)
                participantes_con_score.append((score, p))
            
            # Ordenar y seleccionar los mejores
            participantes_con_score.sort(key=lambda x: x[0], reverse=True)
            participantes_seleccionados = [p[1] for p in participantes_con_score[:tamanio_equipo_config]]
            
            logger.info(f"👥 Participantes seleccionados: {len(participantes_seleccionados)} de {len(participantes_originales)}")
        else:
            participantes_seleccionados = participantes_originales
            tamanio_equipo_config = len(participantes_originales)
        
        # ✅ CORREGIDO: Si hay más problemas que participantes seleccionados, seleccionar los más importantes
        if len(problemas_originales) > len(participantes_seleccionados):
            logger.info(f"🎯 Seleccionando {len(participantes_seleccionados)} problemas más importantes de {len(problemas_originales)}")
            
            # Ordenar problemas por puntos
            problemas_con_score = []
            for p in problemas_originales:
                puntos = p.get('puntos_base', 100) * p.get('multiplicador_dificultad', 1.0)
                problemas_con_score.append((puntos, p))
            
            problemas_con_score.sort(key=lambda x: x[0], reverse=True)
            problemas_seleccionados = [p[1] for p in problemas_con_score[:len(participantes_seleccionados)]]
        else:
            problemas_seleccionados = problemas_originales
        
        logger.info(f"🎯 Tamaño de equipo objetivo: {len(participantes_seleccionados)}")
        logger.info(f"📋 Problemas a asignar: {len(problemas_seleccionados)}")
        
        # Validaciones básicas
        if not participantes_seleccionados or not problemas_seleccionados:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Debe haber al menos un participante y un problema seleccionado"
            )
        
        # Configurar parámetros del algoritmo
        if request.configuracion:
            configuracion = request.configuracion.dict()
        else:
            configuracion = {}
            
        parametros_algoritmo = {
            'poblacion_size': configuracion.get('poblacion_size', 100),
            'generaciones': configuracion.get('generaciones', 150),  
            'tasa_mutacion': configuracion.get('tasa_mutacion', 0.15),
            'tasa_cruce': configuracion.get('tasa_cruce', 0.8),
            'torneo_size': configuracion.get('torneo_size', 5)
        }
        
        # Crear evaluador
        logger.info("🔧 Creando evaluador...")
        evaluador = EvaluadorAsignacion()
        
        # ✅ USAR EL ALGORITMO CORREGIDO con los participantes/problemas seleccionados
        from core.algoritmo_genetico import AlgoritmoGeneticoCoderush
        
        algoritmo_corregido = AlgoritmoGeneticoCoderush(
            problemas=problemas_seleccionados,
            participantes=participantes_seleccionados,
            tamanio_equipo=len(participantes_seleccionados),  # ✅ USAR EL TAMAÑO CORRECTO
            **parametros_algoritmo
        )
        
        # Ejecutar optimización
        logger.info("🏃 Ejecutando optimización TOP 3...")
        resultado_optimizacion = algoritmo_corregido.ejecutar()
        
        if not resultado_optimizacion['exito']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se pudo generar una solución válida"
            )
        
        # ✅ CORREGIR ESTADÍSTICAS EN CADA SOLUCIÓN
        top_3_corregidas = []
        
        for idx, solucion in enumerate(resultado_optimizacion['top_3_soluciones']):
            asignaciones = solucion.get('asignaciones_detalle', [])
            
            if asignaciones:
                # ✅ CALCULAR ESTADÍSTICAS REALES (SIN N/A)
                try:
                    puntuacion_total = sum(
                        float(a.get('puntuacion_esperada', 0)) 
                        for a in asignaciones 
                        if a.get('puntuacion_esperada') is not None
                    )
                    
                    tiempo_total = sum(
                        int(a.get('tiempo_estimado', 120)) 
                        for a in asignaciones 
                        if a.get('tiempo_estimado') is not None
                    )
                    
                    compatibilidades = [
                        float(a.get('compatibilidad', 0.6)) 
                        for a in asignaciones 
                        if a.get('compatibilidad') is not None and not np.isnan(float(a.get('compatibilidad', 0.6)))
                    ]
                    
                    compatibilidad_promedio = np.mean(compatibilidades) * 100 if compatibilidades else 60.0
                    
                    # ✅ ACTUALIZAR ESTADÍSTICAS CON VALORES REALES
                    solucion['estadisticas_solucion'].update({
                        'puntuacion_total_esperada': round(puntuacion_total, 2),
                        'tiempo_total_estimado': int(tiempo_total),
                        'compatibilidad_promedio': round(compatibilidad_promedio, 1),
                        'problemas_asignados': len(asignaciones),
                        'participantes_utilizados': len(set(a.get('participante_id') for a in asignaciones)),
                        'eficiencia_asignacion': len(asignaciones) / max(len(problemas_seleccionados), 1)
                    })
                    
                    logger.info(f"  🥇 Solución {idx+1} CORREGIDA: fitness={solucion['fitness']:.6f}, puntuación={puntuacion_total:.1f}, tiempo={tiempo_total}, compatibilidad={compatibilidad_promedio:.1f}%")
                    
                except Exception as e:
                    logger.error(f"Error corrigiendo estadísticas de solución {idx+1}: {e}")
                    # Valores por defecto seguros
                    solucion['estadisticas_solucion'].update({
                        'puntuacion_total_esperada': 0,
                        'tiempo_total_estimado': len(asignaciones) * 120,
                        'compatibilidad_promedio': 60.0,
                        'problemas_asignados': len(asignaciones),
                        'participantes_utilizados': len(set(a.get('participante_id') for a in asignaciones)),
                        'eficiencia_asignacion': len(asignaciones) / max(len(problemas_seleccionados), 1)
                    })
            
            top_3_corregidas.append(solucion)
        
        # ✅ TAMBIÉN CORREGIR LA MEJOR SOLUCIÓN
        mejor_solucion = resultado_optimizacion['mejor_solucion']
        asignaciones_mejor = mejor_solucion.get('asignaciones_detalle', [])
        
        if asignaciones_mejor:
            try:
                puntuacion_mejor = sum(float(a.get('puntuacion_esperada', 0)) for a in asignaciones_mejor)
                tiempo_mejor = sum(int(a.get('tiempo_estimado', 120)) for a in asignaciones_mejor)
                compatibilidades_mejor = [
                    float(a.get('compatibilidad', 0.6)) 
                    for a in asignaciones_mejor 
                    if not np.isnan(float(a.get('compatibilidad', 0.6)))
                ]
                compatibilidad_mejor = np.mean(compatibilidades_mejor) * 100 if compatibilidades_mejor else 60.0
                
                mejor_solucion['estadisticas_solucion'].update({
                    'puntuacion_total_esperada': round(puntuacion_mejor, 2),
                    'tiempo_total_estimado': int(tiempo_mejor),
                    'compatibilidad_promedio': round(compatibilidad_mejor, 1),
                    'problemas_asignados': len(asignaciones_mejor),
                    'participantes_utilizados': len(set(a.get('participante_id') for a in asignaciones_mejor))
                })
                
            except Exception as e:
                logger.error(f"Error corrigiendo mejor solución: {e}")
        
        # ✅ PREPARAR RESPUESTA COMPLETA CORREGIDA
        respuesta = {
            'success': True,
            'mensaje': f'Optimización TOP 3 completada con {len(participantes_seleccionados)} participantes y {len(problemas_seleccionados)} problemas',
            'timestamp': time.time(),
            
            # ✨ COMPATIBILIDAD: Datos de la mejor solución (formato original)
            'matriz_asignacion': mejor_solucion['matriz_asignacion'],
            'fitness_final': mejor_solucion['fitness'],
            'estadisticas': {
                'generaciones_ejecutadas': resultado_optimizacion['estadisticas_globales']['generaciones_ejecutadas'],
                'tiempo_ejecucion': resultado_optimizacion['estadisticas_globales']['tiempo_ejecucion_segundos'],
                'fitness_componentes': mejor_solucion.get('fitness_componentes', {}),
                'puntuacion_total': mejor_solucion['estadisticas_solucion']['puntuacion_total_esperada'],
                'tiempo_total': mejor_solucion['estadisticas_solucion']['tiempo_total_estimado'],
                'compatibilidad_promedio': mejor_solucion['estadisticas_solucion']['compatibilidad_promedio'],
                'eficiencia': mejor_solucion['fitness'],
                'evolucion_fitness': [],  # Se puede agregar si necesitas el historial
                'diversidad_total': resultado_optimizacion['estadisticas_globales'].get('diversidad_total', 0)
            },
            'asignaciones_detalle': mejor_solucion['asignaciones_detalle'],
            'resumen_asignacion': mejor_solucion['asignaciones_detalle'],
            
            # ✨ NUEVO: TOP 3 SOLUCIONES CORREGIDAS
            'top_3_soluciones': {
                f'solucion_{i+1}': {
                    'ranking': i + 1,
                    'estrategia': f'Solución {i + 1}',
                    'descripcion': f'Solución optimizada #{i + 1}',
                    'matriz_asignacion': sol['matriz_asignacion'],
                    'fitness': sol['fitness'],
                    'fitness_componentes': sol.get('fitness_componentes', {}),
                    'estadisticas': sol['estadisticas_solucion'],
                    'asignaciones_detalle': sol['asignaciones_detalle']
                } for i, sol in enumerate(top_3_corregidas[:3])
            },
            
            # ✨ INFORMACIÓN DE CONFIGURACIÓN APLICADA
            'configuracion_aplicada': {
                'tamanio_equipo_solicitado': tamanio_equipo_config,
                'participantes_originales': len(participantes_originales),
                'participantes_seleccionados': len(participantes_seleccionados),
                'problemas_originales': len(problemas_originales),
                'problemas_seleccionados': len(problemas_seleccionados),
                'seleccion_aplicada': tamanio_equipo_config < len(participantes_originales),
                'razon_seleccion': f'Configuración de competencia limitó equipo a {tamanio_equipo_config}' if tamanio_equipo_config < len(participantes_originales) else 'Se usaron todos los participantes'
            },
            
            # ✨ ESTADÍSTICAS DEL ALGORITMO
            'estadisticas_algoritmo': resultado_optimizacion['estadisticas_globales'],
            
            # ✨ INFORMACIÓN ADICIONAL
            'info_adicional': {
                'tipo_resultado': 'top_3_soluciones_con_configuracion_respetada',
                'num_soluciones_evaluadas': resultado_optimizacion['num_soluciones_obtenidas'],
                'algoritmo_version': 'CODERUSH_TOP_3_Fixed',
                'valores_na_eliminados': True,
                'duplicados_eliminados': True,
                'configuracion_equipo_respetada': True
            }
        }
        
        # ✅ RELLENAR SOLUCIONES FALTANTES CON None SI HAY MENOS DE 3
        for i in range(len(top_3_corregidas), 3):
            respuesta['top_3_soluciones'][f'solucion_{i+1}'] = None
        
        # ✅ ANÁLISIS COMPARATIVO
        respuesta['analisis_comparativo'] = {
            'solucion_recomendada': 1,
            'razon': f'Mejor fitness de {len(top_3_corregidas)} soluciones generadas',
            'confianza': 'alta' if len(top_3_corregidas) >= 2 else 'media',
            'diferencias_significativas': len(set(round(sol['fitness'], 4) for sol in top_3_corregidas)) > 1,
            'num_soluciones_obtenidas': len(top_3_corregidas)
        }
        
        logger.info("✅ Optimización TOP 3 completada exitosamente")
        logger.info(f"🥇 Mejor fitness: {mejor_solucion['fitness']:.6f}")
        logger.info(f"📊 Soluciones generadas: {len(top_3_corregidas)}")
        logger.info(f"👥 Configuración respetada: {len(participantes_seleccionados)} participantes, {len(problemas_seleccionados)} problemas")
        
        return JSONResponse(content=respuesta, status_code=200)
        
    except HTTPException:
        raise
    except ValueError as ve:
        logger.error(f"❌ Error de validación: {ve}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error de validación: {str(ve)}"
        )
    except Exception as e:
        logger.error(f"❌ Error en optimización TOP 3: {e}")
        logger.error(f"📍 Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )

        
def _generar_recomendacion_solucion(top_3_resultados, estadisticas_generales):
    try:
        if len(top_3_resultados) == 0:
            return {"mensaje": "No se obtuvieron soluciones válidas"}
        
        solucion_1 = top_3_resultados[0]
        
        if len(top_3_resultados) == 1:
            return {
                'solucion_recomendada': 1,
                'razon': 'Solo se obtuvo una solución válida',
                'confianza': 'baja',
                'num_soluciones_obtenidas': 1
            }
        
        # Analizar diferencias entre soluciones
        fitness_diff_1_2 = solucion_1.get('fitness', 0) - top_3_resultados[1].get('fitness', 0)
        diversidad = estadisticas_generales.get('diversidad_entre_soluciones', {}).get('diversidad_promedio', 0)
        
        if fitness_diff_1_2 > 0.1:  # Diferencia significativa
            return {
                'solucion_recomendada': 1,
                'razon': 'La primera solución es significativamente mejor que las demás',
                'confianza': 'alta',
                'diferencia_fitness': fitness_diff_1_2,
                'alternativa': 'Usar solución 1 directamente',
                'num_soluciones_obtenidas': len(top_3_resultados)
            }
        elif fitness_diff_1_2 < 0.05:  # Soluciones muy similares
            return {
                'solucion_recomendada': 'multiple',
                'razon': 'Las soluciones tienen fitness muy similar, considerar factores adicionales',
                'confianza': 'media',
                'diferencia_fitness': fitness_diff_1_2,
                'alternativa': 'Evaluar compatibilidad con preferencias del equipo o restricciones adicionales',
                'num_soluciones_obtenidas': len(top_3_resultados)
            }
        else:  # Diferencia moderada
            return {
                'solucion_recomendada': 1,
                'razon': 'La primera solución es moderadamente mejor',
                'confianza': 'media',
                'diferencia_fitness': fitness_diff_1_2,
                'alternativa': 'Considerar solución 2 si hay restricciones adicionales',
                'num_soluciones_obtenidas': len(top_3_resultados)
            }
            
    except Exception as e:
        logger.debug(f"Error generando recomendación: {e}")
        return {
            'solucion_recomendada': 1,
            'razon': 'Usar primera solución por defecto',
            'confianza': 'baja',
            'num_soluciones_obtenidas': len(top_3_resultados) if top_3_resultados else 0
        }


# ============================================================================
# RESTO DE ENDPOINTS (sin cambios importantes)
# ============================================================================

@router.post("/comparar-soluciones")
async def comparar_soluciones_detallado(request: RequestComparacion):
    """
    Endpoint para obtener análisis comparativo MUY detallado de las TOP 3 soluciones
    """
    try:
        logger.info("🔍 Iniciando análisis comparativo detallado...")
        
        # Convertir modelos Pydantic a diccionarios
        participantes = [participante.dict() for participante in request.participantes]
        problemas = [problema.dict() for problema in request.problemas]
        if request.configuracion:
            configuracion = request.configuracion.dict()
        else:
            configuracion = {
                'poblacion_size': 150,
                'generaciones': 200,
                'tasa_mutacion': 0.12,
                'tasa_cruce': 0.85
            }
        
        if not participantes or not problemas:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Debe proporcionar participantes y problemas"
            )
        
        # Configurar parámetros para análisis más exhaustivo
        parametros_analisis = {
            'poblacion_size': configuracion.get('poblacion_size', 150),
            'generaciones': configuracion.get('generaciones', 200),
            'tasa_mutacion': configuracion.get('tasa_mutacion', 0.12),
            'tasa_cruce': configuracion.get('tasa_cruce', 0.85)
        }
        
        # Ejecutar algoritmo
        evaluador = EvaluadorAsignacion()
        algoritmo = AlgoritmoGenetico(
            participantes=participantes,
            problemas=problemas,
            evaluador=evaluador,
            **parametros_analisis
        )
        
        mejor_solucion, fitness_final, estadisticas = algoritmo.ejecutar()
        top_3_resultados = estadisticas.get('top_3_soluciones', [])
        
        if len(top_3_resultados) < 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No se pudieron obtener suficientes soluciones para comparar. Solo se obtuvieron {len(top_3_resultados)} soluciones"
            )
        
        # Análisis comparativo detallado
        analisis_detallado = _realizar_analisis_comparativo_detallado(
            top_3_resultados, participantes, problemas
        )
        
        respuesta_comparativa = {
            'success': True,
            'mensaje': 'Análisis comparativo detallado completado',
            'timestamp': time.time(),
            'num_soluciones_analizadas': len(top_3_resultados),
            
            # Análisis detallado
            'analisis_comparativo': analisis_detallado,
            
            # Recomendaciones estratégicas
            'recomendaciones_estrategicas': _generar_recomendaciones_estrategicas(
                analisis_detallado, estadisticas
            ),
            
            # Datos de las soluciones
            'soluciones_detalle': top_3_resultados,
            'estadisticas_algoritmo': estadisticas
        }
        
        logger.info("✅ Análisis comparativo detallado completado")
        return JSONResponse(content=respuesta_comparativa, status_code=200)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error en análisis comparativo: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en análisis: {str(e)}"
        )


def _realizar_analisis_comparativo_detallado(top_3_resultados, participantes, problemas):
    """
    Realiza análisis comparativo detallado entre las soluciones
    """
    try:
        analisis = {
            'metricas_fitness': {},
            'distribucion_cargas': {},
            'compatibilidad_analisis': {},
            'riesgos_y_oportunidades': {},
            'flexibilidad_estrategica': {}
        }
        
        # Análisis de fitness
        fitness_values = [sol.get('fitness', 0) for sol in top_3_resultados]
        analisis['metricas_fitness'] = {
            'rango_fitness': max(fitness_values) - min(fitness_values) if fitness_values else 0,
            'coeficiente_variacion': np.std(fitness_values) / np.mean(fitness_values) if np.mean(fitness_values) > 0 else 0,
            'convergencia_calidad': 'alta' if (max(fitness_values) - min(fitness_values)) < 0.1 else 'media'
        }
        
        # Análisis de distribución de cargas
        cargas_por_solucion = []
        for sol in top_3_resultados:
            estadisticas_sol = sol.get('estadisticas', {})
            asignaciones = estadisticas_sol.get('asignaciones_detalle', [])
            participantes_con_carga = {}
            
            for asig in asignaciones:
                pid = asig.get('participante_id', 0)
                if pid not in participantes_con_carga:
                    participantes_con_carga[pid] = 0
                participantes_con_carga[pid] += asig.get('tiempo_estimado', 0)
            
            cargas_por_solucion.append(participantes_con_carga)
        
        # Calcular balance de carga
        balances = []
        for cargas in cargas_por_solucion:
            if cargas:
                tiempos = list(cargas.values())
                balance = np.std(tiempos) / np.mean(tiempos) if np.mean(tiempos) > 0 else 0
                balances.append(balance)
        
        analisis['distribucion_cargas'] = {
            'balance_promedio': np.mean(balances) if balances else 0,
            'solucion_mas_balanceada': np.argmin(balances) + 1 if balances else 1,
            'diferencia_balance': max(balances) - min(balances) if len(balances) > 1 else 0
        }
        
        # Análisis de compatibilidad
        compatibilidades = []
        for sol in top_3_resultados:
            estadisticas_sol = sol.get('estadisticas', {})
            comp_prom = estadisticas_sol.get('compatibilidad_promedio', 0)
            compatibilidades.append(comp_prom)
        
        analisis['compatibilidad_analisis'] = {
            'mejor_compatibilidad': max(compatibilidades) if compatibilidades else 0,
            'solucion_mejor_compatibilidad': np.argmax(compatibilidades) + 1 if compatibilidades else 1,
            'rango_compatibilidad': max(compatibilidades) - min(compatibilidades) if len(compatibilidades) > 1 else 0
        }
        
        # Análisis de riesgos
        riesgos = []
        for i, sol in enumerate(top_3_resultados):
            estadisticas_sol = sol.get('estadisticas', {})
            asignaciones = estadisticas_sol.get('asignaciones_detalle', [])
            
            # Calcular riesgo como problemas con baja compatibilidad
            problemas_riesgo = sum(1 for asig in asignaciones if asig.get('compatibilidad', 1.0) < 0.6)
            prob_exito_baja = sum(1 for asig in asignaciones if asig.get('probabilidad_exito', 1.0) < 0.5)
            
            riesgo_total = (problemas_riesgo + prob_exito_baja) / max(len(asignaciones), 1)
            riesgos.append(riesgo_total)
        
        analisis['riesgos_y_oportunidades'] = {
            'solucion_menor_riesgo': np.argmin(riesgos) + 1 if riesgos else 1,
            'riesgo_promedio': np.mean(riesgos) if riesgos else 0,
            'nivel_riesgo': 'bajo' if np.mean(riesgos) < 0.3 else 'medio' if np.mean(riesgos) < 0.6 else 'alto'
        }
        
        return analisis
        
    except Exception as e:
        logger.debug(f"Error en análisis detallado: {e}")
        return {
            'error': 'No se pudo completar el análisis detallado',
            'metricas_fitness': {},
            'distribucion_cargas': {},
            'compatibilidad_analisis': {},
            'riesgos_y_oportunidades': {}
        }


def _generar_recomendaciones_estrategicas(analisis_detallado, estadisticas_generales):
    """
    Genera recomendaciones estratégicas basadas en el análisis
    """
    try:
        recomendaciones = {
            'estrategia_principal': '',
            'estrategia_alternativa': '',
            'consideraciones_especiales': [],
            'metricas_clave': {}
        }
        
        # Determinar estrategia principal
        fitness_convergencia = analisis_detallado.get('metricas_fitness', {}).get('convergencia_calidad', 'media')
        riesgo_nivel = analisis_detallado.get('riesgos_y_oportunidades', {}).get('nivel_riesgo', 'medio')
        
        if fitness_convergencia == 'alta' and riesgo_nivel == 'bajo':
            recomendaciones['estrategia_principal'] = "Usar solución 1 - Alta confianza en resultados"
            recomendaciones['estrategia_alternativa'] = "Cualquiera de las 3 soluciones es viable"
        elif riesgo_nivel == 'alto':
            solucion_menor_riesgo = analisis_detallado.get('riesgos_y_oportunidades', {}).get('solucion_menor_riesgo', 1)
            recomendaciones['estrategia_principal'] = f"Usar solución {solucion_menor_riesgo} - Menor riesgo"
            recomendaciones['estrategia_alternativa'] = "Considerar capacitación adicional para problemas de alta dificultad"
        else:
            recomendaciones['estrategia_principal'] = "Usar solución 1 - Mejor balance general"
            recomendaciones['estrategia_alternativa'] = "Evaluar solución 2 si hay restricciones adicionales"
        
        # Consideraciones especiales
        balance_dif = analisis_detallado.get('distribucion_cargas', {}).get('diferencia_balance', 0)
        if balance_dif > 0.3:
            recomendaciones['consideraciones_especiales'].append(
                "Considerar redistribución manual para mejor balance de carga"
            )
        
        comp_rango = analisis_detallado.get('compatibilidad_analisis', {}).get('rango_compatibilidad', 0)
        if comp_rango > 0.2:
            recomendaciones['consideraciones_especiales'].append(
                "Hay diferencias significativas en compatibilidad entre soluciones"
            )
        
        return recomendaciones
        
    except Exception as e:
        logger.debug(f"Error generando recomendaciones estratégicas: {e}")
        return {
            'estrategia_principal': 'Usar solución 1',
            'estrategia_alternativa': 'Evaluar manualmente',
            'consideraciones_especiales': [],
            'metricas_clave': {}
        }


# ============================================================================
# RESTO DE ENDPOINTS
# ============================================================================

@router.post("/seleccionar-solucion")
async def seleccionar_solucion_especifica(request: RequestSeleccionSolucion):
    """
    Endpoint para obtener detalles de una solución específica del TOP 3
    """
    try:
        logger.info("🎯 Seleccionando solución específica...")
        
        # Convertir modelos Pydantic a diccionarios
        participantes = [participante.dict() for participante in request.participantes]
        problemas = [problema.dict() for problema in request.problemas]
        if request.configuracion:
            configuracion = request.configuracion.dict()
        else:
            configuracion = {
                'poblacion_size': 100,
                'generaciones': 150,
                'tasa_mutacion': 0.15,
                'tasa_cruce': 0.8,
                'torneo_size': 5
            }
        solucion_deseada = request.solucion_numero
        
        if not participantes or not problemas:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Debe proporcionar participantes y problemas"
            )
        
        # Ejecutar algoritmo para obtener TOP 3
        parametros_algoritmo = {
            'poblacion_size': configuracion.get('poblacion_size', 100),
            'generaciones': configuracion.get('generaciones', 150),
            'tasa_mutacion': configuracion.get('tasa_mutacion', 0.15),
            'tasa_cruce': configuracion.get('tasa_cruce', 0.8),
            'torneo_size': configuracion.get('torneo_size', 5)
        }
        
        evaluador = EvaluadorAsignacion()
        algoritmo = AlgoritmoGenetico(
            participantes=participantes,
            problemas=problemas,
            evaluador=evaluador,
            **parametros_algoritmo
        )
        
        mejor_solucion, fitness_final, estadisticas = algoritmo.ejecutar()
        top_3_resultados = estadisticas.get('top_3_soluciones', [])
        
        # Verificar que tengamos la solución solicitada
        if len(top_3_resultados) < solucion_deseada:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Solo se obtuvieron {len(top_3_resultados)} soluciones, no se puede devolver la solución {solucion_deseada}"
            )
        
        # Obtener la solución específica (índice = número - 1)
        solucion_seleccionada = top_3_resultados[solucion_deseada - 1]
        
        # Generar resumen de la solución seleccionada
        resumen_seleccionado = algoritmo.generar_resumen_asignacion(
            solucion_seleccionada.get('matriz_asignacion', mejor_solucion)
        )
        
        # Calcular estadísticas de la posición de esta solución respecto a las otras
        posicion_stats = {
            'es_la_mejor': solucion_deseada == 1,
            'diferencia_con_mejor': solucion_seleccionada.get('fitness', 0) - top_3_resultados[0].get('fitness', 0),
            'posicion_ranking': solucion_deseada,
            'total_soluciones': len(top_3_resultados)
        }
        
        respuesta_solucion = {
            'success': True,
            'mensaje': f'Solución {solucion_deseada} seleccionada exitosamente',
            'timestamp': time.time(),
            
            # Datos de la solución seleccionada en formato completo
            'matriz_asignacion': solucion_seleccionada.get('matriz_asignacion', mejor_solucion),
            'fitness_final': solucion_seleccionada.get('fitness', fitness_final),
            'estadisticas': {
                'generaciones_ejecutadas': estadisticas.get('generaciones_ejecutadas', 0),
                'tiempo_ejecucion': estadisticas.get('tiempo_ejecucion', 0),
                'fitness_componentes': solucion_seleccionada.get('estadisticas', {}).get('fitness_componentes', {}),
                'puntuacion_total': solucion_seleccionada.get('estadisticas', {}).get('puntuacion_total_esperada', 0),
                'tiempo_total': solucion_seleccionada.get('estadisticas', {}).get('tiempo_total_estimado', 0),
                'compatibilidad_promedio': solucion_seleccionada.get('estadisticas', {}).get('compatibilidad_promedio', 0),
                'eficiencia': solucion_seleccionada.get('estadisticas', {}).get('compatibilidad_promedio', 0),
                'evolucion_fitness': estadisticas.get('evolucion_fitness', [])
            },
            'asignaciones_detalle': solucion_seleccionada.get('estadisticas', {}).get('asignaciones_detalle', []),
            'resumen_asignacion': resumen_seleccionado,
            
            # Información sobre la posición de esta solución
            'posicion_en_ranking': posicion_stats,
            
            # Comparación con las otras soluciones
            'comparacion_con_otras': {
                'num_total_soluciones': len(top_3_resultados),
                'fitness_todas': [sol.get('fitness', 0) for sol in top_3_resultados],
                'es_significativamente_diferente': abs(posicion_stats['diferencia_con_mejor']) > 0.05,
                'recomendacion_uso': 'altamente_recomendada' if solucion_deseada == 1 else 'viable' if abs(posicion_stats['diferencia_con_mejor']) < 0.1 else 'evaluar_cuidadosamente'
            },
            
            # Información adicional
            'info_adicional': {
                'solucion_numero': solucion_deseada,
                'tipo_resultado': 'solucion_especifica',
                'algoritmo_version': 'TOP_3_Enhanced'
            }
        }
        
        logger.info(f"✅ Solución {solucion_deseada} seleccionada exitosamente")
        logger.info(f"🎯 Fitness de solución seleccionada: {solucion_seleccionada.get('fitness', 0):.3f}")
        
        return JSONResponse(content=respuesta_solucion, status_code=200)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error seleccionando solución específica: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error seleccionando solución: {str(e)}"
        )


# ============================================================================
# ENDPOINTS ADICIONALES
# ============================================================================

@router.get("/info-sistema")
async def obtener_info_sistema():
    """
    Endpoint para obtener información sobre las capacidades del sistema
    """
    try:
        info_sistema = {
            'version': 'CODERUSH TOP 3 Enhanced v1.0',
            'capacidades': {
                'top_3_soluciones': True,
                'diversidad_garantizada': True,
                'analisis_comparativo': True,
                'recomendaciones_inteligentes': True,
                'seleccion_solucion_especifica': True,
                'compatibilidad_frontend': True
            },
            'endpoints_disponibles': {
                '/asignar': {
                    'descripcion': 'Endpoint de compatibilidad con frontend existente',
                    'metodo': 'POST',
                    'incluye': ['respuesta_compatible', 'mejor_solucion']
                },
                '/optimizar': {
                    'descripcion': 'Endpoint principal - devuelve TOP 3 soluciones con compatibilidad hacia atrás',
                    'metodo': 'POST',
                    'incluye': ['mejor_solucion', 'top_3_soluciones', 'analisis_comparativo']
                },
                '/comparar-soluciones': {
                    'descripcion': 'Análisis comparativo detallado entre las TOP 3 soluciones',
                    'metodo': 'POST',
                    'incluye': ['analisis_detallado', 'recomendaciones_estrategicas']
                },
                '/seleccionar-solucion': {
                    'descripcion': 'Obtener detalles de una solución específica (1, 2 o 3)',
                    'metodo': 'POST',
                    'incluye': ['solucion_especifica', 'comparacion_con_otras']
                },
                '/info-sistema': {
                    'descripcion': 'Información sobre las capacidades del sistema',
                    'metodo': 'GET',
                    'incluye': ['version', 'capacidades', 'endpoints']
                }
            },
            'algoritmo_genetico': {
                'elite_archive': True,
                'diversidad_control': True,
                'estrategias_inicializacion': ['aleatorio', 'greedy_compatibilidad', 'greedy_puntuacion', 'hibrido'],
                'operadores_geneticos': ['seleccion_torneo', 'cruce_uniforme_inteligente', 'mutacion_adaptativa'],
                'criterios_parada': ['generaciones_max', 'convergencia', 'fitness_objetivo']
            },
            'metricas_disponibles': [
                'fitness_general',
                'compatibilidad_promedio',
                'puntuacion_total_esperada',
                'tiempo_total_estimado',
                'diversidad_entre_soluciones',
                'balance_de_carga',
                'analisis_de_riesgos'
            ],
            'timestamp': time.time()
        }
        
        return JSONResponse(content=info_sistema, status_code=200)
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo info del sistema: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo información: {str(e)}"
        )


@router.get("/estadisticas")
async def obtener_estadisticas_sistema():
    """
    Endpoint para obtener estadísticas generales del sistema
    """
    try:
        estadisticas = {
            'sistema': 'CODERUSH TOP 3',
            'version': '1.0.0',
            'algoritmo': {
                'tipo': 'Genético Avanzado con Elite Archive',
                'diversidad_garantizada': True,
                'soluciones_simultaneas': 3,
                'estrategias_inicializacion': 4,
                'operadores_geneticos': 3
            },
            'configuracion_recomendada': {
                'poblacion_size': {
                    'minimo': 50,
                    'recomendado': 100,
                    'maximo': 500,
                    'descripcion': 'Tamaño de la población para el algoritmo genético'
                },
                'generaciones': {
                    'minimo': 50,
                    'recomendado': 150,
                    'maximo': 1000,
                    'descripcion': 'Número máximo de generaciones a ejecutar'
                },
                'tasa_mutacion': {
                    'minimo': 0.01,
                    'recomendado': 0.15,
                    'maximo': 0.5,
                    'descripcion': 'Probabilidad de mutación por individuo'
                },
                'tasa_cruce': {
                    'minimo': 0.1,
                    'recomendado': 0.8,
                    'maximo': 1.0,
                    'descripcion': 'Probabilidad de cruce entre padres'
                }
            },
            'metricas_evaluacion': [
                'fitness_general',
                'puntuacion_esperada',
                'compatibilidad_promedio',
                'tiempo_estimado',
                'balance_de_carga',
                'diversidad_soluciones'
            ],
            'timestamp': time.time(),
            'status': 'operativo'
        }
        
        return JSONResponse(content=estadisticas, status_code=200)
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo estadísticas: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo estadísticas: {str(e)}"
        )


@router.post("/validar-datos")
async def validar_datos_entrada(request: RequestOptimizacion):
    try:
        logger.info("🔍 Validando datos de entrada...")
        
        participantes = [participante.dict() for participante in request.participantes]
        problemas = [problema.dict() for problema in request.problemas]
        if request.configuracion:
            configuracion = request.configuracion.dict()
        else:
            configuracion = {
                'poblacion_size': 100,
                'generaciones': 150,
                'tasa_mutacion': 0.15,
                'tasa_cruce': 0.8,
                'torneo_size': 5
            }
        
        errores = []
        advertencias = []
        
        # Validaciones básicas
        if not participantes:
            errores.append("No se proporcionaron participantes")
        if not problemas:
            errores.append("No se proporcionaron problemas")
        if len(problemas) > len(participantes):
            errores.append("No puede haber más problemas que participantes")
        
        # Validaciones de participantes
        for i, participante in enumerate(participantes):
            if not participante.get('nombre'):
                advertencias.append(f"Participante {i+1} no tiene nombre")
            if not participante.get('habilidades'):
                advertencias.append(f"Participante {i+1} no tiene habilidades definidas")
            
            experiencia = participante.get('experiencia', 0.5)
            if experiencia < 0 or experiencia > 1:
                errores.append(f"Participante {i+1}: experiencia debe estar entre 0 y 1")
        
        # Validaciones de problemas
        for i, problema in enumerate(problemas):
            if not problema.get('nombre'):
                advertencias.append(f"Problema {i+1} no tiene nombre")
            if problema.get('puntos_base', 0) <= 0:
                errores.append(f"Problema {i+1}: puntos_base debe ser mayor a 0")
            if problema.get('tiempo_limite', 0) <= 0:
                errores.append(f"Problema {i+1}: tiempo_limite debe ser mayor a 0")
        
        # Validaciones de configuración
        if configuracion.get('poblacion_size', 0) < 10:
            advertencias.append("Población muy pequeña, se recomienda al menos 50")
        if configuracion.get('generaciones', 0) < 20:
            advertencias.append("Pocas generaciones, se recomienda al menos 50")
        
        # Calcular complejidad estimada
        complejidad = len(participantes) * len(problemas)
        tiempo_estimado = complejidad * configuracion.get('generaciones', 150) / 1000  # Estimación aproximada
        
        resultado_validacion = {
            'valido': len(errores) == 0,
            'errores': errores,
            'advertencias': advertencias,
            'estadisticas_entrada': {
                'num_participantes': len(participantes),
                'num_problemas': len(problemas),
                'ratio_problemas_participantes': len(problemas) / len(participantes) if participantes else 0,
                'complejidad_estimada': complejidad,
                'tiempo_ejecucion_estimado_segundos': tiempo_estimado
            },
            'recomendaciones': [],
            'timestamp': time.time()
        }
        
        if complejidad > 1000:
            resultado_validacion['recomendaciones'].append("Problema complejo detectado - considerar aumentar población y generaciones")
        if len(participantes) > 50:
            resultado_validacion['recomendaciones'].append("Muchos participantes - el algoritmo puede tardar más tiempo")
        if tiempo_estimado > 30:
            resultado_validacion['recomendaciones'].append(f"Tiempo estimado de ejecución: {tiempo_estimado:.1f} segundos - considerar reducir parámetros")
        
        if len(errores) == 0:
            resultado_validacion['mensaje'] = "Datos válidos - listos para optimización"
            status_code = 200
        else:
            resultado_validacion['mensaje'] = f"Se encontraron {len(errores)} errores que deben corregirse"
            status_code = 400
        
        logger.info(f"✅ Validación completada: {len(errores)} errores, {len(advertencias)} advertencias")
        
        return JSONResponse(content=resultado_validacion, status_code=status_code)
        
    except Exception as e:
        logger.error(f"❌ Error en validación: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en validación: {str(e)}"
        )