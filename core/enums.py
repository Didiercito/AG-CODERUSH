from enum import Enum

class TipoProblema(str, Enum):
    ALGORITMOS = "algoritmos"
    ESTRUCTURAS_DATOS = "estructuras_datos"
    MATEMATICAS = "matematicas"
    GRAFOS = "grafos"
    DINAMICA = "programacion_dinamica"
    GEOMETRIA = "geometria_computacional"
    STRINGS = "procesamiento_strings"
    SIMULACION = "simulacion"

class NivelDificultad(str, Enum):
    MUY_FACIL = "muy_facil"      # 0.1-0.2
    FACIL = "facil"              # 0.3-0.4
    MEDIO = "medio"              # 0.5-0.6
    DIFICIL = "dificil"          # 0.7-0.8
    MUY_DIFICIL = "muy_dificil"  # 0.9-1.0

class TipoHabilidad(str, Enum):
    # Habilidades técnicas
    ALGORITMOS_BASICOS = "algoritmos_basicos"
    ALGORITMOS_AVANZADOS = "algoritmos_avanzados"
    ESTRUCTURAS_DATOS = "estructuras_datos"
    MATEMATICAS = "matematicas"
    GEOMETRIA = "geometria"
    GRAFOS = "teoria_grafos"
    PROGRAMACION_DINAMICA = "programacion_dinamica"
    STRINGS = "procesamiento_strings"
    
    # Habilidades de implementación
    DEBUGGING = "debugging"
    OPTIMIZACION_CODIGO = "optimizacion_codigo"
    TESTING = "testing"
    
    # Habilidades de lenguajes
    PYTHON = "python"
    CPP = "cpp"
    JAVA = "java"
    JAVASCRIPT = "javascript"
    
    # Habilidades blandas
    TRABAJO_BAJO_PRESION = "trabajo_bajo_presion"
    COMUNICACION = "comunicacion"
    LIDERAZGO = "liderazgo"
    CREATIVIDAD = "creatividad"