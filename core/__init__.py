from .algoritmo_genetico import AlgoritmoGenetico, IndividuoGenetico, EvaluadorFitness

# Para compatibilidad hacia atrás (por si algo más usa estos nombres)
AlgoritmoGeneticoAvanzado = AlgoritmoGenetico
EvaluadorFitnessAvanzado = EvaluadorFitness
EvaluadorAsignacion = EvaluadorFitness

__all__ = [
    'EvaluadorAsignacion', 
    'EvaluadorFitness',
    'EvaluadorFitnessAvanzado',
    'IndividuoGenetico',
    'AlgoritmoGenetico', 
    'AlgoritmoGeneticoAvanzado'
]