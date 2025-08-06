import numpy as np
import random
import time
import logging
from typing import List, Tuple, Dict
from copy import deepcopy

logger = logging.getLogger(__name__)

class IndividuoGenetico:
    """Representa una solución en el algoritmo genético"""
    def __init__(self, cromosoma: np.ndarray):
        self.cromosoma = cromosoma
        self.fitness = 0.0
        self.fitness_componentes = {}
        self.es_valido = False
        self.violaciones = []
        self.generacion = 0

class EvaluadorFitness:
    """Evaluador único y limpio para fitness de soluciones"""
    
    def __init__(self):
        # Pesos para los componentes del fitness
        self.peso_puntuacion = 0.40       # Puntuación total esperada
        self.peso_compatibilidad = 0.30   # Qué tan bien encajan participante-problema
        self.peso_tiempo = 0.20           # Eficiencia temporal
        self.peso_balance = 0.10          # Balance en uso de participantes
        
    def evaluar_individuo(self, individuo, problemas, participantes):
        try:
            matriz = individuo.cromosoma
            asignaciones = self._extraer_asignaciones_validas(matriz, problemas, participantes)
            
            if not asignaciones:
                individuo.fitness = 0.0
                individuo.es_valido = False
                individuo.violaciones = ["No hay asignaciones válidas"]
                individuo.fitness_componentes = {}
                return
            
            # VALIDACIÓN 1: Un participante solo puede resolver un problema
            participantes_usados = set()
            asignaciones_sin_participantes_duplicados = []
            
            for asig in asignaciones:
                participante_idx = asig['participante_idx']
                if participante_idx not in participantes_usados:
                    asignaciones_sin_participantes_duplicados.append(asig)
                    participantes_usados.add(participante_idx)
                else:
                    logger.debug(f"Participante {participante_idx} ya asignado, saltando duplicado")
            
            # VALIDACIÓN 2: Un problema solo puede ser asignado a un participante
            problemas_usados = set()
            asignaciones_finales = []
            
            for asig in asignaciones_sin_participantes_duplicados:
                problema_idx = asig['problema_idx']
                if problema_idx not in problemas_usados:
                    asignaciones_finales.append(asig)
                    problemas_usados.add(problema_idx)
                else:
                    logger.debug(f"Problema {problema_idx} ya asignado, saltando duplicado")
            
            if not asignaciones_finales:
                individuo.fitness = 0.0
                individuo.es_valido = False
                individuo.violaciones = ["Violación: múltiples asignaciones por problema/participante"]
                individuo.fitness_componentes = {}
                return
            
            # Calcular componentes del fitness - manejar errores
            try:
                puntuacion_norm = self._calcular_puntuacion_normalizada(asignaciones_finales, problemas)
                compatibilidad_prom = self._calcular_compatibilidad_promedio(asignaciones_finales)
                tiempo_norm = self._calcular_tiempo_normalizado(asignaciones_finales, problemas)
                balance_norm = self._calcular_balance_participantes(asignaciones_finales, len(participantes))
                
                # Validar que no hay NaN o valores inválidos
                puntuacion_norm = self._validar_valor(puntuacion_norm, 0.0)
                compatibilidad_prom = self._validar_valor(compatibilidad_prom, 0.5)
                tiempo_norm = self._validar_valor(tiempo_norm, 0.5)
                balance_norm = self._validar_valor(balance_norm, 0.0)
                
            except Exception as e:
                logger.error(f"Error calculando componentes de fitness: {e}")
                individuo.fitness = 0.0
                individuo.es_valido = False
                individuo.violaciones = [f"Error en cálculo de fitness: {str(e)}"]
                individuo.fitness_componentes = {}
                return
            
            # Calcular fitness total con diversificación
            fitness_base = (
                self.peso_puntuacion * puntuacion_norm +
                self.peso_compatibilidad * compatibilidad_prom +
                self.peso_tiempo * tiempo_norm +
                self.peso_balance * balance_norm
            )
            
            # Agregar diversificación para evitar fitness idéntico
            diversificacion = self._calcular_diversificacion(asignaciones_finales, matriz)
            fitness = fitness_base + (diversificacion * 0.01)  # Pequeño factor de diversificación
            
            # Bonus por alta compatibilidad
            if compatibilidad_prom > 0.8:
                fitness *= 1.1
            
            individuo.fitness = max(0.0, min(1.0, fitness))
            individuo.fitness_componentes = {
                'puntuacion_normalizada': puntuacion_norm,
                'compatibilidad_promedio': compatibilidad_prom,
                'tiempo_normalizado': tiempo_norm,
                'balance_normalizado': balance_norm,
                'diversificacion': diversificacion,
                'asignaciones_validas': len(asignaciones_finales)
            }
            individuo.es_valido = True
            individuo.violaciones = []
            
        except Exception as e:
            logger.error(f"Error general en evaluación de individuo: {e}")
            individuo.fitness = 0.0
            individuo.es_valido = False
            individuo.violaciones = [f"Error de evaluación: {str(e)}"]
            individuo.fitness_componentes = {}
    
    def _validar_valor(self, valor, default=0.0):
        """Valida que un valor no sea NaN, infinito o None"""
        if valor is None or np.isnan(valor) or np.isinf(valor):
            return default
        return max(0.0, min(1.0, float(valor)))
    
    def _calcular_diversificacion(self, asignaciones, matriz):
        """Calcula un factor de diversificación basado en la distribución de asignaciones"""
        try:
            if not asignaciones:
                return 0.0
            
            # Factor basado en la varianza de las prioridades
            prioridades = [a['prioridad'] for a in asignaciones]
            if len(prioridades) > 1:
                varianza_prioridades = np.var(prioridades)
            else:
                varianza_prioridades = 0.0
            
            # Factor basado en la distribución espacial en la matriz
            posiciones = [(a['problema_idx'], a['participante_idx']) for a in asignaciones]
            if len(posiciones) > 1:
                # Calcular dispersión geométrica
                centroide_prob = np.mean([pos[0] for pos in posiciones])
                centroide_part = np.mean([pos[1] for pos in posiciones])
                
                dispersiones = [
                    np.sqrt((pos[0] - centroide_prob)**2 + (pos[1] - centroide_part)**2)
                    for pos in posiciones
                ]
                dispersión_promedio = np.mean(dispersiones)
            else:
                dispersión_promedio = 0.0
            
            # Combinar factores
            diversificacion = (varianza_prioridades * 0.3) + (dispersión_promedio * 0.7)
            return min(1.0, diversificacion / 10.0)  # Normalizar
            
        except Exception as e:
            logger.debug(f"Error calculando diversificación: {e}")
            return random.random() * 0.1  # Pequeño factor aleatorio como fallback
    
    def _extraer_asignaciones_validas(self, matriz, problemas, participantes):
        """Extrae asignaciones válidas de la matriz cromosoma"""
        asignaciones = []
        
        try:
            for i in range(min(matriz.shape[0], len(problemas))):
                for j in range(min(matriz.shape[1], len(participantes))):
                    if matriz[i, j] > 0:
                        problema = problemas[i]
                        participante = participantes[j]
                        
                        compatibilidad = self._calcular_compatibilidad_segura(participante, problema)
                        probabilidad_exito = self._calcular_probabilidad_exito_segura(participante, problema)
                        tiempo_estimado = self._estimar_tiempo_seguro(participante, problema)
                        puntos_problema = self._obtener_puntos_seguros(problema)
                        
                        # Validar todos los valores
                        compatibilidad = self._validar_valor(compatibilidad, 0.5)
                        probabilidad_exito = self._validar_valor(probabilidad_exito, 0.5)
                        tiempo_estimado = max(30, int(tiempo_estimado)) if not np.isnan(tiempo_estimado) else 120
                        puntos_problema = max(10, int(puntos_problema)) if not np.isnan(puntos_problema) else 100
                        
                        asignacion = {
                            'problema_idx': i,
                            'participante_idx': j,
                            'prioridad': int(matriz[i, j]),
                            'compatibilidad': compatibilidad,
                            'probabilidad_exito': probabilidad_exito,
                            'tiempo_estimado': tiempo_estimado,
                            'puntos_problema': puntos_problema,
                            'puntuacion_esperada': puntos_problema * probabilidad_exito
                        }
                        
                        asignaciones.append(asignacion)
                        
        except Exception as e:
            logger.error(f"Error extrayendo asignaciones: {e}")
            return []
        
        return asignaciones
    
    def _obtener_tasa_exito_participante(self, participante):
        """Obtiene la tasa de éxito del participante - flexible con nombres de atributos"""
        # Lista de posibles nombres para tasa de éxito
        posibles_nombres = [
            'tasa_exito_historica',
            'tasa_exito',
            'success_rate', 
            'rate_success',
            'porcentaje_exito',
            'exito_historico',
            'win_rate',
            'performance',
            'rendimiento',
            'skill_level',
            'nivel_habilidad'
        ]
        
        try:
            for nombre in posibles_nombres:
                if hasattr(participante, nombre):
                    valor = getattr(participante, nombre)
                    if isinstance(valor, (int, float)) and not np.isnan(valor) and not np.isinf(valor):
                        # Si el valor está en porcentaje (>1), convertir a decimal
                        if valor > 1:
                            valor = valor / 100.0
                        # Asegurar que esté en rango 0-1
                        if 0 <= valor <= 1:
                            return float(valor)
                        else:
                            logger.warning(f"Valor de {nombre} fuera de rango (0-1): {valor}")
            
            # Si no encontramos nada, usar valor por defecto basado en otros atributos
            logger.debug(f"Participante {getattr(participante, 'nombre', 'desconocido')} no tiene tasa de éxito explícita, calculando estimada")
            return self._calcular_tasa_exito_estimada(participante)
            
        except Exception as e:
            logger.warning(f"Error obteniendo tasa de éxito: {e}")
            return 0.6  # Valor por defecto seguro
    
    def _calcular_tasa_exito_estimada(self, participante):
        """Calcula una tasa de éxito estimada basada en otros atributos disponibles"""
        try:
            # Intentar calcular desde otros atributos
            posibles_indicadores = {
                # Experiencia/competencias
                'experiencia': ['experiencia', 'experience', 'competencias_previas', 'competencias', 'años_experiencia'],
                # Problemas resueltos
                'problemas_resueltos': ['problemas_resueltos', 'problems_solved', 'problemas_resueltos_total', 'ejercicios_completados'],
                # Nivel/ranking
                'nivel': ['nivel', 'level', 'rank', 'ranking', 'skill_level', 'nivel_habilidad'],
                # Puntuación histórica
                'puntuacion': ['puntuacion_promedio', 'score', 'average_score', 'puntos_promedio']
            }
            
            valores_encontrados = {}
            
            for categoria, nombres in posibles_indicadores.items():
                for nombre in nombres:
                    if hasattr(participante, nombre):
                        valor = getattr(participante, nombre)
                        if isinstance(valor, (int, float)) and valor >= 0 and not np.isnan(valor) and not np.isinf(valor):
                            valores_encontrados[categoria] = valor
                            break
            
            # Calcular tasa estimada basada en lo que encontremos
            if valores_encontrados:
                tasa_base = 0.5  # Base neutral
                
                # Ajustar por experiencia (0-20 años típico)
                if 'experiencia' in valores_encontrados:
                    exp = min(valores_encontrados['experiencia'], 20)
                    tasa_base += (exp / 20) * 0.2  # +0.2 máximo
                
                # Ajustar por problemas resueltos (0-100 típico)
                if 'problemas_resueltos' in valores_encontrados:
                    prob = min(valores_encontrados['problemas_resueltos'], 100)
                    tasa_base += (prob / 100) * 0.15  # +0.15 máximo
                
                # Ajustar por nivel (1-10 típico)
                if 'nivel' in valores_encontrados:
                    nivel = min(valores_encontrados['nivel'], 10)
                    if nivel >= 1:
                        tasa_base += ((nivel - 1) / 9) * 0.15  # +0.15 máximo
                
                return max(0.1, min(0.9, tasa_base))
            
            # Si no hay nada, usar valor por defecto conservador
            logger.debug(f"No se encontraron indicadores de rendimiento, usando tasa por defecto")
            return 0.6  # Valor neutral-positivo
            
        except Exception as e:
            logger.warning(f"Error calculando tasa de éxito estimada: {e}")
            return 0.6
    
    def _calcular_compatibilidad_segura(self, participante, problema):
        """Calcula compatibilidad - usa método flexible para obtener tasa de éxito"""
        try:
            # Intentar método personalizado primero
            if hasattr(participante, 'calcular_compatibilidad_problema'):
                try:
                    resultado = participante.calcular_compatibilidad_problema(problema)
                    if isinstance(resultado, (int, float)) and 0 <= resultado <= 1 and not np.isnan(resultado):
                        return float(resultado)
                    else:
                        logger.warning(f"Método calcular_compatibilidad_problema devolvió valor inválido: {resultado}")
                except Exception as e:
                    logger.warning(f"Error en método personalizado calcular_compatibilidad_problema: {e}")
            
            # Obtener tasa de éxito de forma flexible
            tasa_exito = self._obtener_tasa_exito_participante(participante)
            
            # Atributos opcionales con valores por defecto razonables
            experiencia = getattr(participante, 'competencias_previas', 
                                 getattr(participante, 'experiencia',
                                 getattr(participante, 'experience', 0)))
            if not isinstance(experiencia, (int, float)) or experiencia < 0 or np.isnan(experiencia):
                experiencia = 0
            
            problemas_resueltos = getattr(participante, 'problemas_resueltos_total',
                                        getattr(participante, 'problemas_resueltos',
                                        getattr(participante, 'problems_solved', 0)))
            if not isinstance(problemas_resueltos, (int, float)) or problemas_resueltos < 0 or np.isnan(problemas_resueltos):
                problemas_resueltos = 0
            
            # Calcular compatibilidad con datos validados
            factor_experiencia = min(0.3, (experiencia / 20.0) * 0.3)
            factor_problemas = min(0.2, (problemas_resueltos / 100.0) * 0.2)
            
            compatibilidad = float(tasa_exito) + factor_experiencia + factor_problemas
            return max(0.1, min(0.95, compatibilidad))
            
        except Exception as e:
            logger.warning(f"Error calculando compatibilidad: {e}")
            return 0.6  # Valor por defecto
    
    def _calcular_probabilidad_exito_segura(self, participante, problema):
        """Calcula probabilidad de éxito usando método flexible"""
        try:
            # Intentar método personalizado
            if hasattr(participante, 'calcular_probabilidad_exito'):
                try:
                    resultado = participante.calcular_probabilidad_exito(problema)
                    if isinstance(resultado, (int, float)) and 0 <= resultado <= 1 and not np.isnan(resultado):
                        return float(resultado)
                    else:
                        logger.warning(f"Método calcular_probabilidad_exito devolvió valor inválido: {resultado}")
                except Exception as e:
                    logger.warning(f"Error en método personalizado calcular_probabilidad_exito: {e}")
            
            # Obtener tasa de éxito de forma flexible
            tasa_exito_base = self._obtener_tasa_exito_participante(participante)
            
            # nivel_dificultad es opcional, valor por defecto 'medio'
            dificultad = getattr(problema, 'nivel_dificultad',
                               getattr(problema, 'dificultad',
                               getattr(problema, 'difficulty', 'medio')))
            
            # Factores de dificultad - más tolerante con variaciones
            factores_dificultad = {
                'muy_facil': 1.3, 'muy facil': 1.3, 'muy fácil': 1.3, 'very easy': 1.3,
                'facil': 1.2, 'fácil': 1.2, 'easy': 1.2,
                'medio': 1.0, 'normal': 1.0, 'medium': 1.0, 'average': 1.0,
                'dificil': 0.8, 'difícil': 0.8, 'hard': 0.8,
                'muy_dificil': 0.6, 'muy difícil': 0.6, 'muy_difícil': 0.6, 'very hard': 0.6,
                # Valores numéricos también
                '1': 1.3, '2': 1.2, '3': 1.0, '4': 0.8, '5': 0.6
            }
            
            dificultad_str = str(dificultad).lower().strip()
            factor_dificultad = factores_dificultad.get(dificultad_str, 1.0)  # Por defecto medio
            
            probabilidad = float(tasa_exito_base) * factor_dificultad
            return max(0.1, min(0.95, probabilidad))
            
        except Exception as e:
            logger.warning(f"Error calculando probabilidad de éxito: {e}")
            return 0.6  # Valor por defecto
    
    def _estimar_tiempo_seguro(self, participante, problema):
        """Estima tiempo - tolerante con fallbacks razonables"""
        try:
            # Intentar método personalizado
            if hasattr(participante, 'estimar_tiempo_resolucion'):
                try:
                    resultado = participante.estimar_tiempo_resolucion(problema)
                    if isinstance(resultado, (int, float)) and resultado > 0 and not np.isnan(resultado):
                        return max(30, int(resultado))
                    else:
                        logger.warning(f"Método estimar_tiempo_resolucion devolvió valor inválido: {resultado}")
                except Exception as e:
                    logger.warning(f"Error en método personalizado estimar_tiempo_resolucion: {e}")
            
            # tiempo_limite es opcional, por defecto 120 minutos
            tiempo_base = getattr(problema, 'tiempo_limite', 120)
            if not isinstance(tiempo_base, (int, float)) or tiempo_base <= 0 or np.isnan(tiempo_base):
                logger.warning(f"tiempo_limite inválido ({tiempo_base}), usando 120 minutos")
                tiempo_base = 120
            
            # factor_velocidad es opcional
            factor_velocidad = getattr(participante, 'factor_velocidad', 1.0)
            if not isinstance(factor_velocidad, (int, float)) or factor_velocidad <= 0 or np.isnan(factor_velocidad):
                logger.warning(f"factor_velocidad inválido ({factor_velocidad}), usando 1.0")
                factor_velocidad = 1.0
            
            # experiencia es opcional
            experiencia = getattr(participante, 'competencias_previas', 0)
            if not isinstance(experiencia, (int, float)) or experiencia < 0 or np.isnan(experiencia):
                experiencia = 0
            
            # Validar rangos con valores sensatos
            tiempo_base = max(30, min(300, int(tiempo_base)))
            factor_velocidad = max(0.5, min(2.0, float(factor_velocidad)))
            
            # Factor experiencia
            factor_experiencia = max(0.7, 1.0 - (experiencia / 50.0))
            
            tiempo_estimado = tiempo_base * factor_velocidad * factor_experiencia
            return max(30, int(tiempo_estimado))
            
        except Exception as e:
            logger.warning(f"Error estimando tiempo: {e}")
            return 120  # Valor por defecto
    
    def _obtener_puntos_seguros(self, problema):
        """Obtiene puntos del problema - tolerante con fallbacks"""
        try:
            # Intentar puntos totales directos
            if hasattr(problema, 'puntos_totales'):
                puntos_totales = getattr(problema, 'puntos_totales')
                if isinstance(puntos_totales, (int, float)) and puntos_totales > 0 and not np.isnan(puntos_totales):
                    return int(puntos_totales)
                else:
                    logger.warning(f"puntos_totales inválido ({puntos_totales}), calculando desde componentes")
            
            # Calcular desde componentes con valores por defecto
            puntos_base = getattr(problema, 'puntos_base', 100)
            if not isinstance(puntos_base, (int, float)) or puntos_base <= 0 or np.isnan(puntos_base):
                logger.warning(f"puntos_base inválido ({puntos_base}), usando 100")
                puntos_base = 100
            
            multiplicador = getattr(problema, 'multiplicador_dificultad', 1.0)
            if not isinstance(multiplicador, (int, float)) or multiplicador <= 0 or np.isnan(multiplicador):
                logger.warning(f"multiplicador_dificultad inválido ({multiplicador}), usando 1.0")
                multiplicador = 1.0
            
            puntos_base = max(10, min(1000, int(puntos_base)))
            multiplicador = max(0.1, min(5.0, float(multiplicador)))
            
            return int(puntos_base * multiplicador)
            
        except Exception as e:
            logger.warning(f"Error obteniendo puntos: {e}")
            return 100  # Valor por defecto
    
    def _calcular_puntuacion_normalizada(self, asignaciones, problemas):
        """Calcula puntuación normalizada"""
        try:
            if not asignaciones:
                return 0.0
                
            puntuacion_total = sum(a['puntuacion_esperada'] for a in asignaciones)
            puntuacion_maxima = sum(self._obtener_puntos_seguros(p) for p in problemas)
            
            if puntuacion_maxima == 0:
                return 0.0
                
            resultado = puntuacion_total / puntuacion_maxima
            return self._validar_valor(resultado, 0.0)
            
        except Exception as e:
            logger.warning(f"Error calculando puntuación normalizada: {e}")
            return 0.0
    
    def _calcular_compatibilidad_promedio(self, asignaciones):
        """Calcula compatibilidad promedio"""
        try:
            if not asignaciones:
                return 0.0
            
            compatibilidades = [a['compatibilidad'] for a in asignaciones]
            resultado = sum(compatibilidades) / len(compatibilidades)
            return self._validar_valor(resultado, 0.5)
            
        except Exception as e:
            logger.warning(f"Error calculando compatibilidad promedio: {e}")
            return 0.5
    
    def _calcular_tiempo_normalizado(self, asignaciones, problemas):
        """Calcula tiempo normalizado (menor tiempo = mejor)"""
        try:
            if not asignaciones:
                return 0.0
                
            tiempo_total = sum(a['tiempo_estimado'] for a in asignaciones)
            tiempo_maximo = sum(getattr(p, 'tiempo_limite', 120) for p in problemas) * 1.5
            
            if tiempo_maximo == 0:
                return 0.5
                
            tiempo_norm = tiempo_total / tiempo_maximo
            resultado = max(0.0, 1.0 - min(1.0, tiempo_norm))  # Invertir: menos tiempo = mejor
            return self._validar_valor(resultado, 0.5)
            
        except Exception as e:
            logger.warning(f"Error calculando tiempo normalizado: {e}")
            return 0.5
    
    def _calcular_balance_participantes(self, asignaciones, total_participantes):
        """Calcula qué tan balanceado está el uso de participantes"""
        try:
            if not asignaciones or total_participantes == 0:
                return 0.0
                
            participantes_usados = len(set(a['participante_idx'] for a in asignaciones))
            resultado = participantes_usados / total_participantes
            return self._validar_valor(resultado, 0.0)
            
        except Exception as e:
            logger.warning(f"Error calculando balance: {e}")
            return 0.0

class AlgoritmoGeneticoCoderush:
    """Algoritmo genético específico para CODERUSH - limpio y eficiente"""
    
    def __init__(self, problemas, participantes, tamanio_equipo=None, **kwargs):
        self.problemas = problemas
        self.participantes = participantes
        self.evaluador = EvaluadorFitness()
        
        # Validación del tamaño del equipo
        self.num_problemas = len(problemas)
        self.num_participantes = len(participantes)
        
        # Validar tamaño del equipo
        if tamanio_equipo is not None:
            if tamanio_equipo > self.num_participantes:
                raise ValueError(f"El tamaño del equipo ({tamanio_equipo}) no puede ser mayor que el número de participantes disponibles ({self.num_participantes})")
            if tamanio_equipo <= 0:
                raise ValueError(f"El tamaño del equipo debe ser mayor que 0")
            self.tamanio_equipo = tamanio_equipo
        else:
            self.tamanio_equipo = self.num_participantes
        
        # Parámetros del algoritmo - ajustados para mayor diversidad
        self.poblacion_size = kwargs.get('poblacion_size', 100)  # Aumentamos población
        self.generaciones_max = kwargs.get('generaciones', 150)  # Más generaciones
        self.prob_cruce = kwargs.get('tasa_cruce', 0.85)  # Mayor cruce
        self.prob_mutacion = kwargs.get('tasa_mutacion', 0.15)  # Mayor mutación
        self.elite_size = max(3, int(self.poblacion_size * 0.05))  # Elite más pequeño
        self.torneo_size = 4  # Torneos más competitivos
        
        # Validaciones básicas
        if not problemas or not participantes:
            raise ValueError("Debe haber al menos un problema y un participante")
        
        # Solo podemos asignar como máximo min(problemas, tamaño_equipo)
        self.max_asignaciones = min(self.num_problemas, self.tamanio_equipo)
        
        # Histórico y múltiples soluciones
        self.top_soluciones = []  # Para almacenar las mejores soluciones
        self.historial_fitness = []
        
        # Para tracking de diversidad
        self.fitness_unicos = set()
        self.contador_diversidad = 0

    def _crear_poblacion_inicial(self):
        poblacion = []
        
        # Crear diferentes estrategias de inicialización para mayor diversidad
        estrategias = ['aleatoria', 'greedy', 'balanceada', 'prioridad_alta']
        
        for i in range(self.poblacion_size):
            estrategia = estrategias[i % len(estrategias)]
            
            if estrategia == 'aleatoria':
                cromosoma = self._crear_individuo_aleatorio()
            elif estrategia == 'greedy':
                cromosoma = self._crear_individuo_greedy()
            elif estrategia == 'balanceada':
                cromosoma = self._crear_individuo_balanceado()
            else:  # prioridad_alta
                cromosoma = self._crear_individuo_prioridad_alta()
            
            individuo = IndividuoGenetico(cromosoma)
            individuo.generacion = 0
            poblacion.append(individuo)
        
        return poblacion

    def _crear_individuo_aleatorio(self):
        """Crea un individuo completamente aleatorio"""
        cromosoma = np.zeros((self.num_problemas, self.num_participantes), dtype=int)
        
        # Seleccionar participantes aleatoriamente
        participantes_disponibles = list(range(self.num_participantes))
        random.shuffle(participantes_disponibles)
        participantes_seleccionados = participantes_disponibles[:self.tamanio_equipo]
        
        # Asignar problemas aleatoriamente - ASEGURANDO 1:1
        problemas_indices = list(range(self.num_problemas))
        random.shuffle(problemas_indices)
        
        # Solo asignar hasta el mínimo entre problemas disponibles y participantes seleccionados
        max_asignaciones = min(len(problemas_indices), len(participantes_seleccionados))
        
        for i in range(max_asignaciones):
            problema_idx = problemas_indices[i]
            participante_idx = participantes_seleccionados[i]
            prioridad = random.randint(1, 3)
            cromosoma[problema_idx, participante_idx] = prioridad
        
        return cromosoma
    
    def _crear_individuo_greedy(self):
        """Crea un individuo usando estrategia greedy basada en compatibilidad"""
        cromosoma = np.zeros((self.num_problemas, self.num_participantes), dtype=int)
        
        # Calcular compatibilidades para todas las combinaciones
        compatibilidades = []
        for i, problema in enumerate(self.problemas):
            for j, participante in enumerate(self.participantes):
                comp = self.evaluador._calcular_compatibilidad_segura(participante, problema)
                compatibilidades.append((comp, i, j))
        
        # Ordenar por compatibilidad descendente
        compatibilidades.sort(reverse=True)
        
        participantes_usados = set()
        problemas_usados = set()
        asignaciones_realizadas = 0
        
        for comp, problema_idx, participante_idx in compatibilidades:
            # Validar que no se repitan participantes ni problemas
            if (participante_idx not in participantes_usados and 
                problema_idx not in problemas_usados and
                asignaciones_realizadas < self.max_asignaciones and
                len(participantes_usados) < self.tamanio_equipo):
                
                # Prioridad basada en compatibilidad
                if comp > 0.8:
                    prioridad = 3
                elif comp > 0.6:
                    prioridad = 2
                else:
                    prioridad = 1
                
                cromosoma[problema_idx, participante_idx] = prioridad
                participantes_usados.add(participante_idx)
                problemas_usados.add(problema_idx)
                asignaciones_realizadas += 1
        
        return cromosoma
    
    def _crear_individuo_balanceado(self):
        """Crea un individuo balanceando diferentes criterios"""
        cromosoma = np.zeros((self.num_problemas, self.num_participantes), dtype=int)
        
        # Seleccionar participantes balanceadamente
        participantes_disponibles = list(range(self.num_participantes))
        random.shuffle(participantes_disponibles)
        participantes_seleccionados = participantes_disponibles[:self.tamanio_equipo]
        
        # Dividir problemas en grupos por dificultad/importancia
        problemas_alta_prioridad = []
        problemas_media_prioridad = []
        problemas_baja_prioridad = []
        
        for i, problema in enumerate(self.problemas):
            puntos = self.evaluador._obtener_puntos_seguros(problema)
            if puntos > 150:
                problemas_alta_prioridad.append(i)
            elif puntos > 75:
                problemas_media_prioridad.append(i)
            else:
                problemas_baja_prioridad.append(i)
        
        # Crear lista de asignaciones priorizando problemas importantes
        todas_las_asignaciones = []
        
        # Alta prioridad primero
        for prob_idx in problemas_alta_prioridad:
            todas_las_asignaciones.append((prob_idx, 3))
        
        # Media prioridad
        for prob_idx in problemas_media_prioridad:
            todas_las_asignaciones.append((prob_idx, 2))
        
        # Baja prioridad
        for prob_idx in problemas_baja_prioridad:
            todas_las_asignaciones.append((prob_idx, 1))
        
        # Asignar hasta el límite - ASEGURANDO 1:1
        random.shuffle(participantes_seleccionados)
        
        max_asignaciones = min(len(todas_las_asignaciones), len(participantes_seleccionados))
        
        for i in range(max_asignaciones):
            prob_idx, prioridad = todas_las_asignaciones[i]
            participante_idx = participantes_seleccionados[i]
            cromosoma[prob_idx, participante_idx] = prioridad
        
        return cromosoma
    
    def _crear_individuo_prioridad_alta(self):
        """Crea un individuo enfocado en problemas de alta prioridad"""
        cromosoma = np.zeros((self.num_problemas, self.num_participantes), dtype=int)
        
        # Identificar los mejores participantes
        mejores_participantes = []
        for j, participante in enumerate(self.participantes):
            tasa_exito = self.evaluador._obtener_tasa_exito_participante(participante)
            mejores_participantes.append((tasa_exito, j))
        
        mejores_participantes.sort(reverse=True)
        mejores_participantes = mejores_participantes[:self.tamanio_equipo]
        
        # Identificar problemas más valiosos
        problemas_valiosos = []
        for i, problema in enumerate(self.problemas):
            puntos = self.evaluador._obtener_puntos_seguros(problema)
            problemas_valiosos.append((puntos, i))
        
        problemas_valiosos.sort(reverse=True)
        
        # Asignar mejores participantes a problemas más valiosos - ASEGURANDO 1:1
        max_asignaciones = min(len(mejores_participantes), len(problemas_valiosos))
        
        for i in range(max_asignaciones):
            _, participante_idx = mejores_participantes[i]
            _, problema_idx = problemas_valiosos[i]
            
            # Todos con alta prioridad
            cromosoma[problema_idx, participante_idx] = 3
        
        return cromosoma
    
    def ejecutar(self):
        start_time = time.time()
        
        logger.info(f"Iniciando CODERUSH con {self.num_problemas} problemas, {self.num_participantes} participantes y equipo de {self.tamanio_equipo}")
        
        try:
            poblacion = self._crear_poblacion_inicial()
            
            individuos_validos = 0
            for individuo in poblacion:
                try:
                    self.evaluador.evaluar_individuo(individuo, self.problemas, self.participantes)
                    if individuo.es_valido:
                        individuos_validos += 1
                        # Agregar a conjunto de fitness únicos
                        fitness_redondeado = round(individuo.fitness, 6)  # Más precisión
                        self.fitness_unicos.add(fitness_redondeado)
                except Exception as e:
                    logger.warning(f"Error evaluando individuo inicial: {e}")
                    individuo.fitness = 0.0
                    individuo.es_valido = False
                    individuo.violaciones = [f"Error de evaluación: {str(e)}"]
            
            if individuos_validos == 0:
                raise RuntimeError("No se pudo crear ningún individuo válido en la población inicial. Revise los datos de entrada.")
            
            logger.info(f"Población inicial: {individuos_validos}/{len(poblacion)} individuos válidos")
            logger.info(f"Diversidad inicial: {len(self.fitness_unicos)} fitness únicos")
            
            self._actualizar_top_soluciones(poblacion)
            
            # Evolucionar
            generaciones_sin_mejora = 0
            fitness_anterior = 0
            
            for generacion in range(self.generaciones_max):
                try:
                    # Crear nueva generación
                    nueva_poblacion = self._evolucionar_generacion(poblacion)
                    
                    # Evaluar nueva población
                    individuos_validos_gen = 0
                    fitness_generacion = []
                    
                    for individuo in nueva_poblacion:
                        try:
                            self.evaluador.evaluar_individuo(individuo, self.problemas, self.participantes)
                            if individuo.es_valido:
                                individuos_validos_gen += 1
                                fitness_generacion.append(individuo.fitness)
                                # Agregar a conjunto de fitness únicos
                                fitness_redondeado = round(individuo.fitness, 6)
                                self.fitness_unicos.add(fitness_redondeado)
                        except Exception as e:
                            logger.debug(f"Error evaluando individuo en gen {generacion}: {e}")
                            individuo.fitness = 0.0
                            individuo.es_valido = False
                            individuo.violaciones = [f"Error: {str(e)}"]
                    
                    poblacion = nueva_poblacion
                    
                    # Actualizar mejores soluciones
                    fitness_anterior = self.top_soluciones[0].fitness if self.top_soluciones else 0
                    self._actualizar_top_soluciones(poblacion)
                    
                    if generacion % 10 == 0:
                        fitness_promedio = np.mean(fitness_generacion) if fitness_generacion else 0
                        fitness_std = np.std(fitness_generacion) if len(fitness_generacion) > 1 else 0
                        
                        self.historial_fitness.append({
                            'generacion': generacion,
                            'mejor_fitness': self.top_soluciones[0].fitness if self.top_soluciones else 0,
                            'fitness_promedio': fitness_promedio,
                            'fitness_std': fitness_std,
                            'individuos_validos': individuos_validos_gen,
                            'diversidad_fitness': len(self.fitness_unicos)
                        })
                        
                        logger.info(f"Gen {generacion}: Mejor={self.top_soluciones[0].fitness:.6f}, Promedio={fitness_promedio:.4f}, STD={fitness_std:.4f}, Válidos={individuos_validos_gen}, Diversidad={len(self.fitness_unicos)}")
                    
                    mejora = (self.top_soluciones[0].fitness if self.top_soluciones else 0) - fitness_anterior
                    if mejora > 0.00001:  # Umbral más estricto para mejora
                        generaciones_sin_mejora = 0
                    else:
                        generaciones_sin_mejora += 1
                    
                    # Condiciones de parada más estrictas
                    if generaciones_sin_mejora >= 30:
                        logger.info(f"Parada temprana en generación {generacion} - Sin mejora por {generaciones_sin_mejora} generaciones")
                        break
                    
                    if self.top_soluciones and self.top_soluciones[0].fitness >= 0.98:
                        logger.info(f"Parada temprana en generación {generacion} - Fitness óptimo alcanzado")
                        break
                        
                except Exception as e:
                    logger.error(f"Error en generación {generacion}: {e}")
                    if generacion < 5:  # Si falla muy temprano
                        raise RuntimeError(f"Error crítico en generación {generacion}: {str(e)}")
                    else:
                        logger.warning(f"Continuando después de error en generación {generacion}")
                        break
            
            # Generar resultado
            tiempo_total = time.time() - start_time
            logger.info(f"Optimización completada: {len(self.fitness_unicos)} fitness únicos generados")
            return self._generar_resultado_final(generacion + 1, tiempo_total)
            
        except Exception as e:
            logger.error(f"Error durante la ejecución del algoritmo: {e}")
            raise RuntimeError(f"Error durante la optimización: {str(e)}")
    
    def _evolucionar_generacion(self, poblacion):
        nueva_poblacion = []
        
        # Ordenar población por fitness
        poblacion_ordenada = sorted(poblacion, key=lambda x: x.fitness, reverse=True)
        
        # Elite (conservar mejores)
        for i in range(self.elite_size):
            elite = IndividuoGenetico(poblacion_ordenada[i].cromosoma.copy())
            elite.generacion = poblacion_ordenada[i].generacion + 1
            nueva_poblacion.append(elite)
        
        # Llenar resto con cruce y mutación
        while len(nueva_poblacion) < self.poblacion_size:
            # Selección de padres
            padre1 = self._seleccion_torneo(poblacion)
            padre2 = self._seleccion_torneo(poblacion)
            
            # Asegurar que los padres sean diferentes
            intentos = 0
            while np.array_equal(padre1.cromosoma, padre2.cromosoma) and intentos < 5:
                padre2 = self._seleccion_torneo(poblacion)
                intentos += 1
            
            # Cruce
            if random.random() < self.prob_cruce:
                hijo = self._cruzar_mejorado(padre1, padre2)
            else:
                hijo = IndividuoGenetico(padre1.cromosoma.copy())
            
            # Mutación adaptativa
            prob_mutacion_adaptativa = self.prob_mutacion
            if len(self.fitness_unicos) < 10:  # Poca diversidad
                prob_mutacion_adaptativa *= 1.5
            
            if random.random() < prob_mutacion_adaptativa:
                hijo.cromosoma = self._mutar_mejorado(hijo.cromosoma)
            
            hijo.generacion = padre1.generacion + 1
            nueva_poblacion.append(hijo)
        
        return nueva_poblacion[:self.poblacion_size]
    
    def _seleccion_torneo(self, poblacion):
        # Selección por torneo con diversidad
        torneo = random.sample(poblacion, min(self.torneo_size, len(poblacion)))
        
        # 90% de las veces seleccionar el mejor, 10% diversificar
        if random.random() < 0.9:
            return max(torneo, key=lambda x: x.fitness)
        else:
            # Seleccionar aleatoriamente del torneo para diversidad
            return random.choice(torneo)
    
    def _cruzar_mejorado(self, padre1, padre2):
        """Cruce mejorado con mayor diversidad y validación 1:1"""
        hijo_cromosoma = np.zeros_like(padre1.cromosoma)
        participantes_usados = set()
        problemas_usados = set()
        
        # Recopilar todas las asignaciones de ambos padres
        todas_asignaciones = []
        
        # Del padre 1
        for i in range(padre1.cromosoma.shape[0]):
            for j in range(padre1.cromosoma.shape[1]):
                if padre1.cromosoma[i, j] > 0:
                    # Calcular score para esta asignación
                    participante = self.participantes[j]
                    problema = self.problemas[i]
                    compatibilidad = self.evaluador._calcular_compatibilidad_segura(participante, problema)
                    score = compatibilidad * padre1.cromosoma[i, j]
                    todas_asignaciones.append((score, i, j, padre1.cromosoma[i, j], 1))
        
        # Del padre 2
        for i in range(padre2.cromosoma.shape[0]):
            for j in range(padre2.cromosoma.shape[1]):
                if padre2.cromosoma[i, j] > 0:
                    participante = self.participantes[j]
                    problema = self.problemas[i]
                    compatibilidad = self.evaluador._calcular_compatibilidad_segura(participante, problema)
                    score = compatibilidad * padre2.cromosoma[i, j]
                    todas_asignaciones.append((score, i, j, padre2.cromosoma[i, j], 2))
        
        # Ordenar por score y agregar factor aleatorio para diversidad
        for i, asig in enumerate(todas_asignaciones):
            score, prob_idx, part_idx, prioridad, padre = asig
            factor_aleatorio = random.uniform(0.8, 1.2)  # Pequeña variación aleatoria
            todas_asignaciones[i] = (score * factor_aleatorio, prob_idx, part_idx, prioridad, padre)
        
        todas_asignaciones.sort(key=lambda x: x[0], reverse=True)
        
        # Seleccionar las mejores asignaciones sin repetir participantes NI PROBLEMAS
        asignaciones_realizadas = 0
        for score, problema_idx, participante_idx, prioridad, padre_origen in todas_asignaciones:
            if (participante_idx not in participantes_usados and 
                problema_idx not in problemas_usados and
                asignaciones_realizadas < self.max_asignaciones):
                
                # Pequeña variación en la prioridad para diversidad
                if random.random() < 0.1:
                    prioridad = random.randint(1, 3)
                
                hijo_cromosoma[problema_idx, participante_idx] = prioridad
                participantes_usados.add(participante_idx)
                problemas_usados.add(problema_idx)
                asignaciones_realizadas += 1
        
        return IndividuoGenetico(hijo_cromosoma)
    
    def _mutar_mejorado(self, cromosoma):
        """Mutación mejorada con múltiples tipos y validación 1:1"""
        cromosoma_mutado = cromosoma.copy()
        
        # Encontrar asignaciones actuales
        asignaciones = []
        for i in range(cromosoma.shape[0]):
            for j in range(cromosoma.shape[1]):
                if cromosoma[i, j] > 0:
                    asignaciones.append((i, j))
        
        if not asignaciones:
            return cromosoma_mutado
        
        # Diferentes tipos de mutación
        tipos_mutacion = ['cambiar_participante', 'cambiar_prioridad', 'intercambiar_asignaciones', 'agregar_asignacion']
        tipo_mutacion = random.choice(tipos_mutacion)
        
        if tipo_mutacion == 'cambiar_participante' and len(asignaciones) > 0:
            # Cambiar asignación a un participante diferente
            problema_idx, participante_actual = random.choice(asignaciones)
            
            # Encontrar participantes libres
            participantes_usados = set(j for i, j in asignaciones)
            participantes_libres = [j for j in range(cromosoma.shape[1]) 
                                  if j not in participantes_usados]
            
            if participantes_libres:
                nuevo_participante = random.choice(participantes_libres)
                prioridad_actual = cromosoma[problema_idx, participante_actual]
                
                cromosoma_mutado[problema_idx, participante_actual] = 0
                cromosoma_mutado[problema_idx, nuevo_participante] = prioridad_actual
        
        elif tipo_mutacion == 'cambiar_prioridad' and len(asignaciones) > 0:
            # Cambiar prioridad de una asignación existente
            problema_idx, participante_idx = random.choice(asignaciones)
            nueva_prioridad = random.randint(1, 3)
            cromosoma_mutado[problema_idx, participante_idx] = nueva_prioridad
        
        elif tipo_mutacion == 'intercambiar_asignaciones' and len(asignaciones) >= 2:
            # Intercambiar dos asignaciones
            asig1 = random.choice(asignaciones)
            asig2 = random.choice(asignaciones)
            
            if asig1 != asig2:
                prob1, part1 = asig1
                prob2, part2 = asig2
                
                prio1 = cromosoma[prob1, part1]
                prio2 = cromosoma[prob2, part2]
                
                cromosoma_mutado[prob1, part1] = 0
                cromosoma_mutado[prob2, part2] = 0
                cromosoma_mutado[prob1, part2] = prio1
                cromosoma_mutado[prob2, part1] = prio2
        
        elif tipo_mutacion == 'agregar_asignacion':
            # Intentar agregar una nueva asignación si hay espacio
            if len(asignaciones) < self.max_asignaciones:
                participantes_usados = set(j for i, j in asignaciones)
                problemas_usados = set(i for i, j in asignaciones)
                
                participantes_libres = [j for j in range(cromosoma.shape[1]) 
                                      if j not in participantes_usados]
                problemas_libres = [i for i in range(cromosoma.shape[0]) 
                                  if i not in problemas_usados]
                
                if participantes_libres and problemas_libres:
                    nuevo_participante = random.choice(participantes_libres)
                    nuevo_problema = random.choice(problemas_libres)
                    nueva_prioridad = random.randint(1, 3)
                    
                    cromosoma_mutado[nuevo_problema, nuevo_participante] = nueva_prioridad
        
        return cromosoma_mutado
    
    def _actualizar_top_soluciones(self, poblacion):
        """Actualiza las TOP 3 mejores soluciones con mejor diversidad"""
        # Combinar población actual con top soluciones existentes
        todos_candidatos = list(poblacion)
        
        if self.top_soluciones:
            todos_candidatos.extend(self.top_soluciones)
        
        # Ordenar por fitness
        candidatos_ordenados = sorted(todos_candidatos, key=lambda x: x.fitness, reverse=True)
        
        # Filtrar soluciones únicas y diversas
        soluciones_unicas = []
        matrices_vistas = set()
        fitness_vistos = set()
        
        for candidato in candidatos_ordenados:
            if len(soluciones_unicas) >= 3:
                break
                
            # Hash de la matriz para detectar duplicados exactos
            matriz_hash = hash(candidato.cromosoma.tobytes())
            fitness_redondeado = round(candidato.fitness, 6)  # Más precisión
            
            # Aceptar si es único o suficientemente diferente
            es_nuevo = matriz_hash not in matrices_vistas
            es_fitness_diverso = fitness_redondeado not in fitness_vistos or len(soluciones_unicas) == 0
            
            if es_nuevo and (es_fitness_diverso or candidato.fitness > 0.8):
                # Crear copia profunda
                solucion_copia = IndividuoGenetico(candidato.cromosoma.copy())
                solucion_copia.fitness = candidato.fitness
                solucion_copia.fitness_componentes = candidato.fitness_componentes.copy() if hasattr(candidato, 'fitness_componentes') else {}
                solucion_copia.es_valido = candidato.es_valido
                solucion_copia.violaciones = candidato.violaciones.copy() if hasattr(candidato, 'violaciones') else []
                solucion_copia.generacion = candidato.generacion
                
                soluciones_unicas.append(solucion_copia)
                matrices_vistas.add(matriz_hash)
                fitness_vistos.add(fitness_redondeado)
        
        self.top_soluciones = soluciones_unicas
    
    def _generar_resultado_final(self, generaciones_ejecutadas, tiempo_ejecucion):
        if not self.top_soluciones:
            raise RuntimeError("No se encontró ninguna solución válida")
        
        # Generar resultados para cada solución del TOP 3
        soluciones_detalladas = []
        
        for idx, solucion in enumerate(self.top_soluciones):
            asignaciones_detalle = self._generar_asignaciones_detalle(solucion)
            
            # VALIDAR que asignaciones_detalle no esté vacío
            if not asignaciones_detalle:
                logger.warning(f"Solución {idx+1} no tiene asignaciones válidas")
                continue
            
            # Estadísticas por solución - CON VALIDACIÓN
            try:
                puntuacion_total = sum(a.get('puntuacion_esperada', 0) for a in asignaciones_detalle)
                tiempo_total = sum(a.get('tiempo_estimado', 120) for a in asignaciones_detalle)
                
                # Validar compatibilidades
                compatibilidades = [a.get('compatibilidad', 0.6) for a in asignaciones_detalle]
                compatibilidad_prom = np.mean(compatibilidades) if compatibilidades else 0.6
                
                # Asegurar que no hay NaN
                puntuacion_total = puntuacion_total if not np.isnan(puntuacion_total) else 0
                tiempo_total = tiempo_total if not np.isnan(tiempo_total) else len(asignaciones_detalle) * 120
                compatibilidad_prom = compatibilidad_prom if not np.isnan(compatibilidad_prom) else 0.6
                
            except Exception as e:
                logger.warning(f"Error calculando estadísticas para solución {idx+1}: {e}")
                puntuacion_total = 0
                tiempo_total = len(asignaciones_detalle) * 120
                compatibilidad_prom = 0.6
            
            solucion_detallada = {
                'solucion_id': idx + 1,
                'matriz_asignacion': solucion.cromosoma.tolist(),
                'fitness': round(solucion.fitness, 6),  # Más precisión
                'fitness_componentes': solucion.fitness_componentes,
                'es_solucion_valida': solucion.es_valido,
                'violaciones': solucion.violaciones,
                'asignaciones_detalle': asignaciones_detalle,
                'estadisticas_solucion': {
                    'problemas_asignados': len(asignaciones_detalle),
                    'participantes_utilizados': len(set(a['participante_id'] for a in asignaciones_detalle)),
                    'puntuacion_total_esperada': round(puntuacion_total, 2),
                    'tiempo_total_estimado': int(tiempo_total),
                    'compatibilidad_promedio': round(compatibilidad_prom * 100, 2),
                    'eficiencia_asignacion': round(len(asignaciones_detalle) / self.max_asignaciones, 3)
                }
            }
            
            soluciones_detalladas.append(solucion_detallada)
        
        if not soluciones_detalladas:
            raise RuntimeError("No se generaron soluciones válidas")
        
        # Estadísticas generales
        mejor_solucion = soluciones_detalladas[0]
        
        return {
            'exito': True,
            'num_soluciones_obtenidas': len(soluciones_detalladas),
            'mejor_solucion': mejor_solucion,
            'top_3_soluciones': soluciones_detalladas,
            'configuracion': {
                'tamanio_equipo_solicitado': self.tamanio_equipo,
                'participantes_disponibles': self.num_participantes,
                'problemas_disponibles': self.num_problemas,
                'max_asignaciones_posibles': self.max_asignaciones
            },
            'estadisticas_globales': {
                'generaciones_ejecutadas': generaciones_ejecutadas,
                'tiempo_ejecucion_segundos': tiempo_ejecucion,
                'fitness_mejor_solucion': mejor_solucion['fitness'],
                'solucion_valida': mejor_solucion['es_solucion_valida'],
                'diversidad_total': len(self.fitness_unicos),
                'fitness_unicos_generados': len(self.fitness_unicos)
            },
            'evolucion': {
                'historial_fitness': self.historial_fitness
            }
        }
    
    def _generar_asignaciones_detalle(self, solucion):
        """Genera asignaciones detalladas para una solución - CON VALIDACIÓN 1:1"""
        asignaciones_detalle = []
        matriz = solucion.cromosoma
        
        # Seguimiento de problemas ya asignados para evitar duplicados
        problemas_asignados = set()
        participantes_asignados = set()
        
        for i in range(matriz.shape[0]):
            for j in range(matriz.shape[1]):
                if matriz[i, j] > 0:
                    # VALIDACIÓN: Evitar problemas y participantes duplicados
                    if i in problemas_asignados:
                        logger.debug(f"Saltando problema {i} - ya asignado")
                        continue
                        
                    if j in participantes_asignados:
                        logger.debug(f"Saltando participante {j} - ya asignado")
                        continue
                    
                    problemas_asignados.add(i)
                    participantes_asignados.add(j)
                    
                    problema = self.problemas[i]
                    participante = self.participantes[j]
                    
                    try:
                        puntos = self.evaluador._obtener_puntos_seguros(problema)
                        compatibilidad = self.evaluador._calcular_compatibilidad_segura(participante, problema)
                        prob_exito = self.evaluador._calcular_probabilidad_exito_segura(participante, problema)
                        tiempo_est = self.evaluador._estimar_tiempo_seguro(participante, problema)
                        
                        # Validar todos los valores
                        puntos = max(10, int(puntos)) if not np.isnan(puntos) else 100
                        compatibilidad = max(0.1, min(1.0, float(compatibilidad))) if not np.isnan(compatibilidad) else 0.6
                        prob_exito = max(0.1, min(1.0, float(prob_exito))) if not np.isnan(prob_exito) else 0.6
                        tiempo_est = max(30, int(tiempo_est)) if not np.isnan(tiempo_est) else 120
                        
                        puntuacion_esperada = puntos * prob_exito
                        
                        asignacion = {
                            'problema_id': getattr(problema, 'id', i),
                            'problema_nombre': getattr(problema, 'nombre', f'Problema {i+1}'),
                            'participante_id': getattr(participante, 'id', j),
                            'participante_nombre': getattr(participante, 'nombre', f'Participante {j+1}'),
                            'prioridad': int(matriz[i, j]),
                            'puntos_problema': puntos,
                            'compatibilidad': compatibilidad,
                            'probabilidad_exito': prob_exito,
                            'tiempo_estimado': tiempo_est,
                            'puntuacion_esperada': round(puntuacion_esperada, 2)
                        }
                        
                        asignaciones_detalle.append(asignacion)
                        
                    except Exception as e:
                        logger.warning(f"Error procesando asignación {i},{j}: {e}")
                        continue
        
        return asignaciones_detalle

# Wrapper mejorado para compatibilidad con tu API existente
class AlgoritmoGenetico:
    def __init__(self, participantes, problemas, tamanio_equipo=None, evaluador=None, **kwargs):
        self.participantes_data = participantes
        self.problemas_data = problemas
        
        # Validar tamaño del equipo antes de crear el algoritmo
        if tamanio_equipo is not None:
            if tamanio_equipo > len(participantes):
                raise ValueError(f"Error: El tamaño del equipo ({tamanio_equipo}) no puede ser mayor que el número de participantes disponibles ({len(participantes)}). Por favor, ajuste el tamaño del equipo.")
            if tamanio_equipo <= 0:
                raise ValueError(f"Error: El tamaño del equipo debe ser mayor que 0.")
        
        # Crear instancia del algoritmo principal
        self.algoritmo = AlgoritmoGeneticoCoderush(
            problemas, 
            participantes, 
            tamanio_equipo=tamanio_equipo,
            **kwargs
        )
    
    def ejecutar(self):
        resultado = self.algoritmo.ejecutar()
        
        if not resultado['exito']:
            raise RuntimeError("No se pudo generar una solución válida")
        
        mejor_solucion = resultado['mejor_solucion']
        top_3_soluciones = resultado['top_3_soluciones']
        
        estadisticas = {
            'generaciones_ejecutadas': resultado['estadisticas_globales']['generaciones_ejecutadas'],
            'tiempo_ejecucion': resultado['estadisticas_globales']['tiempo_ejecucion_segundos'],
            'fitness_componentes': mejor_solucion['fitness_componentes'],
            'puntuacion_total': mejor_solucion['estadisticas_solucion']['puntuacion_total_esperada'],
            'tiempo_total': mejor_solucion['estadisticas_solucion']['tiempo_total_estimado'],
            'compatibilidad_promedio': mejor_solucion['estadisticas_solucion']['compatibilidad_promedio'],
            'eficiencia': mejor_solucion['fitness'],
            'evolucion_fitness': [h['mejor_fitness'] for h in resultado['evolucion']['historial_fitness']],
            'top_3_soluciones': top_3_soluciones,
            'num_soluciones_obtenidas': resultado['num_soluciones_obtenidas'],
            'diversidad_total': resultado['estadisticas_globales']['diversidad_total'],
            'configuracion_equipo': {
                'tamanio_solicitado': resultado['configuracion']['tamanio_equipo_solicitado'],
                'participantes_disponibles': resultado['configuracion']['participantes_disponibles'],
                'problemas_disponibles': resultado['configuracion']['problemas_disponibles'],
                'max_asignaciones': resultado['configuracion']['max_asignaciones_posibles']
            }
        }
        
        return mejor_solucion['matriz_asignacion'], mejor_solucion['fitness'], estadisticas
    
    def generar_resumen_asignacion(self, solucion):
        """Genera resumen de asignaciones"""
        # Usar la primera solución como referencia si no se especifica
        if hasattr(self.algoritmo, 'top_soluciones') and self.algoritmo.top_soluciones:
            return self.algoritmo._generar_asignaciones_detalle(self.algoritmo.top_soluciones[0])
        else:
            return []
    
    def obtener_top_soluciones(self):
        """Obtiene las TOP 3 soluciones generadas"""
        if hasattr(self.algoritmo, 'top_soluciones'):
            soluciones_detalladas = []
            for idx, solucion in enumerate(self.algoritmo.top_soluciones):
                asignaciones = self.algoritmo._generar_asignaciones_detalle(solucion)
                
                solucion_info = {
                    'id': idx + 1,
                    'fitness': solucion.fitness,
                    'matriz': solucion.cromosoma.tolist(),
                    'asignaciones': asignaciones,
                    'valida': solucion.es_valido,
                    'violaciones': solucion.violaciones,
                    'estadisticas': {
                        'problemas_asignados': len(asignaciones),
                        'participantes_usados': len(set(a['participante_id'] for a in asignaciones)),
                        'puntuacion_esperada': sum(a['puntuacion_esperada'] for a in asignaciones),
                        'tiempo_total': sum(a['tiempo_estimado'] for a in asignaciones),
                        'compatibilidad_promedio': np.mean([a['compatibilidad'] for a in asignaciones]) * 100 if asignaciones else 0
                    }
                }
                soluciones_detalladas.append(solucion_info)
            
            return soluciones_detalladas
        return []

def validar_tamanio_equipo(tamanio_equipo, num_participantes):
    """Función auxiliar para validar el tamaño del equipo"""
    if tamanio_equipo is None:
        return {
            'valido': True, 
            'mensaje': f'Se usarán todos los {num_participantes} participantes disponibles',
            'tamanio_sugerido': num_participantes
        }
    
    if tamanio_equipo <= 0:
        return {
            'valido': False,
            'mensaje': 'El tamaño del equipo debe ser mayor que 0',
            'tamanio_sugerido': min(5, num_participantes)
        }
    
    if tamanio_equipo > num_participantes:
        return {
            'valido': False,
            'mensaje': f'El tamaño del equipo ({tamanio_equipo}) no puede ser mayor que el número de participantes disponibles ({num_participantes})',
            'tamanio_sugerido': num_participantes
        }
    
    return {
        'valido': True,
        'mensaje': f'Tamaño de equipo válido: {tamanio_equipo} participantes',
        'tamanio_sugerido': tamanio_equipo
    }

# Función auxiliar para debugging
def debug_datos_entrada(participantes, problemas):
    """Función para debuggear los datos de entrada y detectar problemas"""
    print("=== DEBUG DE DATOS DE ENTRADA ===")
    
    print(f"\nParticipantes: {len(participantes)}")
    for i, p in enumerate(participantes[:3]):  # Solo los primeros 3
        print(f"  Participante {i}:")
        for attr in dir(p):
            if not attr.startswith('_') and not callable(getattr(p, attr)):
                valor = getattr(p, attr)
                print(f"    {attr}: {valor} (tipo: {type(valor)})")
    
    print(f"\nProblemas: {len(problemas)}")
    for i, prob in enumerate(problemas[:3]):  # Solo los primeros 3
        print(f"  Problema {i}:")
        for attr in dir(prob):
            if not attr.startswith('_') and not callable(getattr(prob, attr)):
                valor = getattr(prob, attr)
                print(f"    {attr}: {valor} (tipo: {type(valor)})")
    
    print("=== FIN DEBUG ===\n")

def diagnosticar_algoritmo(participantes, problemas):
    """Diagnostica problemas en los datos de entrada"""
    
    print("🔍 DIAGNÓSTICO DEL ALGORITMO GENÉTICO")
    print("=" * 50)
    
    # 1. Verificar datos básicos
    print(f"📊 Participantes: {len(participantes)}")
    print(f"📊 Problemas: {len(problemas)}")
    
    # 2. Verificar atributos de participantes
    print("\n👥 ANÁLISIS DE PARTICIPANTES:")
    atributos_encontrados = set()
    valores_problematicos = []
    
    for i, p in enumerate(participantes[:5]):  # Solo primeros 5
        print(f"  Participante {i}:")
        for attr in dir(p):
            if not attr.startswith('_') and not callable(getattr(p, attr)):
                atributos_encontrados.add(attr)
                valor = getattr(p, attr)
                print(f"    {attr}: {valor} (tipo: {type(valor).__name__})")
                
                # Detectar valores problemáticos
                if isinstance(valor, (int, float)):
                    if np.isnan(valor) or np.isinf(valor):
                        valores_problematicos.append(f"Participante {i}.{attr} = {valor}")
    
    print(f"\n📋 Atributos únicos encontrados: {sorted(atributos_encontrados)}")
    
    # 3. Verificar atributos de problemas
    print("\n🎯 ANÁLISIS DE PROBLEMAS:")
    atributos_problemas = set()
    
    for i, prob in enumerate(problemas[:5]):  # Solo primeros 5
        print(f"  Problema {i}:")
        for attr in dir(prob):
            if not attr.startswith('_') and not callable(getattr(prob, attr)):
                atributos_problemas.add(attr)
                valor = getattr(prob, attr)
                print(f"    {attr}: {valor} (tipo: {type(valor).__name__})")
                
                # Detectar valores problemáticos
                if isinstance(valor, (int, float)):
                    if np.isnan(valor) or np.isinf(valor):
                        valores_problematicos.append(f"Problema {i}.{attr} = {valor}")
    
    print(f"\n📋 Atributos de problemas: {sorted(atributos_problemas)}")
    
    # 4. Reportar problemas
    if valores_problematicos:
        print("\n⚠️  VALORES PROBLEMÁTICOS DETECTADOS:")
        for problema in valores_problematicos:
            print(f"    ❌ {problema}")
    else:
        print("\n✅ No se detectaron valores NaN o infinitos")
    
    # 5. Verificar compatibilidad
    print("\n🔧 PRUEBA DE COMPATIBILIDAD:")
    try:
        evaluador = EvaluadorFitness()
        
        # Probar con primer participante y primer problema
        if participantes and problemas:
            p = participantes[0]
            prob = problemas[0]
            
            print("  Probando cálculos...")
            compatibilidad = evaluador._calcular_compatibilidad_segura(p, prob)
            prob_exito = evaluador._calcular_probabilidad_exito_segura(p, prob)
            tiempo = evaluador._estimar_tiempo_seguro(p, prob)
            puntos = evaluador._obtener_puntos_seguros(prob)
            
            print(f"    Compatibilidad: {compatibilidad}")
            print(f"    Probabilidad éxito: {prob_exito}")
            print(f"    Tiempo estimado: {tiempo}")
            print(f"    Puntos: {puntos}")
            
            if any(np.isnan([compatibilidad, prob_exito, tiempo, puntos])):
                print("    ❌ PROBLEMA: Algunos cálculos devuelven NaN")
            else:
                print("    ✅ Cálculos básicos funcionan")
                
    except Exception as e:
        print(f"    ❌ Error en prueba de compatibilidad: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 DIAGNÓSTICO COMPLETADO")
    
    return {
        'participantes': len(participantes),
        'problemas': len(problemas),
        'atributos_participantes': sorted(atributos_encontrados),
        'atributos_problemas': sorted(atributos_problemas),
        'valores_problematicos': valores_problematicos
    }