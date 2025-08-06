# core/evaluador.py - Versión con debugging completo

import numpy as np
from typing import Dict, List, TYPE_CHECKING, Any
import uuid
import logging
import traceback

# Configurar logging
logger = logging.getLogger(__name__)

# Evitar importaciones circulares
if TYPE_CHECKING:
    from models.schemas import ConfiguracionCompetencia
    from models.participante import PerfilParticipante
    from models.problema import ProblemaCompleto

class IndividuoGenetico:
    def __init__(self, cromosoma: np.ndarray):
        logger.debug(f"🧬 Creando IndividuoGenetico con cromosoma shape: {cromosoma.shape}")
        self.cromosoma = cromosoma  # Matriz de asignación
        self.fitness = 0.0
        self.fitness_componentes = {}
        self.es_valido = False
        self.violaciones = []
        self.generacion = 0
        self.id = str(uuid.uuid4())[:8]
        logger.debug(f"✅ IndividuoGenetico creado con ID: {self.id}")
    
    def __str__(self):
        return f"Individuo[{self.id}] - Fitness: {self.fitness:.3f} - Válido: {self.es_valido}"

class EvaluadorFitnessAvanzado:
    def __init__(self, config):
        logger.info(f"🎯 Inicializando EvaluadorFitnessAvanzado con config: {config}")
        self.config = config
        self.cache_evaluaciones = {}
        logger.info("✅ EvaluadorFitnessAvanzado inicializado")
    
    def evaluar_individuo(self, 
                         individuo: IndividuoGenetico,
                         problemas: List,
                         participantes: List) -> float:
        """Evaluación completa de un individuo"""
        
        try:
            logger.debug(f"🔍 Evaluando individuo {individuo.id}")
            logger.debug(f"   Problemas: {len(problemas)}, Participantes: {len(participantes)}")
            
            # Cache para evitar re-evaluaciones
            cache_key = f"{hash(individuo.cromosoma.tobytes())}"
            if cache_key in self.cache_evaluaciones:
                logger.debug(f"📋 Usando cache para individuo {individuo.id}")
                resultado = self.cache_evaluaciones[cache_key]
                individuo.fitness = resultado['fitness']
                individuo.fitness_componentes = resultado['componentes']
                individuo.es_valido = resultado['es_valido']
                individuo.violaciones = resultado['violaciones']
                return individuo.fitness
            
            matriz = individuo.cromosoma
            logger.debug(f"   Matriz shape: {matriz.shape}")
            
            # Crear diccionarios de manera segura
            dict_problemas = {}
            dict_participantes = {}
            
            try:
                dict_problemas = {p.id if hasattr(p, 'id') else i: p for i, p in enumerate(problemas)}
                dict_participantes = {p.id if hasattr(p, 'id') else i: p for i, p in enumerate(participantes)}
                logger.debug(f"   Diccionarios creados: {len(dict_problemas)} problemas, {len(dict_participantes)} participantes")
            except Exception as e:
                logger.error(f"❌ Error creando diccionarios: {e}")
                # Fallback
                dict_problemas = {i: p for i, p in enumerate(problemas)}
                dict_participantes = {i: p for i, p in enumerate(participantes)}
            
            # Validar restricciones críticas
            try:
                violaciones = self._validar_restricciones(matriz, problemas, participantes)
                individuo.violaciones = violaciones
                individuo.es_valido = len([v for v in violaciones if 'CRÍTICA' in v]) == 0
                logger.debug(f"   Violaciones: {len(violaciones)}, Válido: {individuo.es_valido}")
            except Exception as e:
                logger.error(f"❌ Error validando restricciones: {e}")
                individuo.violaciones = []
                individuo.es_valido = True
            
            # Evaluar componentes del fitness
            try:
                componentes = self._evaluar_componentes_fitness(matriz, dict_problemas, dict_participantes)
                individuo.fitness_componentes = componentes
                logger.debug(f"   Componentes evaluados: {list(componentes.keys())}")
            except Exception as e:
                logger.error(f"❌ Error evaluando componentes: {e}")
                logger.error(f"📍 Traceback: {traceback.format_exc()}")
                # Componentes por defecto
                componentes = {
                    'puntuacion_normalizada': 0.5,
                    'compatibilidad_normalizada': 0.5,
                    'balance_carga_normalizada': 0.5,
                    'probabilidad_exito_normalizada': 0.5
                }
                individuo.fitness_componentes = componentes
            
            # Calcular fitness total
            try:
                fitness_total = (
                    self.config.peso_puntuacion * componentes['puntuacion_normalizada'] +
                    self.config.peso_compatibilidad * componentes['compatibilidad_normalizada'] +
                    self.config.peso_balance_carga * componentes['balance_carga_normalizada'] +
                    self.config.peso_probabilidad_exito * componentes['probabilidad_exito_normalizada']
                )
                logger.debug(f"   Fitness base calculado: {fitness_total}")
            except Exception as e:
                logger.error(f"❌ Error calculando fitness total: {e}")
                fitness_total = 0.5
            
            # Aplicar penalización por violaciones
            if violaciones:
                try:
                    penalizacion = self._calcular_penalizacion(violaciones)
                    fitness_total *= (1.0 - penalizacion)
                    logger.debug(f"   Penalización aplicada: {penalizacion}, Fitness final: {fitness_total}")
                except Exception as e:
                    logger.error(f"❌ Error calculando penalización: {e}")
            
            individuo.fitness = fitness_total
            
            # Guardar en cache
            try:
                self.cache_evaluaciones[cache_key] = {
                    'fitness': fitness_total,
                    'componentes': componentes,
                    'es_valido': individuo.es_valido,
                    'violaciones': violaciones
                }
            except Exception as e:
                logger.warning(f"⚠️ No se pudo guardar en cache: {e}")
            
            logger.debug(f"✅ Individuo {individuo.id} evaluado: fitness={fitness_total:.3f}")
            return fitness_total
            
        except Exception as e:
            logger.error(f"❌ ERROR CRÍTICO evaluando individuo: {e}")
            logger.error(f"📍 Traceback: {traceback.format_exc()}")
            # Fitness por defecto en caso de error
            individuo.fitness = 0.1
            individuo.es_valido = False
            individuo.violaciones = [f"ERROR: {str(e)}"]
            return 0.1
    
    def _evaluar_componentes_fitness(self, 
                                   matriz: np.ndarray,
                                   dict_problemas: Dict,
                                   dict_participantes: Dict) -> Dict:
        """Evalúa cada componente del fitness por separado"""
        
        try:
            logger.debug(f"🔧 Evaluando componentes de fitness...")
            
            # 1. Puntuación esperada
            puntuacion_total = 0
            asignaciones_activas = []
            
            for i in range(matriz.shape[0]):
                for j in range(matriz.shape[1]):
                    if matriz[i, j] > 0:
                        try:
                            problema = dict_problemas[i]
                            participante = dict_participantes[j]
                            
                            # Obtener puntos del problema de manera segura
                            puntos = getattr(problema, 'puntos_totales', None)
                            if puntos is None:
                                puntos_base = getattr(problema, 'puntos_base', 100)
                                multiplicador = getattr(problema, 'multiplicador_dificultad', 1.0)
                                puntos = puntos_base * multiplicador
                            
                            # Calcular probabilidad de éxito de manera segura
                            try:
                                if hasattr(participante, 'calcular_probabilidad_exito'):
                                    prob_exito = participante.calcular_probabilidad_exito(problema)
                                else:
                                    prob_exito = 0.5
                            except Exception as e:
                                logger.debug(f"   Error calculando prob_exito: {e}")
                                prob_exito = 0.5
                            
                            puntuacion_esperada = puntos * prob_exito
                            puntuacion_total += puntuacion_esperada
                            
                            asignaciones_activas.append({
                                'problema_id': i,
                                'participante_id': j,
                                'prioridad': matriz[i, j],
                                'puntuacion_esperada': puntuacion_esperada,
                                'probabilidad_exito': prob_exito
                            })
                            
                        except Exception as e:
                            logger.debug(f"   Error procesando asignación ({i},{j}): {e}")
                            continue
            
            logger.debug(f"   Asignaciones activas: {len(asignaciones_activas)}")
            logger.debug(f"   Puntuación total: {puntuacion_total}")
            
            # 2. Compatibilidad promedio
            compatibilidades = []
            for asignacion in asignaciones_activas:
                try:
                    problema = dict_problemas[asignacion['problema_id']]
                    participante = dict_participantes[asignacion['participante_id']]
                    
                    if hasattr(participante, 'calcular_compatibilidad_problema'):
                        compatibilidad = participante.calcular_compatibilidad_problema(problema)
                    else:
                        compatibilidad = 0.5
                    
                    compatibilidades.append(compatibilidad)
                    
                except Exception as e:
                    logger.debug(f"   Error calculando compatibilidad: {e}")
                    compatibilidades.append(0.5)
            
            compatibilidad_promedio = np.mean(compatibilidades) if compatibilidades else 0.0
            logger.debug(f"   Compatibilidad promedio: {compatibilidad_promedio}")
            
            # 3. Balance de carga
            cargas_trabajo = []
            tiempos_participantes = []
            
            for j in range(matriz.shape[1]):
                tiempo_total = 0
                for i in range(matriz.shape[0]):
                    if matriz[i, j] > 0:
                        try:
                            problema = dict_problemas[i]
                            participante = dict_participantes[j]
                            
                            if hasattr(participante, 'estimar_tiempo_resolucion'):
                                tiempo_estimado = participante.estimar_tiempo_resolucion(problema)
                            else:
                                tiempo_estimado = getattr(problema, 'tiempo_limite', 120)
                            
                            tiempo_total += tiempo_estimado
                            
                        except Exception as e:
                            logger.debug(f"   Error calculando tiempo: {e}")
                            tiempo_total += 120
                
                cargas_trabajo.append(tiempo_total)
                if tiempo_total > 0:
                    tiempos_participantes.append(tiempo_total)
            
            # Balance mejor cuando la varianza es menor
            if len(tiempos_participantes) > 1:
                try:
                    varianza = np.var(tiempos_participantes)
                    media = np.mean(tiempos_participantes)
                    balance_score = 1.0 / (1.0 + varianza / max(media, 1))
                except:
                    balance_score = 0.5
            else:
                balance_score = 1.0 if tiempos_participantes else 0.0
            
            logger.debug(f"   Balance de carga: {balance_score}")
            
            # 4. Probabilidad de éxito promedio
            probabilidades_exito = [a['probabilidad_exito'] for a in asignaciones_activas]
            prob_exito_promedio = np.mean(probabilidades_exito) if probabilidades_exito else 0.0
            logger.debug(f"   Probabilidad éxito promedio: {prob_exito_promedio}")
            
            # Normalización (valores entre 0 y 1)
            try:
                puntuacion_max_teorica = sum(getattr(p, 'puntos_totales', 
                    getattr(p, 'puntos_base', 100) * getattr(p, 'multiplicador_dificultad', 1.0)) 
                    for p in dict_problemas.values())
            except:
                puntuacion_max_teorica = len(dict_problemas) * 100
            
            componentes_resultado = {
                'puntuacion_total': puntuacion_total,
                'puntuacion_normalizada': min(puntuacion_total / max(puntuacion_max_teorica, 1), 1.0),
                'compatibilidad_promedio': compatibilidad_promedio,
                'compatibilidad_normalizada': compatibilidad_promedio,
                'balance_carga_score': balance_score,
                'balance_carga_normalizada': balance_score,
                'probabilidad_exito_promedio': prob_exito_promedio,
                'probabilidad_exito_normalizada': prob_exito_promedio,
                'asignaciones_activas': len(asignaciones_activas),
                'cargas_trabajo': cargas_trabajo
            }
            
            logger.debug(f"✅ Componentes evaluados exitosamente")
            return componentes_resultado
            
        except Exception as e:
            logger.error(f"❌ Error evaluando componentes: {e}")
            logger.error(f"📍 Traceback: {traceback.format_exc()}")
            # Componentes por defecto
            return {
                'puntuacion_total': 0,
                'puntuacion_normalizada': 0.5,
                'compatibilidad_promedio': 0.5,
                'compatibilidad_normalizada': 0.5,
                'balance_carga_score': 0.5,
                'balance_carga_normalizada': 0.5,
                'probabilidad_exito_promedio': 0.5,
                'probabilidad_exito_normalizada': 0.5,
                'asignaciones_activas': 0,
                'cargas_trabajo': []
            }
    
    def _validar_restricciones(self, 
                             matriz: np.ndarray,
                             problemas: List,
                             participantes: List) -> List[str]:
        """Valida todas las restricciones del problema"""
        violaciones = []
        
        try:
            logger.debug(f"🔍 Validando restricciones...")
            
            # RESTRICCIÓN CRÍTICA: Un problema por participante
            for j in range(matriz.shape[1]):
                asignaciones = np.sum(matriz[:, j] > 0)
                if asignaciones > 1:
                    violacion = f"CRÍTICA: Participante {j} tiene {asignaciones} problemas asignados"
                    violaciones.append(violacion)
                    logger.debug(f"   {violacion}")
            
            # RESTRICCIÓN: Disponibilidad de participantes
            for j in range(matriz.shape[1]):
                if j < len(participantes):
                    try:
                        participante = participantes[j]
                        disponibilidad = getattr(participante, 'disponibilidad', True)
                        if not disponibilidad and np.any(matriz[:, j] > 0):
                            violacion = f"CRÍTICA: Participante {j} no está disponible"
                            violaciones.append(violacion)
                            logger.debug(f"   {violacion}")
                    except Exception as e:
                        logger.debug(f"   Error validando disponibilidad participante {j}: {e}")
            
            logger.debug(f"✅ Validación completada: {len(violaciones)} violaciones")
            return violaciones
            
        except Exception as e:
            logger.error(f"❌ Error validando restricciones: {e}")
            return []
    
    def _calcular_penalizacion(self, violaciones: List[str]) -> float:
        """Calcula penalización total por violaciones"""
        try:
            penalizacion = 0.0
            
            for violacion in violaciones:
                if 'CRÍTICA' in violacion:
                    penalizacion += 0.5  # 50% de penalización por violación crítica
                elif 'MENOR' in violacion:
                    penalizacion += 0.1  # 10% de penalización por violación menor
            
            return min(penalizacion, 0.9)  
            
        except Exception as e:
            logger.error(f"❌ Error calculando penalización: {e}")
            return 0.0


class ProblemaWrapper:
    def __init__(self, data: Dict[str, Any]):
        try:
            self.id: int = data.get('id', 0)
            self.nombre: str = data.get('nombre', 'Problema')
            self.tipo: str = data.get('tipo', 'general')
            self.nivel_dificultad: str = data.get('nivel_dificultad', 'medio')
            self.puntos_base: int = data.get('puntos_base', 100)
            self.multiplicador_dificultad: float = data.get('multiplicador_dificultad', 1.0)
            self.habilidades_requeridas: Dict[str, float] = data.get('habilidades_requeridas', {})
            self.tiempo_limite: int = data.get('tiempo_limite', 120)
            self.tasa_resolucion_historica: float = data.get('tasa_resolucion_historica', 0.5)
            self.puntos_totales: float = self.puntos_base * self.multiplicador_dificultad
            
        except Exception as e:
            self.id = 0
            self.nombre = 'Problema'
            self.tipo = 'general'
            self.nivel_dificultad = 'medio'
            self.puntos_base = 100
            self.multiplicador_dificultad = 1.0
            self.habilidades_requeridas = {}
            self.tiempo_limite = 120
            self.tasa_resolucion_historica = 0.5
            self.puntos_totales = 100

class ParticipanteWrapper:
    
    def __init__(self, data: Dict[str, Any], evaluador: 'EvaluadorAsignacion'):
        try:
            
            self.id: int = data.get('id', 0)
            self.nombre: str = data.get('nombre', 'Participante')
            self.email: str = data.get('email', '')
            self.habilidades: Dict[str, Any] = data.get('habilidades', {})
            self.competencias_participadas: int = data.get('competencias_participadas', 0)
            self.tasa_exito_historica: float = data.get('tasa_exito_historica', 0.5)
            self.tipos_problema_preferidos: List[str] = data.get('tipos_problema_preferidos', [])
            self.tipos_problema_evitar: List[str] = data.get('tipos_problema_evitar', [])
            self.tiempo_maximo_disponible: int = data.get('tiempo_maximo_disponible', 300)
            self.nivel_energia: float = data.get('nivel_energia', 0.8)
            self.nivel_concentracion: float = data.get('nivel_concentracion', 0.8)
            self.disponibilidad: bool = data.get('disponibilidad', True)
            self._evaluador = evaluador
            
            
        except Exception as e:
            self.id = 0
            self.nombre = 'Participante'
            self.email = ''
            self.habilidades = {}
            self.competencias_participadas = 0
            self.tasa_exito_historica = 0.5
            self.tipos_problema_preferidos = []
            self.tipos_problema_evitar = []
            self.tiempo_maximo_disponible = 300
            self.nivel_energia = 0.8
            self.nivel_concentracion = 0.8
            self.disponibilidad = True
            self._evaluador = evaluador
    
    def calcular_compatibilidad_problema(self, problema: ProblemaWrapper) -> float:
        try:
            return self._evaluador._calcular_compatibilidad_simple(self, problema)
        except Exception as e:
            return 0.5
    
    def calcular_probabilidad_exito(self, problema: ProblemaWrapper) -> float:
        try:
            return self._evaluador._calcular_probabilidad_simple(self, problema)
        except Exception as e:
            return 0.5
    
    def estimar_tiempo_resolucion(self, problema: ProblemaWrapper) -> float:
        try:
            return self._evaluador._estimar_tiempo_simple(self, problema)
        except Exception as e:
            return 120

class EvaluadorAsignacion:
    
    def __init__(self):
        try:
            self.config = type('Config', (), {
                'peso_puntuacion': 0.4,
                'peso_compatibilidad': 0.3,
                'peso_balance_carga': 0.2,
                'peso_probabilidad_exito': 0.1
            })()
            
            self.evaluador_real = EvaluadorFitnessAvanzado(self.config)
            
            
        except Exception as e:
            logger.error(f"❌ Error inicializando EvaluadorAsignacion: {e}")
            logger.error(f"📍 Traceback: {traceback.format_exc()}")
            raise
    
    def evaluar(self, solucion, participantes, problemas):
        try:
            if not hasattr(solucion, 'cromosoma'):
                import numpy as np
                if isinstance(solucion, list):
                    cromosoma = np.array(solucion)
                else:
                    cromosoma = solucion
                individuo = IndividuoGenetico(cromosoma)
            else:
                individuo = solucion
            
            problemas_obj = self._convertir_problemas(problemas)
            participantes_obj = self._convertir_participantes(participantes)
            
            fitness = self.evaluador_real.evaluar_individuo(individuo, problemas_obj, participantes_obj)
            logger.debug(f"✅ Solución evaluada: fitness={fitness}")
            return fitness
            
        except Exception as e:
            logger.error(f"❌ Error evaluando solución: {e}")
            logger.error(f"📍 Traceback: {traceback.format_exc()}")
            return 0.5  # Fitness por defecto
    
    def _convertir_problemas(self, problemas_data: List[Dict[str, Any]]) -> List[ProblemaWrapper]:
        """Convierte diccionarios a objetos problema con type hints correctos"""
        try:
            logger.debug(f"🔧 Convirtiendo {len(problemas_data)} problemas...")
            problemas_obj = [ProblemaWrapper(p_data) for p_data in problemas_data]
            logger.debug(f"✅ {len(problemas_obj)} problemas convertidos")
            return problemas_obj
        except Exception as e:
            logger.error(f"❌ Error convirtiendo problemas: {e}")
            return []
    
    def _convertir_participantes(self, participantes_data: List[Dict[str, Any]]) -> List[ParticipanteWrapper]:
        """Convierte diccionarios a objetos participante con type hints correctos"""
        try:
            logger.debug(f"🔧 Convirtiendo {len(participantes_data)} participantes...")
            participantes_obj = [ParticipanteWrapper(p_data, self) for p_data in participantes_data]
            logger.debug(f"✅ {len(participantes_obj)} participantes convertidos")
            return participantes_obj
        except Exception as e:
            logger.error(f"❌ Error convirtiendo participantes: {e}")
            return []
    
    def _calcular_compatibilidad_simple(self, participante: ParticipanteWrapper, problema: ProblemaWrapper) -> float:
        """Calcula compatibilidad básica"""
        try:
            if not problema.habilidades_requeridas or not participante.habilidades:
                return 0.5
            
            compatibilidades = []
            for habilidad, nivel_requerido in problema.habilidades_requeridas.items():
                if habilidad in participante.habilidades:
                    habilidad_data = participante.habilidades[habilidad]
                    if isinstance(habilidad_data, dict):
                        nivel_participante = habilidad_data.get('nivel', 0)
                    else:
                        nivel_participante = float(habilidad_data) if isinstance(habilidad_data, (int, float)) else 0.5
                    compatibilidad = min(nivel_participante / max(nivel_requerido, 0.1), 1.0)
                    compatibilidades.append(compatibilidad)
                else:
                    compatibilidades.append(0.2)  # Penalización por no tener la habilidad
            
            resultado = sum(compatibilidades) / len(compatibilidades) if compatibilidades else 0.5
            return max(0.0, min(resultado, 1.0))
            
        except Exception as e:
            logger.debug(f"Error calculando compatibilidad simple: {e}")
            return 0.5
    
    def _calcular_probabilidad_simple(self, participante: ParticipanteWrapper, problema: ProblemaWrapper) -> float:
        """Calcula probabilidad de éxito básica"""
        try:
            compatibilidad = self._calcular_compatibilidad_simple(participante, problema)
            experiencia = min(participante.competencias_participadas / 10.0, 1.0)
            energia = participante.nivel_energia
            concentracion = participante.nivel_concentracion
            
            # Preferencias de tipo de problema
            bonus_preferencia = 0.0
            if problema.tipo in participante.tipos_problema_preferidos:
                bonus_preferencia = 0.1
            elif problema.tipo in participante.tipos_problema_evitar:
                bonus_preferencia = -0.2
            
            probabilidad = (compatibilidad * 0.4 + experiencia * 0.3 + energia * 0.15 + concentracion * 0.15 + bonus_preferencia)
            return max(0.1, min(probabilidad, 0.95))
            
        except Exception as e:
            logger.debug(f"Error calculando probabilidad simple: {e}")
            return 0.5
    
    def _estimar_tiempo_simple(self, participante: ParticipanteWrapper, problema: ProblemaWrapper) -> float:
        """Estima tiempo de resolución básico"""
        try:
            tiempo_base = problema.tiempo_limite
            compatibilidad = self._calcular_compatibilidad_simple(participante, problema)
            experiencia = min(participante.competencias_participadas / 10.0, 1.0)
            
            # Ajustar tiempo según habilidades
            factor_tiempo = 1.0 - (compatibilidad * 0.3) - (experiencia * 0.2)
            tiempo_estimado = tiempo_base * max(factor_tiempo, 0.5)
            
            return min(tiempo_estimado, participante.tiempo_maximo_disponible)
            
        except Exception as e:
            logger.debug(f"Error estimando tiempo simple: {e}")
            return 120