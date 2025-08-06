# api/routes/sistema.py
"""
Rutas para gestión del sistema y datos de ejemplo
✅ CON PROTECCIÓN CONTRA GENERACIÓN AUTOMÁTICA
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from database.database import get_db_session
from database.crud import crud_participante, crud_problema
from api.dependencies import respuesta_exito, respuesta_error
from datetime import datetime

router = APIRouter()

@router.post("/generar-datos-ejemplo", tags=["sistema"])
async def generar_datos_ejemplo(
    forzar_generacion: bool = Query(False, description="Forzar generación aunque ya existan datos"),
    db: Session = Depends(get_db_session)
):
    """
    Genera datos de ejemplo optimizados para competencias de programación competitiva
    
    ✅ PROTECCIÓN CONTRA GENERACIÓN AUTOMÁTICA:
    - Por defecto NO genera si ya hay datos
    - Requiere forzar_generacion=true para sobrescribir
    
    Tiempos ajustados: Fácil(30-45min), Medio(60-75min), Difícil(90-120min)
    """
    try:
        print("🎯 Solicitud de generación de datos de ejemplo...")
        
        # ✅ VERIFICAR SI YA EXISTEN DATOS
        if not forzar_generacion:
            from database.models import Participante, Problema
            total_participantes = db.query(Participante).count()
            total_problemas = db.query(Problema).count()
            
            if total_participantes > 0 or total_problemas > 0:
                return respuesta_error(
                    f"⚠️ Ya existen datos en la base de datos "
                    f"({total_participantes} participantes, {total_problemas} problemas). "
                    f"Usa ?forzar_generacion=true para sobrescribir o "
                    f"llama a /api/limpiar-datos primero.",
                    codigo_error="DATOS_EXISTENTES"
                )
        
        print("🎲 ✅ GENERANDO datos de ejemplo para competencias de programación...")
        
        # ================================================================
        # PARTICIPANTES DE EJEMPLO
        # ================================================================
        participantes_ejemplo = [
            {
                "nombre": "Ana García",
                "email": "ana.garcia@example.com",
                "edad": 22,
                "universidad": "Universidad Tecnológica",
                "semestre": 6,
                "habilidades": {
                    "algoritmos_basicos": {"nivel": 0.8, "experiencia_anos": 2, "proyectos": 3},
                    "python": {"nivel": 0.9, "experiencia_anos": 3, "proyectos": 5}
                },
                "competencias_participadas": 5,
                "problemas_resueltos_total": 15,
                "tasa_exito_historica": 0.75,
                "tipos_problema_preferidos": ["algoritmos"],
                "tipos_problema_evitar": [],
                "tiempo_maximo_disponible": 180,
                "nivel_energia": 0.85,
                "nivel_concentracion": 0.9,
                "disponibilidad": True
            },
            {
                "nombre": "Carlos López",
                "email": "carlos.lopez@example.com", 
                "edad": 24,
                "universidad": "Instituto Politécnico",
                "semestre": 8,
                "habilidades": {
                    "estructuras_datos": {"nivel": 0.85, "experiencia_anos": 2.5, "proyectos": 4},
                    "java": {"nivel": 0.8, "experiencia_anos": 2, "proyectos": 6}
                },
                "competencias_participadas": 8,
                "problemas_resueltos_total": 22,
                "tasa_exito_historica": 0.68,
                "tipos_problema_preferidos": ["estructuras_datos"],
                "tipos_problema_evitar": [],
                "tiempo_maximo_disponible": 180,
                "nivel_energia": 0.8,
                "nivel_concentracion": 0.85,
                "disponibilidad": True
            },
            {
                "nombre": "María Rodriguez",
                "email": "maria.rodriguez@example.com",
                "edad": 23,
                "universidad": "Universidad Nacional", 
                "semestre": 7,
                "habilidades": {
                    "matematicas": {"nivel": 0.95, "experiencia_anos": 4, "proyectos": 8},
                    "optimizacion": {"nivel": 0.88, "experiencia_anos": 1.5, "proyectos": 3}
                },
                "competencias_participadas": 12,
                "problemas_resueltos_total": 35,
                "tasa_exito_historica": 0.82,
                "tipos_problema_preferidos": ["matematicas"],
                "tipos_problema_evitar": [],
                "tiempo_maximo_disponible": 180,
                "nivel_energia": 0.9,
                "nivel_concentracion": 0.95,
                "disponibilidad": True
            },
            {
                "nombre": "Diego Fernández",
                "email": "diego.fernandez@example.com",
                "edad": 25,
                "universidad": "Universidad de Ingeniería",
                "semestre": 9,
                "habilidades": {
                    "grafos": {"nivel": 0.92, "experiencia_anos": 3, "proyectos": 7},
                    "cpp": {"nivel": 0.88, "experiencia_anos": 4, "proyectos": 9}
                },
                "competencias_participadas": 15,
                "problemas_resueltos_total": 45,
                "tasa_exito_historica": 0.78,
                "tipos_problema_preferidos": ["grafos", "algoritmos"],
                "tipos_problema_evitar": ["simulacion"],
                "tiempo_maximo_disponible": 180,
                "nivel_energia": 0.88,
                "nivel_concentracion": 0.92,
                "disponibilidad": True
            },
            {
                "nombre": "Sofia Martínez",
                "email": "sofia.martinez@example.com",
                "edad": 20,
                "universidad": "Instituto Tecnológico",
                "semestre": 4,
                "habilidades": {
                    "programacion_dinamica": {"nivel": 0.75, "experiencia_anos": 1, "proyectos": 2},
                    "javascript": {"nivel": 0.85, "experiencia_anos": 2.5, "proyectos": 6}
                },
                "competencias_participadas": 3,
                "problemas_resueltos_total": 8,
                "tasa_exito_historica": 0.6,
                "tipos_problema_preferidos": ["strings", "programacion_dinamica"],
                "tipos_problema_evitar": ["matematicas"],
                "tiempo_maximo_disponible": 150,
                "nivel_energia": 0.9,
                "nivel_concentracion": 0.85,
                "disponibilidad": True
            }
        ]
        
        # ================================================================
        # PROBLEMAS DE EJEMPLO - TIEMPOS OPTIMIZADOS PARA COMPETENCIAS
        # ================================================================
        problemas_ejemplo = [
            {
                "nombre": "Ordenamiento Burbuja Optimizado",
                "descripcion": "Implementar algoritmo de ordenamiento burbuja con optimizaciones para casos especiales",
                "tipo": "algoritmos",
                "nivel_dificultad": "facil",
                "puntos_base": 100,
                "multiplicador_dificultad": 1.2,
                "bonus_tiempo": 50,
                "habilidades_requeridas": {
                    "algoritmos_basicos": 0.6,
                    "python": 0.5
                },
                "tiempo_limite": 45,
                "memoria_limite": 256,
                "fuente": "CODERUSH",
                "año_competencia": 2025,
                "tasa_resolucion_historica": 0.75,
                "url_problema": "https://example.com/problema1",
                "tags": ["sorting", "algorithms", "optimization"],
                "problemas_prerequisito": [],
                "problemas_relacionados": []
            },
            {
                "nombre": "Árbol Binario de Búsqueda Balanceado",
                "descripcion": "Implementar operaciones CRUD en un árbol binario de búsqueda autobalanceado",
                "tipo": "estructuras_datos",
                "nivel_dificultad": "medio",
                "puntos_base": 200,
                "multiplicador_dificultad": 1.5,
                "bonus_tiempo": 75,
                "habilidades_requeridas": {
                    "estructuras_datos": 0.8,
                    "algoritmos_basicos": 0.6
                },
                "tiempo_limite": 75,
                "memoria_limite": 512,
                "fuente": "CODERUSH",
                "año_competencia": 2025,
                "tasa_resolucion_historica": 0.45,
                "url_problema": "https://example.com/problema2",
                "tags": ["trees", "data_structures", "balanced"],
                "problemas_prerequisito": [],
                "problemas_relacionados": []
            },
            {
                "nombre": "Optimización de Ruta con Restricciones",
                "descripcion": "Encontrar la ruta óptima en un grafo con múltiples restricciones usando programación lineal",
                "tipo": "optimizacion",
                "nivel_dificultad": "dificil",
                "puntos_base": 300,
                "multiplicador_dificultad": 2.0,
                "bonus_tiempo": 100,
                "habilidades_requeridas": {
                    "optimizacion": 0.85,
                    "matematicas": 0.7,
                    "algoritmos_basicos": 0.6
                },
                "tiempo_limite": 120,
                "memoria_limite": 1024,
                "fuente": "CODERUSH",
                "año_competencia": 2025,
                "tasa_resolucion_historica": 0.25,
                "url_problema": "https://example.com/problema3",
                "tags": ["optimization", "linear_programming", "constraints"],
                "problemas_prerequisito": [],
                "problemas_relacionados": []
            },
            {
                "nombre": "Detección de Ciclos en Grafo Dirigido",
                "descripcion": "Implementar algoritmo para detectar ciclos en un grafo dirigido usando DFS",
                "tipo": "grafos",
                "nivel_dificultad": "medio",
                "puntos_base": 180,
                "multiplicador_dificultad": 1.6,
                "bonus_tiempo": 60,
                "habilidades_requeridas": {
                    "grafos": 0.8,
                    "algoritmos_basicos": 0.7,
                    "cpp": 0.6
                },
                "tiempo_limite": 75,
                "memoria_limite": 512,
                "fuente": "CODERUSH",
                "año_competencia": 2025,
                "tasa_resolucion_historica": 0.55,
                "url_problema": "https://example.com/problema4",
                "tags": ["graphs", "dfs", "cycles"],
                "problemas_prerequisito": [],
                "problemas_relacionados": []
            },
            {
                "nombre": "Subsequencia Común Más Larga",
                "descripcion": "Encontrar la subsequencia común más larga entre dos cadenas usando programación dinámica",
                "tipo": "programacion_dinamica",
                "nivel_dificultad": "medio",
                "puntos_base": 160,
                "multiplicador_dificultad": 1.4,
                "bonus_tiempo": 70,
                "habilidades_requeridas": {
                    "programacion_dinamica": 0.75,
                    "algoritmos_basicos": 0.6,
                    "strings": 0.5
                },
                "tiempo_limite": 60,
                "memoria_limite": 256,
                "fuente": "CODERUSH",
                "año_competencia": 2025,
                "tasa_resolucion_historica": 0.5,
                "url_problema": "https://example.com/problema5",
                "tags": ["dynamic_programming", "strings", "lcs"],
                "problemas_prerequisito": [],
                "problemas_relacionados": []
            }
        ]
        
        # ================================================================
        # INSERTAR DATOS
        # ================================================================
        participantes_creados = []
        problemas_creados = []
        
        print("👥 Creando participantes...")
        for participante_data in participantes_ejemplo:
            try:
                participante = crud_participante.create(db, participante_data)
                participantes_creados.append(participante)
                print(f"   ✅ {participante.nombre} creado")
            except Exception as e:
                print(f"   ❌ Error creando {participante_data['nombre']}: {e}")
        
        print("🧩 Creando problemas...")
        for problema_data in problemas_ejemplo:
            try:
                problema = crud_problema.create(db, problema_data)
                problemas_creados.append(problema)
                print(f"   ✅ {problema.nombre} creado ({problema.tiempo_limite} min)")
            except Exception as e:
                print(f"   ❌ Error creando {problema_data['nombre']}: {e}")
        
        # ================================================================
        # ESTADÍSTICAS FINALES
        # ================================================================
        tiempo_total_equipo = sum(p.tiempo_limite for p in problemas_creados)
        tiempo_promedio = tiempo_total_equipo / len(problemas_creados) if problemas_creados else 0
        
        return respuesta_exito(
            "🎯 Datos de ejemplo generados exitosamente MANUALMENTE para competencias de programación",
            {
                "modo_generacion": "MANUAL_SOLICITADO",
                "forzar_generacion": forzar_generacion,
                "participantes_creados": len(participantes_creados),
                "problemas_creados": len(problemas_creados),
                "estadisticas_tiempo": {
                    "tiempo_total_equipo_minutos": tiempo_total_equipo,
                    "tiempo_total_equipo_horas": round(tiempo_total_equipo / 60, 1),
                    "tiempo_promedio_por_problema": round(tiempo_promedio, 0),
                    "distribucion_tiempos": {
                        "facil": "45 min",
                        "medio": "60-75 min", 
                        "dificil": "120 min"
                    }
                },
                "participantes": [
                    {
                        "id": p.id,
                        "nombre": p.nombre,
                        "universidad": p.universidad,
                        "tasa_exito": p.tasa_exito_historica,
                        "tiempo_max_disponible": p.tiempo_maximo_disponible
                    } for p in participantes_creados
                ],
                "problemas": [
                    {
                        "id": p.id,
                        "nombre": p.nombre,
                        "tipo": p.tipo,
                        "dificultad": p.nivel_dificultad,
                        "tiempo_limite": p.tiempo_limite,
                        "puntos_totales": p.puntos_base * p.multiplicador_dificultad
                    } for p in problemas_creados
                ],
                "recomendacion": f"Tiempo total optimizado: {tiempo_total_equipo} min ({round(tiempo_total_equipo/60, 1)}h) - Ideal para competencias de programación de 5-7 horas",
                "proteccion_automatica": "✅ Datos generados solo por solicitud manual"
            }
        )
        
    except Exception as e:
        print(f"❌ Error generando datos de ejemplo: {e}")
        raise respuesta_error(f"Error generando datos de ejemplo: {str(e)}")

@router.delete("/limpiar-datos", tags=["sistema"])
async def limpiar_datos(confirmar: bool = False, db: Session = Depends(get_db_session)):
    """
    Limpia todos los datos de la base de datos
    ⚠️ ADVERTENCIA: Esta acción es irreversible
    """
    if not confirmar:
        raise respuesta_error(
            "Debes confirmar la acción agregando ?confirmar=true a la URL. "
            "⚠️ ADVERTENCIA: Esto borrará TODOS los datos de manera irreversible."
        )
    
    try:
        from database.models import Participante, Problema, Asignacion
        from sqlalchemy import text
        
        # Contar datos antes de borrar
        total_participantes = db.query(Participante).count()
        total_problemas = db.query(Problema).count()
        total_asignaciones = db.query(Asignacion).count()
        
        # Borrar todos los datos usando text() para SQL raw
        db.execute(text("DELETE FROM asignaciones"))
        db.execute(text("DELETE FROM participantes")) 
        db.execute(text("DELETE FROM problemas"))
        
        # Reiniciar secuencias
        db.execute(text("ALTER SEQUENCE participantes_id_seq RESTART WITH 1"))
        db.execute(text("ALTER SEQUENCE problemas_id_seq RESTART WITH 1"))
        db.execute(text("ALTER SEQUENCE asignaciones_id_seq RESTART WITH 1"))
        
        db.commit()
        
        return respuesta_exito(
            "🗑️ Base de datos limpiada exitosamente",
            {
                "datos_eliminados": {
                    "participantes": total_participantes,
                    "problemas": total_problemas,
                    "asignaciones": total_asignaciones
                },
                "secuencias_reiniciadas": ["participantes_id_seq", "problemas_id_seq", "asignaciones_id_seq"],
                "estado": "Base de datos completamente limpia y lista para nuevos datos",
                "modo_operacion": "CSV_MANUAL_READY"
            }
        )
        
    except Exception as e:
        db.rollback()
        raise respuesta_error(f"Error limpiando base de datos: {str(e)}")

@router.get("/estadisticas-sistema", tags=["sistema"])
async def estadisticas_sistema(db: Session = Depends(get_db_session)):
    """Obtiene estadísticas generales del sistema"""
    try:
        from database.models import Participante, Problema, Asignacion
        from sqlalchemy import text, func
        
        # Contar registros
        total_participantes = db.query(Participante).count()
        participantes_disponibles = db.query(Participante).filter(Participante.disponibilidad == True).count()
        total_problemas = db.query(Problema).count()
        total_asignaciones = db.query(Asignacion).count()
        
        # Estadísticas de problemas
        if total_problemas > 0:
            tiempo_total = db.query(func.sum(Problema.tiempo_limite)).scalar() or 0
            tiempo_promedio = db.query(func.avg(Problema.tiempo_limite)).scalar() or 0
        else:
            tiempo_total = 0
            tiempo_promedio = 0
        
        return respuesta_exito(
            "Estadísticas del sistema obtenidas",
            {
                "participantes": {
                    "total": total_participantes,
                    "disponibles": participantes_disponibles,
                    "porcentaje_disponibles": round((participantes_disponibles / total_participantes * 100) if total_participantes > 0 else 0, 1)
                },
                "problemas": {
                    "total": total_problemas,
                    "tiempo_total_minutos": int(tiempo_total),
                    "tiempo_total_horas": round(tiempo_total / 60, 1),
                    "tiempo_promedio_por_problema": round(tiempo_promedio, 0)
                },
                "asignaciones": {
                    "total": total_asignaciones
                },
                "sistema": {
                    "ratio_problemas_participantes": round(total_problemas / total_participantes, 2) if total_participantes > 0 else 0,
                    "estado": "Operativo" if total_participantes > 0 and total_problemas > 0 else "Necesita datos",
                    "modo_operacion": "CSV_MANUAL",
                    "datos_automaticos": False,
                    "timestamp": datetime.now().isoformat()
                },
                "instrucciones": {
                    "cargar_datos": "Usa POST /api/generar-datos-ejemplo o carga CSV desde frontend",
                    "limpiar_datos": "Usa DELETE /api/limpiar-datos?confirmar=true",
                    "ejecutar_algoritmo": "POST /api/asignar después de tener datos"
                }
            }
        )
        
    except Exception as e:
        raise respuesta_error(f"Error obteniendo estadísticas: {str(e)}")

@router.get("/verificar-datos", tags=["sistema"])
async def verificar_datos(db: Session = Depends(get_db_session)):
    """
    ✅ ENDPOINT NUEVO: Verificar si existen datos en la base de datos
    Útil para el frontend para decidir si mostrar mensaje de "sin datos"
    """
    try:
        from database.models import Participante, Problema, Asignacion
        
        # Contar datos existentes
        total_participantes = db.query(Participante).count()
        total_problemas = db.query(Problema).count()
        total_asignaciones = db.query(Asignacion).count()
        
        tiene_datos = total_participantes > 0 or total_problemas > 0
        
        return respuesta_exito(
            "Verificación de datos completada",
            {
                "tiene_datos": tiene_datos,
                "contadores": {
                    "participantes": total_participantes,
                    "problemas": total_problemas,
                    "asignaciones": total_asignaciones
                },
                "estado_bd": "CON_DATOS" if tiene_datos else "VACIA",
                "modo_operacion": "CSV_MANUAL",
                "datos_automaticos": False,
                "recomendacion": "Listo para usar" if tiene_datos else "Carga datos desde CSV o genera datos de ejemplo"
            }
        )
        
    except Exception as e:
        raise respuesta_error(f"Error verificando datos: {str(e)}")

# ============================================================================
# ENDPOINTS DE INFORMACIÓN ADICIONALES
# ============================================================================

@router.get("/modo-operacion", tags=["sistema"])
async def modo_operacion():
    """
    ✅ ENDPOINT NUEVO: Información sobre el modo de operación del sistema
    """
    return respuesta_exito(
        "Información del modo de operación",
        {
            "modo": "CSV_MANUAL",
            "descripcion": "Sistema configurado para carga manual de datos",
            "caracteristicas": {
                "generacion_automatica": False,
                "carga_csv": True,
                "generacion_manual": True,
                "limpieza_datos": True
            },
            "endpoints_disponibles": {
                "generar_datos": "POST /api/generar-datos-ejemplo?forzar_generacion=true",
                "limpiar_datos": "DELETE /api/limpiar-datos?confirmar=true",
                "verificar_datos": "GET /api/verificar-datos",
                "estadisticas": "GET /api/estadisticas-sistema"
            },
            "instrucciones": [
                "1. Carga datos desde CSV en el frontend",
                "2. O usa POST /api/generar-datos-ejemplo para datos de prueba",
                "3. Ejecuta POST /api/asignar para obtener asignaciones optimizadas",
                "4. Usa DELETE /api/limpiar-datos para empezar de nuevo"
            ],
            "protecciones": [
                "No genera datos automáticamente al iniciar",
                "Requiere confirmación para generar si ya existen datos",
                "Requiere confirmación para limpiar datos",
                "Validación de parámetros en todos los endpoints"
            ]
        }
    )