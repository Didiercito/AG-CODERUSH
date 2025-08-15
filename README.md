# 🚀 CODERUSH - Sistema de Optimización Genética

Sistema inteligente de optimización con algoritmo genético para competencias de programación y asignación de equipos.

## 📋 Características Principales

✅ **Algoritmo Genético Puro**
- Optimización multi-objetivo sin penalizaciones
- 4 objetivos principales: puntuación, fortalezas, problemas resueltos, tiempo
- Población adaptativa con estrategias diversas

✅ **Carga de Datos CSV**
- Interfaz para cargar participantes y problemas desde archivos CSV
- Validación automática de estructura de datos
- Procesamiento robusto con manejo de errores

✅ **API REST Simplificada**
- FastAPI con documentación automática
- Endpoint principal de optimización
- Métricas y análisis de convergencia

✅ **Interfaz Visual Completa**
- Dashboard interactivo para configuración
- Visualización de las 3 mejores soluciones
- Gráficas de convergencia del algoritmo genético

## 🏗️ Estructura del Proyecto

```
code-rush-back/
├── main.py                     # Aplicación FastAPI
├── config.py                   # Configuración del sistema
├── requirements.txt            # Dependencias
├── datasets/                   # Archivos CSV de ejemplo
│   ├── participantes_principiantes.csv
│   └── problemas_faciles.csv
├── models/                     # Modelos de datos
│   ├── __init__.py
│   └── schemas.py              # Esquemas Pydantic
├── core/                       # Lógica principal
│   ├── __init__.py
│   └── algoritmo_genetico.py   # Algoritmo genético completo
└── api/                        # Endpoints API
    ├── __init__.py
    └── routes/
        ├── __init__.py
        └── asignaciones.py     # Endpoint de optimización
```

## 🚀 Instalación y Configuración

### 1. Crear entorno virtual
```bash
# Crear carpeta del proyecto
mkdir coderush-backend && cd coderush-backend

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Windows:
venv\Scripts\activate
# En Linux/Mac:
source venv/bin/activate
```

### 2. Instalar dependencias
```bash
pip install fastapi uvicorn numpy pydantic
```

### 3. Ejecutar la aplicación
```bash
python main.py
```

### 4. Acceder a la documentación
- **Aplicación:** http://localhost:8000
- **Health Check:** http://localhost:8000/api/health
- **Swagger UI:** http://localhost:8000/docs

## 📊 Formato de CSV

### Participantes CSV (mínimo requerido)
```csv
id,nombre,email,edad,universidad,habilidad_principal,nivel_habilidad,experiencia_anos,tasa_exito_historica,tiempo_maximo_disponible,disponibilidad
1,Ana García,ana@email.com,22,Universidad Tech,algoritmos_basicos,0.8,2,0.75,180,true
```

### Problemas CSV (mínimo requerido)
```csv
id,nombre,descripcion,tipo,nivel_dificultad,puntos_base,multiplicador_dificultad,tiempo_limite,habilidades_requeridas,tasa_resolucion_historica
1,Ordenamiento,Algoritmo de ordenamiento,algoritmos,facil,100,1.2,45,algoritmos_basicos:0.6,0.75
```

## 📚 Uso Básico

### 1. Optimizar asignaciones
```bash
POST http://localhost:8000/api/optimizar
Content-Type: application/json

{
  "participantes": [...],  // Datos del CSV
  "problemas": [...],      // Datos del CSV
  "configuracion": {
    "nombre": "Competencia 2025",
    "tiempo_total_minutos": 300,
    "tamanio_equipo": 6,
    "tipo": "Maratón de Código"
  }
}
```

### 2. Obtener métricas de solución
```bash
GET http://localhost:8000/api/metricas/1
```

## 🎯 Endpoints Disponibles

| Endpoint | Método | Descripción |
|----------|---------|-------------|
| `/api/optimizar` | POST | Ejecutar algoritmo genético |
| `/api/metricas/{id}` | GET | Obtener métricas de solución específica |
| `/api/health` | GET | Estado del servidor |

## 🔧 Configuración del Algoritmo

### Variables de Optimización (4 objetivos)
1. **Maximizar Puntuación Total** (40%)
2. **Maximizar Fortalezas Individuales** (30%)
3. **Maximizar Problemas Resueltos** (20%)
4. **Minimizar Tiempo Total** (10%)

### Parámetros Adaptativos
- **Población:** 60-150 individuos (adaptativo)
- **Generaciones:** 100-150 (adaptativo)
- **Cruce:** 80%
- **Mutación:** 25%
- **Elitismo:** 5%

## 📊 Ejemplo de Respuesta

```json
{
  "success": true,
  "mensaje": "Optimización completada. 3 mejores estrategias encontradas.",
  "top_3_soluciones": {
    "solucion_1": {
      "solucion_id": 1,
      "fitness": 0.4249,
      "nombre_estrategia": "Estrategia Optimizada 1",
      "asignaciones_detalle": [
        {
          "problema_nombre": "Suma de dos números",
          "participante_nombre": "Valentina Ruiz",
          "compatibilidad": 0.35,
          "tiempo_estimado": 9.0,
          "puntuacion_esperada": 56.0
        }
      ],
      "estadisticas": {
        "puntuacion_total_esperada": 628.37,
        "tiempo_total_estimado": 41,
        "compatibilidad_promedio": 28.0,
        "participantes_utilizados": 6
      }
    }
  },
  "historial": [
    {
      "generacion": 0,
      "mejor_fitness": 0.3215,
      "fitness_promedio": 0.2487
    }
  ]
}
```

## 🔬 Algoritmo Genético

### Características Técnicas
- **Representación:** Matriz problemas x participantes
- **Selección:** Torneo adaptativo
- **Cruce:** Un punto con reparación
- **Mutación:** Intercambio e reasignación
- **Evaluación:** Sin penalizaciones, algoritmo puro

### Estructura del Individuo
```python
class IndividuoGenetico:
    cromosoma: np.ndarray    # Matriz de asignaciones
    fitness: float           # Valor de aptitud
    es_valido: bool         # Cumple restricciones
    metricas_detalladas: dict # Análisis adicional
```

## 🎮 Flujo de Trabajo

1. **Preparar Datos:** Crear CSVs de participantes y problemas
2. **Cargar en Frontend:** Usar botones "Cargar CSV"
3. **Configurar Competencia:** Establecer nombre, tiempo, tamaño equipo
4. **Ejecutar Optimización:** Algoritmo genético genera soluciones
5. **Analizar Resultados:** Revisar TOP 3 soluciones y métricas
6. **Ver Convergencia:** Gráficas de evolución del algoritmo

## 🐛 Solución de Problemas

### Error: "CSV mal formateado"
- **Causa:** Faltan columnas requeridas
- **Solución:** Verificar estructura contra ejemplo en `/datasets/`

### Error: "Participantes insuficientes"
- **Causa:** Tamaño equipo > participantes disponibles
- **Solución:** Reducir tamaño equipo o agregar participantes

### Fitness bajo consistente
- **Causa:** Incompatibilidad entre habilidades y problemas
- **Solución:** Revisar campo `habilidades_requeridas` en problemas

## 📈 Métricas de Rendimiento

- **Fitness:** 0.0 - 1.0 (sin penalizaciones)
- **Convergencia:** Típicamente en 50-100 generaciones
- **Soluciones válidas:** 100% (algoritmo puro)
- **Diversidad:** TOP 3 soluciones diferentes garantizada

## 🔄 Integración Frontend

El backend está diseñado para trabajar con un frontend React que:
- Carga archivos CSV de participantes y problemas
- Envía datos procesados al endpoint `/api/optimizar`
- Visualiza resultados y métricas de convergencia
- Permite análisis comparativo de las 3 mejores soluciones

## 📄 Datos de Ejemplo

El proyecto incluye archivos CSV de ejemplo en `/datasets/`:
- `participantes_principiantes.csv` - 8 participantes con habilidades básicas
- `problemas_faciles.csv` - 10 problemas de nivel principiante

## 🤝 Contribución

1. Fork el repositorio
2. Crear rama para feature (`git checkout -b feature/mejora`)
3. Commit cambios (`git commit -am 'Descripción del cambio'`)
4. Push a la rama (`git push origin feature/mejora`)
5. Crear Pull Request

## 📄 Licencia

Proyecto académico - Universidad Tecnológica

## 🎯 Objetivos Académicos

Este proyecto demuestra:
- ✅ Implementación completa de algoritmo genético
- ✅ API REST con FastAPI
- ✅ Procesamiento de datos CSV
- ✅ Optimización multi-objetivo
- ✅ Validación robusta de datos
- ✅ Interfaz visual funcional
- ✅ Documentación técnica completa