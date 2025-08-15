import numpy as np
import random
import logging
from typing import Dict, List
from copy import deepcopy

logger = logging.getLogger(__name__)

class IndividuoGenetico:
    def __init__(self, cromosoma: np.ndarray):
        self.cromosoma = cromosoma
        self.fitness = 0.0
        self.es_valido = False
        self.metricas_detalladas = {}

class EvaluadorFitness:
    def __init__(self):
        # ✅ PESOS ADAPTATIVOS: Se calculan dinámicamente según los datos
        self.pesos_base = {
            'puntuacion': 0.4,
            'fortalezas_individuales': 0.3,
            'cantidad_problemas': 0.2,
            'tiempo_total': 0.1
        }
        
        logger.info("Evaluador inicializado con pesos adaptativos")

    def _calcular_pesos_dinamicos(self, problemas, participantes):
        """Calcula pesos dinámicamente según las características de los datos"""
        # Análisis de diversidad de dificultades
        dificultades = [p.get('nivel_dificultad', 'medio') for p in problemas]
        diversidad_dificultad = len(set(dificultades)) / len(dificultades) if dificultades else 0.5
        
        # Análisis de dispersión de habilidades
        experiencias = [p.get('experiencia_anos', 2) for p in participantes]
        dispersión_experiencia = np.std(experiencias) / np.mean(experiencias) if experiencias else 0.5
        
        # Ajustar pesos dinámicamente
        factor_complejidad = (diversidad_dificultad + dispersión_experiencia) / 2
        
        return {
            'puntuacion': self.pesos_base['puntuacion'] * (1 + factor_complejidad * 0.2),
            'fortalezas_individuales': self.pesos_base['fortalezas_individuales'] * (1 + (1-factor_complejidad) * 0.3),
            'cantidad_problemas': self.pesos_base['cantidad_problemas'],
            'tiempo_total': self.pesos_base['tiempo_total'] * (1 + factor_complejidad * 0.1)
        }

    def _parsear_habilidades_requeridas(self, habilidades_str: str) -> Dict[str, float]:
        """Parsea habilidades requeridas de forma robusta"""
        habilidades = {}
        if not habilidades_str or str(habilidades_str) == 'nan':
            return {'algoritmos_basicos': 0.5}
        
        try:
            for par in str(habilidades_str).split(';'):
                if ':' in par:
                    habilidad, nivel = par.split(':')
                    habilidades[habilidad.strip()] = float(nivel)
        except:
            habilidades['algoritmos_basicos'] = 0.5
        return habilidades

    def _calcular_compatibilidad_pura(self, participante: Dict, problema: Dict) -> float:
        """Compatibilidad pura basada solo en datos reales, sin factores artificiales"""
        habilidades_req = self._parsear_habilidades_requeridas(problema['habilidades_requeridas'])
        
        # Solo datos reales del CSV
        habilidad_principal = participante['habilidad_principal']
        nivel_habilidad = participante['nivel_habilidad']
        tasa_exito_historica = participante['tasa_exito_historica']
        
        # Compatibilidad directa de habilidades
        compatibilidad_habilidad = 0.0
        if habilidad_principal in habilidades_req:
            compatibilidad_habilidad = nivel_habilidad * habilidades_req[habilidad_principal]
        elif habilidad_principal == problema['tipo']:
            compatibilidad_habilidad = nivel_habilidad * 0.9
        else:
            # Compatibilidad cruzada basada en experiencia general
            compatibilidad_habilidad = nivel_habilidad * 0.6
        
        # Factor de experiencia histórica real
        factor_experiencia = tasa_exito_historica
        
        # ✅ COMBINACIÓN PURA: Solo promedio ponderado, sin artificios
        compatibilidad = (
            0.7 * compatibilidad_habilidad +
            0.3 * factor_experiencia
        )
        
        return max(0.0, min(1.0, compatibilidad))

    def _calcular_probabilidad_exito_real(self, participante: Dict, problema: Dict) -> float:
        """Probabilidad basada únicamente en datos históricos reales"""
        tasa_base = participante['tasa_exito_historica']
        experiencia_anos = participante['experiencia_anos']
        competencias = participante['competencias_participadas']
        problemas_resueltos = participante['problemas_resueltos_total']
        
        # Factor de experiencia acumulada (datos reales)
        experiencia_normalizada = min(1.0, experiencia_anos / 10.0)
        competencias_normalizadas = min(1.0, competencias / 20.0)
        problemas_normalizados = min(1.0, problemas_resueltos / 200.0)
        
        factor_experiencia_total = (
            experiencia_normalizada + competencias_normalizadas + problemas_normalizados
        ) / 3.0
        
        # Compatibilidad con el problema
        compatibilidad = self._calcular_compatibilidad_pura(participante, problema)
        
        # Dificultad histórica del problema
        tasa_problema_historica = problema.get('tasa_resolucion_historica', 0.5)
        
        # ✅ CÁLCULO PURO: Solo promedios ponderados de datos reales
        probabilidad = (
            0.4 * tasa_base +
            0.3 * factor_experiencia_total +
            0.2 * compatibilidad +
            0.1 * tasa_problema_historica
        )
        
        return max(0.1, min(0.9, probabilidad))

    def _estimar_tiempo_real(self, participante: Dict, problema: Dict) -> float:
        """Estimación basada en datos reales sin factores artificiales"""
        tiempo_limite_problema = problema['tiempo_limite']
        
        # Factores reales de velocidad
        experiencia_anos = participante['experiencia_anos']
        problemas_resueltos = participante['problemas_resueltos_total']
        
        # ✅ FACTORES PUROS: Basados en relaciones matemáticas simples
        # Más experiencia = mayor velocidad (menos tiempo)
        factor_experiencia = max(0.5, 1.0 - (experiencia_anos / 15.0))
        factor_practica = max(0.5, 1.0 - (problemas_resueltos / 400.0))
        
        # Compatibilidad afecta velocidad de resolución
        compatibilidad = self._calcular_compatibilidad_pura(participante, problema)
        factor_dificultad_personal = max(0.6, 1.4 - compatibilidad)
        
        # ✅ TIEMPO ESTIMADO PURO
        tiempo_estimado = tiempo_limite_problema * 0.7 * (
            0.4 * factor_experiencia +
            0.4 * factor_practica +
            0.2 * factor_dificultad_personal
        )
        
        # Límites realistas basados en el tiempo del problema
        tiempo_minimo = tiempo_limite_problema * 0.2
        tiempo_maximo = tiempo_limite_problema * 0.8
        
        return max(tiempo_minimo, min(tiempo_maximo, tiempo_estimado))

    def _calcular_puntuacion_esperada_pura(self, participante: Dict, problema: Dict) -> float:
        """Puntuación esperada basada solo en probabilidad real de éxito"""
        puntos_base = problema['puntos_base']
        multiplicador = problema['multiplicador_dificultad']
        
        # ✅ PUNTUACIÓN PURA: Solo multiplicación directa
        puntuacion_maxima = puntos_base * multiplicador
        probabilidad_exito = self._calcular_probabilidad_exito_real(participante, problema)
        
        return puntuacion_maxima * probabilidad_exito

    def evaluar_individuo(self, individuo, problemas, participantes, config):
        """Evaluación que considera trabajo en paralelo real"""
        try:
            # Calcular pesos dinámicos para esta evaluación
            pesos_dinamicos = self._calcular_pesos_dinamicos(problemas, participantes)
            
            asignaciones = self._extraer_asignaciones_validas(individuo.cromosoma, problemas, participantes)
            if not asignaciones:
                individuo.fitness, individuo.es_valido = 0.0, False
                return

            # ✅ CALCULAR POR PARTICIPANTE (trabajo en paralelo)
            asignaciones_enriquecidas = []
            asignaciones_por_participante = {}
            
            for asig in asignaciones:
                participante = participantes[asig['participante_idx']]
                problema = problemas[asig['problema_idx']]
                
                # Agrupar por participante
                p_idx = asig['participante_idx']
                if p_idx not in asignaciones_por_participante:
                    asignaciones_por_participante[p_idx] = []
                
                asig_calculada = {
                    **asig,
                    'compatibilidad': self._calcular_compatibilidad_pura(participante, problema),
                    'tiempo_estimado': self._estimar_tiempo_real(participante, problema),
                    'probabilidad_exito': self._calcular_probabilidad_exito_real(participante, problema),
                    'puntuacion_esperada': self._calcular_puntuacion_esperada_pura(participante, problema)
                }
                
                asignaciones_enriquecidas.append(asig_calculada)
                asignaciones_por_participante[p_idx].append(asig_calculada)

            # ✅ VALIDAR QUE USE EL TAMAÑO DE EQUIPO CORRECTO
            participantes_usados = len(asignaciones_por_participante)
            participantes_esperados = min(config.tamanio_equipo, len(asignaciones))
            
            # Factor de utilización de equipo
            if participantes_usados < participantes_esperados:
                factor_utilizacion = participantes_usados / participantes_esperados
            else:
                factor_utilizacion = 1.0

            # ✅ CALCULAR TIEMPO EN PARALELO (NO SECUENCIAL)
            tiempos_por_participante = {}
            for p_idx, asigs_participante in asignaciones_por_participante.items():
                tiempo_total_participante = sum(a['tiempo_estimado'] for a in asigs_participante)
                tiempos_por_participante[p_idx] = tiempo_total_participante
            
            # ✅ TIEMPO TOTAL = MÁXIMO TIEMPO DE CUALQUIER PARTICIPANTE
            tiempo_total_paralelo = max(tiempos_por_participante.values()) if tiempos_por_participante else 0

            # ✅ VALIDACIÓN DE TIEMPO EN PARALELO
            if tiempo_total_paralelo > config.tiempo_total_minutos:
                individuo.fitness = 0.0
                individuo.es_valido = False
                return
            
            # ===================================================================
            # ✅ OBJETIVOS PUROS PARA TRABAJO EN PARALELO
            # ===================================================================
            
            # 1. Puntuación total esperada
            puntuacion_total = sum(a['puntuacion_esperada'] for a in asignaciones_enriquecidas)
            puntuacion_maxima_teorica = sum(p['puntos_base'] * p['multiplicador_dificultad'] for p in problemas)
            obj_puntuacion = puntuacion_total / puntuacion_maxima_teorica if puntuacion_maxima_teorica > 0 else 0
            
            # 2. Fortalezas individuales
            compatibilidades = [a['compatibilidad'] for a in asignaciones_enriquecidas]
            obj_fortalezas = np.mean(compatibilidades) if compatibilidades else 0
            
            # 3. Cantidad de problemas esperados
            problemas_esperados = sum(a['probabilidad_exito'] for a in asignaciones_enriquecidas)
            obj_cantidad = problemas_esperados / len(problemas) if problemas else 0
            
            # 4. ✅ EFICIENCIA TEMPORAL EN PARALELO
            eficiencia_temporal = max(0.0, 1.0 - (tiempo_total_paralelo / config.tiempo_total_minutos))
            obj_tiempo = eficiencia_temporal
            
            # ✅ BONUS POR UTILIZACIÓN DE EQUIPO COMPLETO
            bonus_equipo = factor_utilizacion * 0.1
            
            # ✅ BONUS POR BALANCE DE CARGA
            if len(tiempos_por_participante) > 1:
                tiempos = list(tiempos_por_participante.values())
                cv_tiempos = np.std(tiempos) / np.mean(tiempos) if np.mean(tiempos) > 0 else 1.0
                bonus_balance = max(0.0, (1.0 - cv_tiempos)) * 0.05
            else:
                bonus_balance = 0.0
            
            # ✅ FITNESS FINAL CON BONIFICACIONES POR TRABAJO EN EQUIPO
            fitness_base = (
                pesos_dinamicos['puntuacion'] * obj_puntuacion +
                pesos_dinamicos['fortalezas_individuales'] * obj_fortalezas +
                pesos_dinamicos['cantidad_problemas'] * obj_cantidad +
                pesos_dinamicos['tiempo_total'] * obj_tiempo
            )
            
            fitness_final = fitness_base + bonus_equipo + bonus_balance
            
            individuo.fitness = fitness_final
            individuo.es_valido = True
            
            # Métricas detalladas
            individuo.metricas_detalladas = {
                'puntuacion_total': puntuacion_total,
                'obj_puntuacion': obj_puntuacion,
                'obj_fortalezas': obj_fortalezas,
                'obj_cantidad': obj_cantidad,
                'obj_tiempo': obj_tiempo,
                'participantes_utilizados': participantes_usados,
                'participantes_esperados': participantes_esperados,
                'factor_utilizacion': factor_utilizacion,
                'tiempo_total_paralelo': tiempo_total_paralelo,
                'tiempos_por_participante': tiempos_por_participante,
                'bonus_equipo': bonus_equipo,
                'bonus_balance': bonus_balance,
                'pesos_utilizados': pesos_dinamicos
            }
            
        except Exception as e:
            logger.error(f"Error en evaluación: {e}", exc_info=True)
            individuo.fitness, individuo.es_valido = 0.0, False

    def _extraer_asignaciones_validas(self, matriz, problemas, participantes):
        """Extrae asignaciones válidas de la matriz cromosómica"""
        asignaciones = []
        problemas_usados = set()
        
        for i in range(matriz.shape[0]):
            for j in range(matriz.shape[1]):
                if matriz[i,j] > 0 and i not in problemas_usados:
                    asignaciones.append({
                        'problema_idx': i,
                        'participante_idx': j
                    })
                    problemas_usados.add(i)
        
        return asignaciones

class AlgoritmoGeneticoCoderush:
    def __init__(self, problemas, participantes, configuracion_competencia):
        self.problemas = problemas
        self.participantes = participantes
        self.configuracion = configuracion_competencia
        self.evaluador = EvaluadorFitness()
        
        self.num_problemas = len(problemas)
        self.num_participantes = len(participantes)
        
        # ✅ PARÁMETROS ADAPTATIVOS: Se calculan según el tamaño del problema
        self.poblacion_size = max(80, min(self.num_problemas * self.num_participantes * 3, 200))
        self.generaciones_max = max(120, self.poblacion_size)
        self.prob_cruce = 0.50
        self.prob_mutacion = 0.15
        self.elite_size = max(5, int(self.poblacion_size * 0.08))
        self.torneo_size = max(3, int(self.poblacion_size * 0.05))
        
        self.historial_fitness = []
        
        logger.info(f"Algoritmo con trabajo en paralelo - Población: {self.poblacion_size}")
        logger.info(f"Generaciones: {self.generaciones_max}, Tamaño equipo: {configuracion_competencia.tamanio_equipo}")

    def iniciar_optimizacion(self):
        """Ejecuta el algoritmo genético con trabajo en paralelo"""
        logger.info("Iniciando optimización con trabajo en paralelo real")
        
        self.historial_fitness = []
        poblacion = self._crear_poblacion_inicial()
        self._evaluar_poblacion(poblacion)
        
        for generacion in range(self.generaciones_max):
            poblacion.sort(key=lambda x: x.fitness, reverse=True)
            
            # Registrar progreso cada 20 generaciones
            if generacion % 20 == 0:
                mejor_fitness = poblacion[0].fitness
                fitness_promedio = np.mean([ind.fitness for ind in poblacion])
                
                self.historial_fitness.append({
                    'generacion': generacion,
                    'mejor_fitness': mejor_fitness,
                    'fitness_promedio': fitness_promedio
                })
                
                # Log de participantes utilizados
                if poblacion[0].metricas_detalladas:
                    participantes_usados = poblacion[0].metricas_detalladas.get('participantes_utilizados', 0)
                    logger.info(f"Generación {generacion}: Fitness={mejor_fitness:.4f}, Participantes={participantes_usados}")
                else:
                    logger.info(f"Generación {generacion}: Fitness={mejor_fitness:.4f}")
            
            # Crear nueva generación
            nueva_poblacion = self._aplicar_elitismo(poblacion)
            
            while len(nueva_poblacion) < self.poblacion_size:
                padre1 = self._seleccion_por_torneo(poblacion)
                padre2 = self._seleccion_por_torneo(poblacion)
                
                hijo = self._cruza(padre1, padre2)
                self._mutacion(hijo)
                
                self.evaluador.evaluar_individuo(hijo, self.problemas, 
                                               self.participantes, self.configuracion)
                nueva_poblacion.append(hijo)
            
            poblacion = nueva_poblacion
        
        return self._formatear_resultado_final(poblacion)

    def _crear_poblacion_inicial(self):
        """Crea población inicial con múltiples estrategias"""
        poblacion = []
        estrategias = ['aleatorio', 'por_experiencia', 'balanceado', 'por_compatibilidad']
        
        for i in range(self.poblacion_size):
            estrategia = estrategias[i % len(estrategias)]
            individuo = self._crear_individuo_con_estrategia(estrategia)
            poblacion.append(individuo)
        
        return poblacion

    def _crear_individuo_con_estrategia(self, estrategia):
        """Crea individuo FORZANDO uso de múltiples participantes"""
        cromosoma = np.zeros((self.num_problemas, self.num_participantes), dtype=int)
        
        # ✅ ASIGNAR MÁS PROBLEMAS para forzar uso de múltiples participantes
        min_problemas = max(3, self.num_problemas // 2)
        max_problemas = min(self.num_problemas, self.num_problemas * 3 // 4)
        num_asignar = random.randint(min_problemas, max_problemas)
        problemas_elegidos = random.sample(range(self.num_problemas), num_asignar)
        
        if estrategia == 'aleatorio':
            for i in problemas_elegidos:
                j = random.randint(0, self.num_participantes - 1)
                cromosoma[i, j] = 1
                
        elif estrategia == 'por_experiencia':
            participantes_ord = sorted(range(self.num_participantes), 
                                     key=lambda i: self.participantes[i]['experiencia_anos'] + 
                                                  self.participantes[i]['competencias_participadas'], 
                                     reverse=True)
            # ✅ FORZAR DIVERSIDAD: Rotar entre participantes
            for idx, i in enumerate(problemas_elegidos):
                idx_participante = idx % len(participantes_ord)
                j = participantes_ord[idx_participante]
                cromosoma[i, j] = 1
                
        elif estrategia == 'balanceado':
            # ✅ ESTRATEGIA MEJORADA: Distribuir uniformemente
            carga = [0] * self.num_participantes
            for i in problemas_elegidos:
                # Siempre asignar al participante con menor carga
                min_carga = min(carga)
                candidatos = [idx for idx, c in enumerate(carga) if c == min_carga]
                j = random.choice(candidatos)
                cromosoma[i, j] = 1
                carga[j] += 1
                
        else:  # por_compatibilidad con distribución
            # ✅ DISTRIBUCIÓN FORZADA: Asegurar que varios participantes trabajen
            participantes_usados = set()
            for i in problemas_elegidos:
                problema = self.problemas[i]
                
                # Si ya usamos suficientes participantes, continuar con compatibilidad normal
                if len(participantes_usados) >= min(6, self.num_participantes):
                    compatibilidades = []
                    for j in range(self.num_participantes):
                        participante = self.participantes[j]
                        comp = self.evaluador._calcular_compatibilidad_pura(participante, problema)
                        compatibilidades.append((j, comp))
                    
                    compatibilidades.sort(key=lambda x: x[1], reverse=True)
                    top_50_pct = max(1, len(compatibilidades) // 2)
                    j, _ = random.choice(compatibilidades[:top_50_pct])
                else:
                    # Forzar uso de participante nuevo
                    participantes_disponibles = list(set(range(self.num_participantes)) - participantes_usados)
                    if participantes_disponibles:
                        j = random.choice(participantes_disponibles)
                    else:
                        j = random.randint(0, self.num_participantes - 1)
                
                cromosoma[i, j] = 1
                participantes_usados.add(j)
        
        return IndividuoGenetico(cromosoma)

    def _evaluar_poblacion(self, poblacion):
        """Evalúa toda la población"""
        for individuo in poblacion:
            self.evaluador.evaluar_individuo(individuo, self.problemas, 
                                           self.participantes, self.configuracion)

    def _seleccion_por_torneo(self, poblacion):
        """Selección por torneo"""
        candidatos = random.sample(poblacion, min(self.torneo_size, len(poblacion)))
        return max(candidatos, key=lambda x: x.fitness)

    def _aplicar_elitismo(self, poblacion):
        """Preserva los mejores individuos"""
        return [deepcopy(ind) for ind in poblacion[:self.elite_size]]

    def _cruza(self, padre1, padre2):
        """Cruza uniforme con reparación"""
        if random.random() > self.prob_cruce:
            return deepcopy(padre1 if random.random() < 0.5 else padre2)
        
        # Cruza uniforme: cada gen se toma aleatoriamente de un padre
        cromosoma_hijo = np.zeros_like(padre1.cromosoma)
        for i in range(cromosoma_hijo.shape[0]):
            for j in range(cromosoma_hijo.shape[1]):
                if random.random() < 0.5:
                    cromosoma_hijo[i, j] = padre1.cromosoma[i, j]
                else:
                    cromosoma_hijo[i, j] = padre2.cromosoma[i, j]
        
        cromosoma_reparado = self._reparar_cromosoma(cromosoma_hijo)
        return IndividuoGenetico(cromosoma_reparado)

    def _mutacion(self, individuo):
        """Mutación adaptativa"""
        if random.random() > self.prob_mutacion:
            return
        
        tipos_mutacion = ['intercambio', 'reasignacion', 'agregar', 'quitar']
        tipo = random.choice(tipos_mutacion)
        
        if tipo == 'intercambio':
            asignaciones = list(np.argwhere(individuo.cromosoma > 0))
            if len(asignaciones) >= 2:
                idx1, idx2 = random.sample(range(len(asignaciones)), 2)
                prob1, part1 = asignaciones[idx1]
                prob2, part2 = asignaciones[idx2]
                
                individuo.cromosoma[prob1, part1] = 0
                individuo.cromosoma[prob2, part2] = 0
                individuo.cromosoma[prob1, part2] = 1
                individuo.cromosoma[prob2, part1] = 1
                
        elif tipo == 'reasignacion':
            asignaciones = list(np.argwhere(individuo.cromosoma > 0))
            if asignaciones:
                prob_idx, _ = random.choice(asignaciones)
                individuo.cromosoma[prob_idx, :] = 0
                nuevo_participante = random.randint(0, self.num_participantes - 1)
                individuo.cromosoma[prob_idx, nuevo_participante] = 1
                
        elif tipo == 'agregar':
            problemas_sin_asignar = []
            for i in range(self.num_problemas):
                if np.sum(individuo.cromosoma[i, :]) == 0:
                    problemas_sin_asignar.append(i)
            
            if problemas_sin_asignar:
                prob_idx = random.choice(problemas_sin_asignar)
                participante = random.randint(0, self.num_participantes - 1)
                individuo.cromosoma[prob_idx, participante] = 1
                
        else:  # quitar
            asignaciones = list(np.argwhere(individuo.cromosoma > 0))
            if len(asignaciones) > 1:  # Mantener al menos una asignación
                prob_idx, part_idx = random.choice(asignaciones)
                individuo.cromosoma[prob_idx, part_idx] = 0

    def _reparar_cromosoma(self, cromosoma):
        """Repara cromosoma para cumplir restricciones básicas"""
        cromosoma_reparado = cromosoma.copy()
        
        # Asegurar que cada problema tenga máximo un participante
        for i in range(self.num_problemas):
            asignaciones = np.where(cromosoma_reparado[i, :] > 0)[0]
            
            if len(asignaciones) > 1:
                # Mantener solo una asignación aleatoria
                elegido = random.choice(asignaciones)
                cromosoma_reparado[i, :] = 0
                cromosoma_reparado[i, elegido] = 1
        
        return cromosoma_reparado

    def _formatear_resultado_final(self, poblacion):
        """Formatea el resultado final garantizando diversidad"""
        poblacion.sort(key=lambda x: x.fitness, reverse=True)
        soluciones_validas = [ind for ind in poblacion if ind.es_valido]
        
        if not soluciones_validas:
            return {'exito': False, 'mensaje': 'No se encontró solución válida'}
        
        # ✅ SELECCIÓN DIVERSA CON UMBRAL MUY ESTRICTO
        top_3 = [soluciones_validas[0]]
        
        # ✅ DEBUG: Log de la primera solución
        primera_asignaciones = self.evaluador._extraer_asignaciones_validas(soluciones_validas[0].cromosoma, self.problemas, self.participantes)
        logger.info(f"🥇 SOLUCIÓN 1 - Fitness: {soluciones_validas[0].fitness:.4f}")
        logger.info(f"   Asignaciones: {[(self.problemas[a['problema_idx']]['nombre'][:15], self.participantes[a['participante_idx']]['nombre']) for a in primera_asignaciones[:3]]}")
        
        for idx, solucion in enumerate(soluciones_validas[1:min(50, len(soluciones_validas))], 2):  # ✅ Buscar en más candidatos
            if len(top_3) >= 3:
                break
            
            # ✅ DEBUG: Log de cada candidato
            candidato_asignaciones = self.evaluador._extraer_asignaciones_validas(solucion.cromosoma, self.problemas, self.participantes)
            logger.info(f"🔍 CANDIDATO {idx} - Fitness: {solucion.fitness:.4f}")
            logger.info(f"   Asignaciones: {[(self.problemas[a['problema_idx']]['nombre'][:15], self.participantes[a['participante_idx']]['nombre']) for a in candidato_asignaciones[:3]]}")
            
            # ✅ UMBRAL EXTREMADAMENTE ESTRICTO + VERIFICACIÓN ADICIONAL
            es_diferente = True
            for existente_idx, existente in enumerate(top_3):
                similitud = self._calcular_similitud(solucion.cromosoma, existente.cromosoma)
                
                # ✅ DEBUG: Log de similitud
                logger.info(f"   Similitud con solución {existente_idx + 1}: {similitud:.4f}")
                
                # ✅ DOBLE VERIFICACIÓN: Similitud + Asignaciones diferentes
                asignaciones_nueva = self.evaluador._extraer_asignaciones_validas(solucion.cromosoma, self.problemas, self.participantes)
                asignaciones_existente = self.evaluador._extraer_asignaciones_validas(existente.cromosoma, self.problemas, self.participantes)
                
                # Comparar asignaciones directamente
                asignaciones_diferentes = len(asignaciones_nueva) != len(asignaciones_existente)
                if not asignaciones_diferentes:
                    # Verificar si al menos 2 asignaciones son diferentes
                    diferencias = 0
                    for asig_nueva in asignaciones_nueva:
                        encontrada = False
                        for asig_exist in asignaciones_existente:
                            if (asig_nueva['problema_idx'] == asig_exist['problema_idx'] and 
                                asig_nueva['participante_idx'] == asig_exist['participante_idx']):
                                encontrada = True
                                break
                        if not encontrada:
                            diferencias += 1
                    
                    asignaciones_diferentes = diferencias >= 2  # Al menos 2 asignaciones diferentes
                
                # ✅ DEBUG: Log de verificación de asignaciones
                logger.info(f"   Asignaciones diferentes: {asignaciones_diferentes} (diferencias: {diferencias if 'diferencias' in locals() else 'N/A'})")
                
                # Si similitud > 0.1 O las asignaciones son muy similares, rechazar
                if similitud > 0.1 or not asignaciones_diferentes:
                    es_diferente = False
                    logger.info(f"   ❌ RECHAZADO - Similitud: {similitud:.4f} > 0.1 o asignaciones similares")
                    break
                else:
                    logger.info(f"   ✅ DIFERENTE - Similitud: {similitud:.4f} <= 0.1 y asignaciones diferentes")
            
            if es_diferente:
                top_3.append(solucion)
                logger.info(f"🎯 SOLUCIÓN {len(top_3)} AGREGADA - Fitness: {solucion.fitness:.4f}")
            
        # ✅ SI AÚN NO HAY DIVERSIDAD, FORZAR SOLUCIONES DIFERENTES
        if len(top_3) < 3:
            logger.info(f"⚠️ FORZANDO DIVERSIDAD - Solo {len(top_3)} soluciones encontradas")
            # Crear soluciones artificialmente diferentes
            for i in range(len(top_3), min(3, len(soluciones_validas))):
                if i < len(soluciones_validas):
                    candidato = soluciones_validas[i]
                    # Forzar que sea diferente modificando ligeramente
                    candidato_modificado = self._forzar_diferencia(candidato, top_3)
                    top_3.append(candidato_modificado)
                    logger.info(f"🔧 SOLUCIÓN FORZADA {len(top_3)} - Fitness: {candidato_modificado.fitness:.4f}")
        
        # ✅ LOGGING PARA DEBUG FINAL
        fitness_values = [round(s.fitness, 4) for s in top_3]
        participantes_por_solucion = [s.metricas_detalladas.get('participantes_utilizados', 0) for s in top_3]
        logger.info(f"🏆 TOP 3 FINAL - Fitness: {fitness_values}")
        logger.info(f"🏆 TOP 3 FINAL - Participantes: {participantes_por_solucion}")
        
        # ✅ DEBUG: Verificar que las asignaciones finales sean diferentes
        for i, solucion in enumerate(top_3):
            asignaciones = self.evaluador._extraer_asignaciones_validas(solucion.cromosoma, self.problemas, self.participantes)
            logger.info(f"🏆 SOLUCIÓN {i+1} FINAL:")
            for j, asig in enumerate(asignaciones[:5]):  # Mostrar primeras 5
                problema_nombre = self.problemas[asig['problema_idx']]['nombre'][:20]
                participante_nombre = self.participantes[asig['participante_idx']]['nombre']
                logger.info(f"   {j+1}. {problema_nombre} → {participante_nombre}")
        
        mejores_soluciones = {}
        for i, solucion in enumerate(top_3):
            mejores_soluciones[f'solucion_{i+1}'] = self._convertir_a_json(solucion, i)
        
        return {
            'exito': True,
            'mejores_soluciones': mejores_soluciones,
            'historial': self.historial_fitness,
            'estadisticas_finales': {
                'generaciones_ejecutadas': self.generaciones_max,
                'mejor_fitness': top_3[0].fitness,
                'fitness_promedio': np.mean([ind.fitness for ind in poblacion]),
                'soluciones_validas': len(soluciones_validas),
                'diversidad_lograda': len(top_3),
                'participantes_utilizados_mejor': top_3[0].metricas_detalladas.get('participantes_utilizados', 0),
                'tiempo_paralelo_mejor': top_3[0].metricas_detalladas.get('tiempo_total_paralelo', 0)
            }
        }

    def _forzar_diferencia(self, solucion_base, soluciones_existentes):
        """Fuerza que una solución sea diferente modificando asignaciones"""
        nuevo_cromosoma = solucion_base.cromosoma.copy()
        
        # Obtener asignaciones actuales
        asignaciones_actuales = self.evaluador._extraer_asignaciones_validas(nuevo_cromosoma, self.problemas, self.participantes)
        
        if len(asignaciones_actuales) >= 2:
            # Intercambiar 2 asignaciones para forzar diferencia
            idx1, idx2 = random.sample(range(len(asignaciones_actuales)), 2)
            asig1 = asignaciones_actuales[idx1]
            asig2 = asignaciones_actuales[idx2]
            
            # Intercambiar participantes
            nuevo_cromosoma[asig1['problema_idx'], asig1['participante_idx']] = 0
            nuevo_cromosoma[asig2['problema_idx'], asig2['participante_idx']] = 0
            nuevo_cromosoma[asig1['problema_idx'], asig2['participante_idx']] = 1
            nuevo_cromosoma[asig2['problema_idx'], asig1['participante_idx']] = 1
        
        # Crear nuevo individuo y evaluarlo
        nuevo_individuo = IndividuoGenetico(nuevo_cromosoma)
        self.evaluador.evaluar_individuo(nuevo_individuo, self.problemas, self.participantes, self.configuracion)
        
        return nuevo_individuo

    def _calcular_similitud(self, cromosoma1, cromosoma2):
        """Calcula similitud entre cromosomas"""
        diferencias = np.sum(cromosoma1 != cromosoma2)
        similitud = 1 - (diferencias / cromosoma1.size)
        return similitud

    def _convertir_a_json(self, individuo, indice):
        """Convierte individuo a formato JSON con métricas de trabajo en paralelo"""
        asignaciones = self.evaluador._extraer_asignaciones_validas(
            individuo.cromosoma, self.problemas, self.participantes
        )
        
        detalle_asignaciones = []
        for asig in asignaciones:
            problema = self.problemas[asig['problema_idx']]
            participante = self.participantes[asig['participante_idx']]
            
            # Recalcular métricas
            compatibilidad = self.evaluador._calcular_compatibilidad_pura(participante, problema)
            tiempo_estimado = self.evaluador._estimar_tiempo_real(participante, problema)
            puntuacion_esperada = self.evaluador._calcular_puntuacion_esperada_pura(participante, problema)
            
            detalle_asignaciones.append({
                'problema_nombre': problema['nombre'],
                'participante_nombre': participante['nombre'],
                'compatibilidad': round(compatibilidad, 3),
                'tiempo_estimado': round(tiempo_estimado, 1),
                'puntuacion_esperada': round(puntuacion_esperada, 2)
            })
        
        return {
            'solucion_id': indice + 1,
            'fitness': round(individuo.fitness, 6),
            'nombre_estrategia': f"Estrategia Optimizada {indice + 1}",
            'asignaciones_detalle': detalle_asignaciones,
            'metrica_transparencia': {
                'pesos_utilizados': individuo.metricas_detalladas.get('pesos_utilizados', {}),
                'num_asignaciones': len(asignaciones),
                'algoritmo_trabajo_paralelo': True,
                'participantes_utilizados': individuo.metricas_detalladas.get('participantes_utilizados', 0),
                'tiempo_total_paralelo': round(individuo.metricas_detalladas.get('tiempo_total_paralelo', 0), 1),
                'factor_utilizacion_equipo': round(individuo.metricas_detalladas.get('factor_utilizacion', 0), 3),
                'bonus_equipo': round(individuo.metricas_detalladas.get('bonus_equipo', 0), 3),
                'bonus_balance': round(individuo.metricas_detalladas.get('bonus_balance', 0), 3),
                'metricas_detalladas': individuo.metricas_detalladas
            }
        }