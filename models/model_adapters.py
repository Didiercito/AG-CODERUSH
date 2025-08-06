# adapters/model_adapters.py - ADAPTADORES ENTRE BD Y MODELOS COMPLEJOS

from typing import Dict, List, Optional
from database.models import Participante as ParticipanteDB, Problema as ProblemaDB, Asignacion as AsignacionDB
from core.enums import TipoHabilidad, TipoProblema, NivelDificultad
import json

# ============================================================================
# ADAPTADOR PARTICIPANTE: BD Simple ↔ Modelo Complejo
# ============================================================================

def participante_db_to_perfil(participante_db: ParticipanteDB) -> dict:
    """Convierte participante de BD a estructura de PerfilParticipante"""
    
    # Mapear habilidades simples a estructura compleja
    habilidades_complejas = {}
    
    if participante_db.habilidad_algoritmos is not None:
        habilidades_complejas[TipoHabilidad.ALGORITMOS_BASICOS] = {
            "tipo": TipoHabilidad.ALGORITMOS_BASICOS,
            "nivel": participante_db.habilidad_algoritmos / 10.0,  # Convertir escala 0-10 a 0-1
            "experiencia_anos": participante_db.experiencia_competencias or 0,
            "certificaciones": [],
            "proyectos_relevantes": 0
        }
    
    if participante_db.habilidad_estructuras is not None:
        habilidades_complejas[TipoHabilidad.ESTRUCTURAS_DATOS] = {
            "tipo": TipoHabilidad.ESTRUCTURAS_DATOS,
            "nivel": participante_db.habilidad_estructuras / 10.0,
            "experiencia_anos": participante_db.experiencia_competencias or 0,
            "certificaciones": [],
            "proyectos_relevantes": 0
        }
    
    if participante_db.habilidad_matematicas is not None:
        habilidades_complejas[TipoHabilidad.MATEMATICAS] = {
            "tipo": TipoHabilidad.MATEMATICAS,
            "nivel": participante_db.habilidad_matematicas / 10.0,
            "experiencia_anos": participante_db.experiencia_competencias or 0,
            "certificaciones": [],
            "proyectos_relevantes": 0
        }
    
    if participante_db.habilidad_optimizacion is not None:
        habilidades_complejas[TipoHabilidad.OPTIMIZACION] = {
            "tipo": TipoHabilidad.OPTIMIZACION,
            "nivel": participante_db.habilidad_optimizacion / 10.0,
            "experiencia_anos": participante_db.experiencia_competencias or 0,
            "certificaciones": [],
            "proyectos_relevantes": 0
        }
    
    # Mapear lenguaje preferido a habilidad
    if participante_db.lenguaje_preferido:
        lenguaje_enum = mapear_lenguaje_a_enum(participante_db.lenguaje_preferido)
        if lenguaje_enum:
            habilidades_complejas[lenguaje_enum] = {
                "tipo": lenguaje_enum,
                "nivel": participante_db.velocidad_codificacion / 10.0,
                "experiencia_anos": participante_db.experiencia_competencias or 0,
                "certificaciones": [],
                "proyectos_relevantes": 0
            }
    
    return {
        "id": participante_db.id,
        "nombre": participante_db.nombre,
        "email": f"{participante_db.nombre.lower().replace(' ', '.')}@example.com",  # Email generado
        "edad": 22,  # Edad por defecto
        "universidad": "Universidad Tecnológica",  # Universidad por defecto
        "semestre": 6,  # Semestre por defecto
        "habilidades": habilidades_complejas,
        "competencias_participadas": participante_db.experiencia_competencias or 0,
        "problemas_resueltos_total": 0,
        "ranking_promedio": None,
        "tasa_exito_historica": 0.5,
        "tipos_problema_preferidos": [],
        "tipos_problema_evitar": [],
        "tiempo_maximo_disponible": 300,
        "nivel_energia": 0.8,
        "nivel_concentracion": 0.8,
        "disponibilidad": participante_db.disponibilidad
    }

def perfil_to_participante_db(perfil_data: dict) -> dict:
    """Convierte PerfilParticipante a datos para BD simple"""
    
    # Extraer habilidades y convertir a escala 0-10
    habilidades = perfil_data.get("habilidades", {})
    
    habilidad_algoritmos = 0.0
    habilidad_estructuras = 0.0
    habilidad_matematicas = 0.0
    habilidad_optimizacion = 0.0
    velocidad_codificacion = 0.0
    lenguaje_preferido = "python"
    
    for habilidad_tipo, habilidad_data in habilidades.items():
        nivel_0_10 = habilidad_data.get("nivel", 0) * 10.0
        
        if habilidad_tipo == TipoHabilidad.ALGORITMOS_BASICOS:
            habilidad_algoritmos = nivel_0_10
        elif habilidad_tipo == TipoHabilidad.ESTRUCTURAS_DATOS:
            habilidad_estructuras = nivel_0_10
        elif habilidad_tipo == TipoHabilidad.MATEMATICAS:
            habilidad_matematicas = nivel_0_10
        elif habilidad_tipo == TipoHabilidad.OPTIMIZACION:
            habilidad_optimizacion = nivel_0_10
        elif habilidad_tipo in [TipoHabilidad.PYTHON, TipoHabilidad.JAVA, TipoHabilidad.CPP]:
            velocidad_codificacion = nivel_0_10
            lenguaje_preferido = mapear_enum_a_lenguaje(habilidad_tipo)
    
    return {
        "nombre": perfil_data.get("nombre"),
        "habilidad_algoritmos": habilidad_algoritmos,
        "habilidad_estructuras": habilidad_estructuras,
        "habilidad_matematicas": habilidad_matematicas,
        "habilidad_optimizacion": habilidad_optimizacion,
        "velocidad_codificacion": velocidad_codificacion,
        "experiencia_competencias": perfil_data.get("competencias_participadas", 0),
        "lenguaje_preferido": lenguaje_preferido,
        "disponibilidad": perfil_data.get("disponibilidad", True)
    }

# ============================================================================
# ADAPTADOR PROBLEMA: BD Simple ↔ Modelo Complejo
# ============================================================================

def problema_db_to_completo(problema_db: ProblemaDB) -> dict:
    """Convierte problema de BD a estructura de ProblemaCompleto"""
    
    # Mapear dificultad string a enum
    dificultad_enum = mapear_dificultad_string_a_enum(problema_db.dificultad)
    
    # Mapear tipo string a enum
    tipo_enum = mapear_tipo_string_a_enum(problema_db.tipo_problema)
    
    # Construir habilidades requeridas desde campos individuales
    habilidades_requeridas = {}
    
    if problema_db.req_algoritmos and problema_db.req_algoritmos > 0:
        habilidades_requeridas[TipoHabilidad.ALGORITMOS_BASICOS] = problema_db.req_algoritmos / 10.0
    
    if problema_db.req_estructuras and problema_db.req_estructuras > 0:
        habilidades_requeridas[TipoHabilidad.ESTRUCTURAS_DATOS] = problema_db.req_estructuras / 10.0
    
    if problema_db.req_matematicas and problema_db.req_matematicas > 0:
        habilidades_requeridas[TipoHabilidad.MATEMATICAS] = problema_db.req_matematicas / 10.0
    
    if problema_db.req_optimizacion and problema_db.req_optimizacion > 0:
        habilidades_requeridas[TipoHabilidad.OPTIMIZACION] = problema_db.req_optimizacion / 10.0
    
    return {
        "id": problema_db.id,
        "nombre": problema_db.titulo,  # titulo → nombre
        "descripcion": problema_db.descripcion or "",
        "tipo": tipo_enum,
        "nivel_dificultad": dificultad_enum,
        "puntos_base": problema_db.puntuacion_maxima or 100,
        "multiplicador_dificultad": calcular_multiplicador_dificultad(dificultad_enum),
        "bonus_tiempo": 50,
        "habilidades_requeridas": habilidades_requeridas,
        "tiempo_limite": problema_db.tiempo_estimado or 180,
        "memoria_limite": 256,
        "fuente": "Sistema CODERUSH",
        "año_competencia": 2025,
        "tasa_resolucion_historica": 0.5,
        "problemas_prerequisito": [],
        "problemas_relacionados": []
    }

def completo_to_problema_db(problema_data: dict) -> dict:
    """Convierte ProblemaCompleto a datos para BD simple"""
    
    # Extraer habilidades requeridas y convertir a campos individuales
    habilidades = problema_data.get("habilidades_requeridas", {})
    
    req_algoritmos = 0.0
    req_estructuras = 0.0
    req_matematicas = 0.0
    req_optimizacion = 0.0
    
    for habilidad_tipo, nivel in habilidades.items():
        nivel_0_10 = nivel * 10.0
        
        if habilidad_tipo == TipoHabilidad.ALGORITMOS_BASICOS:
            req_algoritmos = nivel_0_10
        elif habilidad_tipo == TipoHabilidad.ESTRUCTURAS_DATOS:
            req_estructuras = nivel_0_10
        elif habilidad_tipo == TipoHabilidad.MATEMATICAS:
            req_matematicas = nivel_0_10
        elif habilidad_tipo == TipoHabilidad.OPTIMIZACION:
            req_optimizacion = nivel_0_10
    
    return {
        "titulo": problema_data.get("nombre"),
        "descripcion": problema_data.get("descripcion"),
        "dificultad": mapear_enum_a_dificultad_string(problema_data.get("nivel_dificultad")),
        "tipo_problema": mapear_enum_a_tipo_string(problema_data.get("tipo")),
        "puntuacion_maxima": problema_data.get("puntos_base", 100),
        "tiempo_estimado": problema_data.get("tiempo_limite", 180),
        "req_algoritmos": req_algoritmos,
        "req_estructuras": req_estructuras,
        "req_matematicas": req_matematicas,
        "req_optimizacion": req_optimizacion,
        "lenguajes_permitidos": "python,java,cpp",
        "activo": True
    }

# ============================================================================
# FUNCIONES DE MAPEO
# ============================================================================

def mapear_lenguaje_a_enum(lenguaje: str) -> Optional[TipoHabilidad]:
    """Mapea string de lenguaje a enum TipoHabilidad"""
    mapeo = {
        "python": TipoHabilidad.PYTHON,
        "java": TipoHabilidad.JAVA,
        "cpp": TipoHabilidad.CPP,
        "c++": TipoHabilidad.CPP,
        "javascript": TipoHabilidad.JAVASCRIPT
    }
    return mapeo.get(lenguaje.lower())

def mapear_enum_a_lenguaje(enum_habilidad: TipoHabilidad) -> str:
    """Mapea enum TipoHabilidad a string de lenguaje"""
    mapeo = {
        TipoHabilidad.PYTHON: "python",
        TipoHabilidad.JAVA: "java",
        TipoHabilidad.CPP: "cpp",
        TipoHabilidad.JAVASCRIPT: "javascript"
    }
    return mapeo.get(enum_habilidad, "python")

def mapear_dificultad_string_a_enum(dificultad: str) -> NivelDificultad:
    """Mapea string de dificultad a enum NivelDificultad"""
    mapeo = {
        "muy_facil": NivelDificultad.MUY_FACIL,
        "facil": NivelDificultad.FACIL,
        "medio": NivelDificultad.MEDIO,
        "dificil": NivelDificultad.DIFICIL,
        "muy_dificil": NivelDificultad.MUY_DIFICIL
    }
    return mapeo.get(dificultad, NivelDificultad.MEDIO)

def mapear_enum_a_dificultad_string(enum_dificultad: NivelDificultad) -> str:
    """Mapea enum NivelDificultad a string de dificultad"""
    mapeo = {
        NivelDificultad.MUY_FACIL: "muy_facil",
        NivelDificultad.FACIL: "facil",
        NivelDificultad.MEDIO: "medio",
        NivelDificultad.DIFICIL: "dificil",
        NivelDificultad.MUY_DIFICIL: "muy_dificil"
    }
    return mapeo.get(enum_dificultad, "medio")

def mapear_tipo_string_a_enum(tipo: str) -> TipoProblema:
    """Mapea string de tipo a enum TipoProblema"""
    mapeo = {
        "algoritmo": TipoProblema.ALGORITMOS,
        "algoritmos": TipoProblema.ALGORITMOS,
        "estructuras": TipoProblema.ESTRUCTURAS_DATOS,
        "estructuras_datos": TipoProblema.ESTRUCTURAS_DATOS,
        "grafos": TipoProblema.GRAFOS,
        "matematicas": TipoProblema.MATEMATICAS,
        "geometria": TipoProblema.GEOMETRIA_COMPUTACIONAL,
        "programacion_dinamica": TipoProblema.PROGRAMACION_DINAMICA,
        "strings": TipoProblema.STRINGS,
        "simulacion": TipoProblema.SIMULACION
    }
    return mapeo.get(tipo, TipoProblema.ALGORITMOS)

def mapear_enum_a_tipo_string(enum_tipo: TipoProblema) -> str:
    """Mapea enum TipoProblema a string de tipo"""
    mapeo = {
        TipoProblema.ALGORITMOS: "algoritmo",
        TipoProblema.ESTRUCTURAS_DATOS: "estructuras",
        TipoProblema.GRAFOS: "grafos",
        TipoProblema.MATEMATICAS: "matematicas",
        TipoProblema.GEOMETRIA_COMPUTACIONAL: "geometria",
        TipoProblema.PROGRAMACION_DINAMICA: "programacion_dinamica",
        TipoProblema.STRINGS: "strings",
        TipoProblema.SIMULACION: "simulacion"
    }
    return mapeo.get(enum_tipo, "algoritmo")

def calcular_multiplicador_dificultad(dificultad: NivelDificultad) -> float:
    """Calcula multiplicador de dificultad basado en el nivel"""
    mapeo = {
        NivelDificultad.MUY_FACIL: 1.0,
        NivelDificultad.FACIL: 1.2,
        NivelDificultad.MEDIO: 1.5,
        NivelDificultad.DIFICIL: 2.0,
        NivelDificultad.MUY_DIFICIL: 2.5
    }
    return mapeo.get(dificultad, 1.5)