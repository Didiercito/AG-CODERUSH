# 🚀 CODERUSH - Sistema de Optimización Genética

Sistema avanzado de optimización con algoritmo genético para competencias de programación, hackathons y asignación de tareas en equipos de desarrollo.

## 📋 Características Principales

✅ **Sistema de Habilidades Avanzado**
- 20+ tipos de habilidades técnicas y blandas
- Niveles, experiencia y proyectos por habilidad
- Cálculo automático de compatibilidad problema-participante

✅ **Algoritmo Genético Robusto**
- Población de 100 individuos con estrategias diversas
- Cruce y mutación inteligentes que respetan restricciones
- Optimización multi-objetivo con pesos configurables

✅ **API REST Completa**
- FastAPI con documentación automática
- Endpoints para asignación, simulación y análisis
- Validación robusta de entrada y manejo de errores

✅ **Restricciones Inteligentes**
- Un problema por participante (restricción crítica)
- Validación de tiempo disponible
- Prerrequisitos de problemas
- Disponibilidad de participantes

## 🏗️ Estructura del Proyecto

```
coderush/
├── main.py                     # Punto de entrada FastAPI
├── config.py                   # Configuración del sistema
├── requirements.txt            # Dependencias
├── models/                     # Modelos de datos
│   ├── __init__.py
│   ├── participante.py         # Modelos de participantes
│   ├── problema.py             # Modelos de problemas
│   └── schemas.py              # Esquemas Pydantic
├── core/                       # Lógica principal
│   ├── __init__.py
│   ├── enums.py               # Enumeraciones
│   ├── evaluador.py           # Evaluación de fitness
│   └── algoritmo_genetico.py  # Algoritmo genético
└── api/                       # Endpoints API
    ├── __init__.py
    └── routes.py              # Rutas FastAPI
```

## 🚀 Instalación y Configuración

### 1. Crear entorno virtual
```bash
# Crear carpeta del proyecto
mkdir coderush && cd coderush

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
pip install -r requirements.txt
```

### 3. Ejecutar la aplicación
```bash
python main.py
```

### 4. Acceder a la documentación
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **API Base:** http://localhost:8000/api/

## 📚 Uso Básico

### 1. Obtener datos de ejemplo
```bash
GET http://localhost:8000/api/generar-datos-ejemplo
```

### 2. Crear asignación óptima
```bash
POST http://localhost:8000/api/asignar
Content-Type: application/json

{
  "problemas": [...],
  "participantes": [...],
  "parametros_ag": {
    "poblacion_size": 50,
    "generaciones_max": 100,
    "prob_cruce": 0.8,
    "prob_mutacion": 0.15
  }
}
```

### 3. Simular competencia
```bash
POST http://localhost:8000/api/simular-competencia
```

## 🎯 Endpoints Principales

| Endpoint | Método | Descripción |
|----------|---------|-------------|
| `/api/asignar` | POST | Crear asignación óptima |
| `/api/generar-datos-ejemplo` | POST | Generar datos de prueba |
| `/api/simular-competencia` | POST | Simular competencia completa |
| `/api/asignaciones` | GET | Listar todas las asignaciones |
| `/api/asignaciones/{id}` | GET | Obtener asignación específica |
| `/api/estadisticas-sistema` | GET | Estadísticas del sistema |

## 🔧 Configuración Avanzada

### Parámetros del Algoritmo Genético
```json
{
  "parametros_ag": {
    "poblacion_size": 100,
    "generaciones_max": 200,
    "prob_cruce": 0.8,
    "prob_mutacion": 0.15,
    "elitismo_porcentaje": 0.1,
    "torneo_size": 5
  }
}
```

### Configuración de Competencia
```json
{
  "configuracion_competencia": {
    "nombre": "Hackathon 2024",
    "duracion_total": 300,
    "peso_puntuacion": 0.4,
    "peso_compatibilidad": 0.25,
    "peso_balance_carga": 0.2,
    "peso_probabilidad_exito": 0.15
  }
}
```

## 📊 Ejemplo de Respuesta

```json
{
  "exito": true,
  "mensaje": "Asignación completada exitosamente",
  "matriz_asignacion": [[2, 0, 0], [0, 3, 0], [0, 0, 1]],
  "fitness_final": 0.87,
  "asignaciones_detalle": [
    {
      "problema_nombre": "Ordenamiento Avanzado",
      "participante_nombre": "Ana García",
      "compatibilidad": 0.91,
      "probabilidad_exito": 0.85,
      "puntuacion_esperada": 127.5
    }
  ],
  "estadisticas": {
    "generaciones_ejecutadas": 150,
    "tiempo_ejecucion_segundos": 2.34,
    "problemas_asignados": 3,
    "participantes_utilizados": 3
  }
}
```

## 🎮 Flujo de Trabajo Típico

1. **Definir Participantes:** Crear perfiles con habilidades específicas
2. **Definir Problemas:** Establecer requerimientos y puntuaciones
3. **Configurar Competencia:** Ajustar pesos y parámetros
4. **Ejecutar Optimización:** Usar algoritmo genético
5. **Analizar Resultados:** Revisar asignaciones y estadísticas
6. **Simular Competencia:** Probar la asignación en escenario real

## 🔬 Algoritmo Genético

### Características Técnicas
- **Representación:** Matriz de asignación con prioridades
- **Selección:** Torneo de 5 individuos
- **Cruce:** Uniforme inteligente que respeta restricciones
- **Mutación:** Adaptativa con 3 tipos diferentes
- **Elitismo:** 10% de mejores individuos conservados

### Objetivos de Optimización
1. **Puntuación Esperada** (40%): Maximizar puntos del equipo
2. **Compatibilidad** (25%): Ajustar habilidades a problemas
3. **Balance de Carga** (20%): Equilibrar trabajo entre participantes
4. **Probabilidad de Éxito** (15%): Maximizar chance de resolución

## 🐛 Solución de Problemas

### Error: "No puede haber más problemas que participantes"
- **Causa:** Restricción del modelo
- **Solución:** Agregar más participantes o reducir problemas

### Error: "Debe tener al menos una habilidad definida"
- **Causa:** Participante sin habilidades
- **Solución:** Definir al menos una habilidad por participante

### Fitness muy bajo
- **Causa:** Incompatibilidad entre problemas y participantes
- **Solución:** Ajustar habilidades o tipos de problemas

## 📈 Métricas de Rendimiento

- **Fitness:** 0.0 - 1.0 (mayor es mejor)
- **Tiempo de convergencia:** Típicamente < 100 generaciones
- **Diversidad de población:** 0.0 - 1.0 (mayor diversidad = mejor exploración)
- **Violaciones de restricciones:** 0 para solución válida

## 🤝 Contribución

1. Fork el repositorio
2. Crear rama para feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo `LICENSE` para más detalles.

## 🔗 Enlaces Útiles

- [Documentación FastAPI](https://fastapi.tiangolo.com/)
- [Algoritmos Genéticos](https://en.wikipedia.org/wiki/Genetic_algorithm)
- [Optimización Multi-objetivo](https://en.wikipedia.org/wiki/Multi-objective_optimization)