import numpy as np
import random
import logging
from typing import Dict
from copy import deepcopy

logger = logging.getLogger(__name__)

class IndividuoGenetico:
    """Representa una única solución candidata (un "individuo")."""
    def __init__(self, cromosoma: np.ndarray):
        self.cromosoma = cromosoma
        self.fitness = 0.0
        self.es_valido = False

class EvaluadorFitness:
    """Calcula la puntuación de calidad (fitness) de una solución."""
    def __init__(self, pesos: Dict[str, float]):
        self.pesos = pesos

    def evaluar_individuo(self, individuo, problemas, participantes, config):
        try:
            asignaciones = self._extraer_asignaciones_validas(individuo.cromosoma, problemas, participantes)
            if not asignaciones:
                individuo.fitness, individuo.es_valido = 0.0, False
                return

            num_participantes_usados = len(asignaciones)
            penalizacion_equipo_incompleto = 0.9 if num_participantes_usados < len(participantes) else 0

            tiempo_total = sum(a['tiempo_estimado'] for a in asignaciones)
            penalizacion_tiempo_excedido = 0.5 if tiempo_total > config.tiempo_total_minutos else 0

            puntuacion_norm = self._calcular_puntuacion_normalizada(asignaciones, problemas)   # <-- OBJETIVO 1: MAX PUNTUACIÓN
            compatibilidad_prom = self._calcular_compatibilidad_promedio(asignaciones)      # <-- OBJETIVO 2: MAX COMPATIBILIDAD
            tiempo_norm = self._calcular_tiempo_normalizado(asignaciones, problemas)        # <-- OBJETIVO 3: MIN TIEMPO
            balance_norm = self._calcular_balance_participantes(asignaciones, len(participantes)) # <-- OBJETIVO 4: MAX BALANCE
            
      
            fitness_base = (
                self.pesos.get('puntuacion', 0.4) * puntuacion_norm +
                self.pesos.get('compatibilidad', 0.3) * compatibilidad_prom +
                self.pesos.get('tiempo', 0.2) * tiempo_norm +
                self.pesos.get('balance', 0.1) * balance_norm
            )
            
            penalizacion_total = penalizacion_tiempo_excedido + penalizacion_equipo_incompleto
            individuo.fitness = max(0.0, fitness_base * (1 - penalizacion_total))
            individuo.es_valido = True
        except Exception:
            individuo.fitness, individuo.es_valido = 0.0, False

    def _extraer_asignaciones_validas(self, matriz, problemas, participantes):
        asignaciones = []
        participantes_usados = set()
        problemas_usados = set()
        
        for i in range(matriz.shape[0]):
            for j in range(matriz.shape[1]):
                if matriz[i, j] > 0:
                    if j in participantes_usados or i in problemas_usados:
                        continue
                    
                    problema, participante = problemas[i], participantes[j]
                    puntos = self._obtener_puntos_seguros(problema)
                    prob_exito = self._calcular_probabilidad_exito_segura(participante, problema)
                    asignaciones.append({'problema_idx': i, 'participante_idx': j, 'compatibilidad': self._calcular_compatibilidad_segura(participante, problema), 'tiempo_estimado': self._estimar_tiempo_seguro(participante, problema), 'puntuacion_esperada': puntos * prob_exito})
                    participantes_usados.add(j)
                    problemas_usados.add(i)
        return asignaciones

    def _validar_valor(self, valor, default=0.0):
        return default if valor is None or np.isnan(valor) or np.isinf(valor) else max(0.0, min(1.0, float(valor)))
    
    def _obtener_tasa_exito_participante(self, participante):
        return participante.get('tasa_exito_historica', 0.6)
    
    def _calcular_compatibilidad_segura(self, participante, problema):
        tasa_exito = self._obtener_tasa_exito_participante(participante)
        habilidades_p = participante.get('habilidades', {})
        habilidades_r = problema.get('habilidades_requeridas', {})
        if not habilidades_r: return tasa_exito
        niveles = [habilidades_p.get(h, {}).get('nivel', 0) for h in habilidades_r]
        score = sum(niveles) / len(niveles) if niveles else 0
        return self._validar_valor((tasa_exito * 0.6) + (score * 0.4))
    
    def _calcular_probabilidad_exito_segura(self, participante, problema):
        factores = {'muy_facil': 1.2, 'facil': 1.1, 'medio': 1.0, 'dificil': 0.9, 'muy_dificil': 0.8}
        factor = factores.get(problema.get('nivel_dificultad', 'medio'), 1.0)
        return self._validar_valor(self._calcular_compatibilidad_segura(participante, problema) * factor, 0.5)
    
    def _estimar_tiempo_seguro(self, participante, problema):
        return problema.get('tiempo_limite', 120) * (1.5 - self._calcular_compatibilidad_segura(participante, problema))
    
    def _obtener_puntos_seguros(self, problema):
        return problema.get('puntos_base', 100) * problema.get('multiplicador_dificultad', 1.0)
    
    def _calcular_puntuacion_normalizada(self, asignaciones, problemas):
        p_max = sum(self._obtener_puntos_seguros(p) for p in problemas)
        return sum(a['puntuacion_esperada'] for a in asignaciones) / p_max if p_max > 0 else 0
    
    def _calcular_compatibilidad_promedio(self, asignaciones):
        return np.mean([a['compatibilidad'] for a in asignaciones]) if asignaciones else 0
    
    def _calcular_tiempo_normalizado(self, asignaciones, problemas):
        t_max = sum(p.get('tiempo_limite', 120) for p in problemas)
        return max(0.0, 1.0 - (sum(a['tiempo_estimado'] for a in asignaciones) / t_max if t_max > 0 else 1.0))
    
    def _calcular_balance_participantes(self, asignaciones, total_participantes):
        return len({a['participante_idx'] for a in asignaciones}) / total_participantes if total_participantes > 0 else 0

class AlgoritmoGeneticoCoderush:
    def __init__(self, problemas, participantes, configuracion_competencia, pesos_estrategia={}, **kwargs):
        self.problemas = problemas
        self.participantes = participantes
        self.configuracion = configuracion_competencia
        self.evaluador = EvaluadorFitness(pesos_estrategia)
        self.num_problemas = len(problemas)
        self.num_participantes = len(participantes)
        self.poblacion_size = 80
        self.generaciones_max = 100
        self.prob_cruce = 0.9
        self.prob_mutacion = 0.3
        self.elite_size = max(2, int(self.poblacion_size * 0.05))
        self.torneo_size = 5
        self.max_asignaciones = min(self.num_problemas, self.num_participantes)
        
    def iniciar_optimizacion(self):
        poblacion = self.crear_poblacion()
        for ind in poblacion: self.evaluador.evaluar_individuo(ind, self.problemas, self.participantes, self.configuracion)
        
        for _ in range(self.generaciones_max):
            poblacion.sort(key=lambda x: x.fitness, reverse=True)
            nueva_poblacion = self.poda_por_elitismo(poblacion)
            while len(nueva_poblacion) < self.poblacion_size:
                padre1, padre2 = self.poda_por_seleccion(poblacion)
                hijo = self.cruza(padre1, padre2)
                self.mutacion(hijo)
                self.evaluador.evaluar_individuo(hijo, self.problemas, self.participantes, self.configuracion)
                nueva_poblacion.append(hijo)
            poblacion = nueva_poblacion
        return self.formatear_resultado_final(poblacion)

    def crear_poblacion(self):
        return [self._crear_solucion_aleatoria() for _ in range(self.poblacion_size)]

    def _crear_solucion_aleatoria(self):
        cromosoma = np.zeros((self.num_problemas, self.num_participantes), dtype=int)
        participantes_idx = list(range(self.num_participantes))
        problemas_idx = random.sample(range(self.num_problemas), self.max_asignaciones)
        for i in range(self.max_asignaciones):
            cromosoma[problemas_idx[i], participantes_idx[i]] = 1
        return IndividuoGenetico(cromosoma)

    def poda_por_seleccion(self, poblacion):
        return max(random.sample(poblacion, self.torneo_size), key=lambda x: x.fitness)
        
    def poda_por_elitismo(self, poblacion):
        return [deepcopy(ind) for ind in poblacion[:self.elite_size]]

    def cruza(self, padre1, padre2):
        punto = random.randint(1, self.num_problemas - 1) if self.num_problemas > 1 else 1
        cromosoma_hijo = np.vstack((padre1.cromosoma[:punto], padre2.cromosoma[punto:]))
        
        participantes_usados, problemas_usados = set(), set()
        for i in range(self.num_problemas):
            for j in range(self.num_participantes):
                if cromosoma_hijo[i, j] > 0:
                    if j in participantes_usados or i in problemas_usados:
                        cromosoma_hijo[i, j] = 0
                    else:
                        participantes_usados.add(j)
                        problemas_usados.add(i)
        return IndividuoGenetico(cromosoma_hijo)

    def mutacion(self, individuo):
        if random.random() < self.prob_mutacion:
            asignaciones = list(np.argwhere(individuo.cromosoma > 0))
            if len(asignaciones) >= 2:
                idx1, idx2 = random.sample(range(len(asignaciones)), 2)
                prob1, part1 = asignaciones[idx1]
                prob2, part2 = asignaciones[idx2]
                individuo.cromosoma[prob1, part1], individuo.cromosoma[prob2, part2] = 0, 0
                individuo.cromosoma[prob1, part2], individuo.cromosoma[prob2, part1] = 1, 1

    def formatear_resultado_final(self, poblacion):
        poblacion.sort(key=lambda x: x.fitness, reverse=True)
        solucion_unica = poblacion[0] if poblacion else None
        if not solucion_unica:
            return {'exito': False}
        return {'exito': True, 'mejor_solucion': self.convertir_matriz_a_json(solucion_unica, 0)}

    def convertir_matriz_a_json(self, solucion, idx):
        asignaciones = self.evaluador._extraer_asignaciones_validas(solucion.cromosoma, self.problemas, self.participantes)
        detalle_final = []
        for asig in asignaciones:
            problema = self.problemas[asig['problema_idx']]
            participante = self.participantes[asig['participante_idx']]
            detalle_final.append({'problema_nombre': problema.get('nombre'), 'participante_nombre': participante.get('nombre'), 'compatibilidad': asig['compatibilidad'], 'tiempo_estimado': asig['tiempo_estimado'], 'puntuacion_esperada': asig['puntuacion_esperada']})
        return {'solucion_id': idx + 1, 'fitness': round(solucion.fitness, 6), 'asignaciones_detalle': detalle_final}