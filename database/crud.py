from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc
from typing import List, Optional, Dict, Any
from database.models import Participante, Problema, Asignacion
import uuid

# ============================================================================
# CRUD PARTICIPANTES
# ============================================================================

class CRUDParticipante:
    
    def create(self, db: Session, participante_data: Dict[str, Any]) -> Participante:
        """Crear nuevo participante"""
        participante = Participante(**participante_data)
        db.add(participante)
        db.commit()
        db.refresh(participante)
        return participante
    
    def get(self, db: Session, participante_id: int) -> Optional[Participante]:
        """Obtener participante por ID"""
        return db.query(Participante).filter(Participante.id == participante_id).first()
    
    def get_by_email(self, db: Session, email: str) -> Optional[Participante]:
        """Obtener participante por email"""
        return db.query(Participante).filter(Participante.email == email).first()
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[Participante]:
        """Obtener todos los participantes"""
        return db.query(Participante).offset(skip).limit(limit).all()
    
    def get_available(self, db: Session) -> List[Participante]:
        """Obtener participantes disponibles"""
        return db.query(Participante).filter(Participante.disponibilidad == True).all()
    
    def get_by_universidad(self, db: Session, universidad: str) -> List[Participante]:
        """Obtener participantes por universidad"""
        return db.query(Participante).filter(Participante.universidad == universidad).all()
    
    def search_by_habilidad(self, db: Session, habilidad: str, nivel_minimo: float = 0.0) -> List[Participante]:
        """Buscar participantes por habilidad específica"""
        # Usar JSON path para buscar en habilidades
        return db.query(Participante).filter(
            Participante.habilidades[habilidad]['nivel'].astext.cast(db.Float) >= nivel_minimo
        ).all()
    
    def update(self, db: Session, participante_id: int, update_data: Dict[str, Any]) -> Optional[Participante]:
        """Actualizar participante"""
        participante = self.get(db, participante_id)
        if participante:
            for field, value in update_data.items():
                setattr(participante, field, value)
            db.commit()
            db.refresh(participante)
        return participante
    
    def delete(self, db: Session, participante_id: int) -> bool:
        """Eliminar participante"""
        participante = self.get(db, participante_id)
        if participante:
            db.delete(participante)
            db.commit()
            return True
        return False
    
    def get_estadisticas(self, db: Session) -> Dict[str, Any]:
        """Obtener estadísticas de participantes"""
        total = db.query(Participante).count()
        disponibles = db.query(Participante).filter(Participante.disponibilidad == True).count()
        
        # Promedio de experiencia
        avg_competencias = db.query(db.func.avg(Participante.competencias_participadas)).scalar() or 0
        avg_tasa_exito = db.query(db.func.avg(Participante.tasa_exito_historica)).scalar() or 0
        
        return {
            'total_participantes': total,
            'participantes_disponibles': disponibles,
            'promedio_competencias': round(avg_competencias, 2),
            'promedio_tasa_exito': round(avg_tasa_exito, 3)
        }

# ============================================================================
# CRUD PROBLEMAS
# ============================================================================

class CRUDProblema:
    
    def create(self, db: Session, problema_data: Dict[str, Any]) -> Problema:
        """Crear nuevo problema"""
        problema = Problema(**problema_data)
        db.add(problema)
        db.commit()
        db.refresh(problema)
        return problema
    
    def get(self, db: Session, problema_id: int) -> Optional[Problema]:
        """Obtener problema por ID"""
        return db.query(Problema).filter(Problema.id == problema_id).first()
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[Problema]:
        """Obtener todos los problemas"""
        return db.query(Problema).offset(skip).limit(limit).all()
    
    def get_by_tipo(self, db: Session, tipo: str) -> List[Problema]:
        """Obtener problemas por tipo"""
        return db.query(Problema).filter(Problema.tipo == tipo).all()
    
    def get_by_dificultad(self, db: Session, dificultad: str) -> List[Problema]:
        """Obtener problemas por nivel de dificultad"""
        return db.query(Problema).filter(Problema.nivel_dificultad == dificultad).all()
    
    def get_by_fuente(self, db: Session, fuente: str) -> List[Problema]:
        """Obtener problemas por fuente"""
        return db.query(Problema).filter(Problema.fuente == fuente).all()
    
    def get_by_puntos_range(self, db: Session, min_puntos: int, max_puntos: int) -> List[Problema]:
        """Obtener problemas por rango de puntos"""
        return db.query(Problema).filter(
            and_(
                Problema.puntos_base >= min_puntos,
                Problema.puntos_base <= max_puntos
            )
        ).all()
    
    def search_by_habilidad_requerida(self, db: Session, habilidad: str) -> List[Problema]:
        """Buscar problemas que requieren una habilidad específica"""
        return db.query(Problema).filter(
            Problema.habilidades_requeridas.has_key(habilidad)
        ).all()
    
    def get_ordenados_por_puntos(self, db: Session, ascending: bool = False) -> List[Problema]:
        """Obtener problemas ordenados por puntos"""
        order = asc(Problema.puntos_base) if ascending else desc(Problema.puntos_base)
        return db.query(Problema).order_by(order).all()
    
    def update(self, db: Session, problema_id: int, update_data: Dict[str, Any]) -> Optional[Problema]:
        """Actualizar problema"""
        problema = self.get(db, problema_id)
        if problema:
            for field, value in update_data.items():
                setattr(problema, field, value)
            db.commit()
            db.refresh(problema)
        return problema
    
    def delete(self, db: Session, problema_id: int) -> bool:
        """Eliminar problema"""
        problema = self.get(db, problema_id)
        if problema:
            db.delete(problema)
            db.commit()
            return True
        return False
    
    def get_estadisticas(self, db: Session) -> Dict[str, Any]:
        """Obtener estadísticas de problemas"""
        total = db.query(Problema).count()
        
        # Distribución por tipo
        tipos = db.query(Problema.tipo, db.func.count(Problema.id)).group_by(Problema.tipo).all()
        distribucion_tipos = {tipo: count for tipo, count in tipos}
        
        # Distribución por dificultad
        dificultades = db.query(Problema.nivel_dificultad, db.func.count(Problema.id)).group_by(Problema.nivel_dificultad).all()
        distribucion_dificultades = {dif: count for dif, count in dificultades}
        
        # Promedio de puntos
        avg_puntos = db.query(db.func.avg(Problema.puntos_base)).scalar() or 0
        
        return {
            'total_problemas': total,
            'distribucion_tipos': distribucion_tipos,
            'distribucion_dificultades': distribucion_dificultades,
            'promedio_puntos': round(avg_puntos, 2)
        }

# ============================================================================
# CRUD ASIGNACIONES
# ============================================================================

class CRUDAsignacion:
    
    def create(self, db: Session, asignacion_data: Dict[str, Any]) -> Asignacion:
        """Crear nueva asignación"""
        # Generar UUID si no se proporciona
        if 'uuid' not in asignacion_data:
            asignacion_data['uuid'] = str(uuid.uuid4())
        
        asignacion = Asignacion(**asignacion_data)
        db.add(asignacion)
        db.commit()
        db.refresh(asignacion)
        return asignacion
    
    def get(self, db: Session, asignacion_id: int) -> Optional[Asignacion]:
        """Obtener asignación por ID"""
        return db.query(Asignacion).filter(Asignacion.id == asignacion_id).first()
    
    def get_by_uuid(self, db: Session, asignacion_uuid: str) -> Optional[Asignacion]:
        """Obtener asignación por UUID"""
        return db.query(Asignacion).filter(Asignacion.uuid == asignacion_uuid).first()
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[Asignacion]:
        """Obtener todas las asignaciones"""
        return db.query(Asignacion).order_by(desc(Asignacion.created_at)).offset(skip).limit(limit).all()
    
    def get_validas(self, db: Session) -> List[Asignacion]:
        """Obtener solo asignaciones válidas"""
        return db.query(Asignacion).filter(Asignacion.es_solucion_valida == True).all()
    
    def get_mejores_fitness(self, db: Session, limit: int = 10) -> List[Asignacion]:
        """Obtener asignaciones con mejor fitness"""
        return db.query(Asignacion).order_by(desc(Asignacion.fitness_final)).limit(limit).all()
    
    def get_by_participante(self, db: Session, participante_id: int) -> List[Asignacion]:
        """Obtener asignaciones que incluyen un participante específico"""
        return db.query(Asignacion).filter(
            Asignacion.participantes_ids.contains([participante_id])
        ).all()
    
    def get_by_problema(self, db: Session, problema_id: int) -> List[Asignacion]:
        """Obtener asignaciones que incluyen un problema específico"""
        return db.query(Asignacion).filter(
            Asignacion.problemas_ids.contains([problema_id])
        ).all()
    
    def get_recientes(self, db: Session, dias: int = 7) -> List[Asignacion]:
        """Obtener asignaciones recientes"""
        from datetime import datetime, timedelta
        fecha_limite = datetime.now() - timedelta(days=dias)
        
        return db.query(Asignacion).filter(
            Asignacion.created_at >= fecha_limite
        ).order_by(desc(Asignacion.created_at)).all()
    
    def update(self, db: Session, asignacion_id: int, update_data: Dict[str, Any]) -> Optional[Asignacion]:
        """Actualizar asignación"""
        asignacion = self.get(db, asignacion_id)
        if asignacion:
            for field, value in update_data.items():
                setattr(asignacion, field, value)
            db.commit()
            db.refresh(asignacion)
        return asignacion
    
    def delete(self, db: Session, asignacion_id: int) -> bool:
        """Eliminar asignación"""
        asignacion = self.get(db, asignacion_id)
        if asignacion:
            db.delete(asignacion)
            db.commit()
            return True
        return False
    
    def get_estadisticas(self, db: Session) -> Dict[str, Any]:
        """Obtener estadísticas de asignaciones"""
        total = db.query(Asignacion).count()
        validas = db.query(Asignacion).filter(Asignacion.es_solucion_valida == True).count()
        
        # Promedios
        avg_fitness = db.query(db.func.avg(Asignacion.fitness_final)).scalar() or 0
        avg_tiempo_ejecucion = db.query(db.func.avg(Asignacion.tiempo_ejecucion_segundos)).scalar() or 0
        avg_generaciones = db.query(db.func.avg(Asignacion.generaciones_ejecutadas)).scalar() or 0
        
        # Mejor y peor fitness
        mejor_fitness = db.query(db.func.max(Asignacion.fitness_final)).scalar() or 0
        peor_fitness = db.query(db.func.min(Asignacion.fitness_final)).scalar() or 0
        
        return {
            'total_asignaciones': total,
            'asignaciones_validas': validas,
            'porcentaje_validas': round((validas / total * 100) if total > 0 else 0, 2),
            'fitness_promedio': round(avg_fitness, 4),
            'mejor_fitness': round(mejor_fitness, 4),
            'peor_fitness': round(peor_fitness, 4),
            'tiempo_promedio_segundos': round(avg_tiempo_ejecucion, 2),
            'generaciones_promedio': round(avg_generaciones, 2)
        }

# ============================================================================
# INSTANCIAS CRUD
# ============================================================================

# Instancias para usar en toda la aplicación
crud_participante = CRUDParticipante()
crud_problema = CRUDProblema()
crud_asignacion = CRUDAsignacion()

# ============================================================================
# OPERACIONES COMPLEJAS
# ============================================================================

def buscar_asignacion_optima(db: Session, 
                           problemas_ids: List[int], 
                           participantes_ids: List[int]) -> Optional[Asignacion]:
    """
    Buscar la mejor asignación existente para un conjunto específico de problemas y participantes
    """
    asignaciones = db.query(Asignacion).filter(
        and_(
            Asignacion.problemas_ids == problemas_ids,
            Asignacion.participantes_ids == participantes_ids,
            Asignacion.es_solucion_valida == True
        )
    ).order_by(desc(Asignacion.fitness_final)).first()
    
    return asignaciones

def get_dashboard_stats(db: Session) -> Dict[str, Any]:
    """
    Obtener estadísticas completas para dashboard
    """
    stats_participantes = crud_participante.get_estadisticas(db)
    stats_problemas = crud_problema.get_estadisticas(db)
    stats_asignaciones = crud_asignacion.get_estadisticas(db)
    
    return {
        'participantes': stats_participantes,
        'problemas': stats_problemas,
        'asignaciones': stats_asignaciones,
        'timestamp': datetime.now().isoformat()
    }