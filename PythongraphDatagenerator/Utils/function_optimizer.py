import numpy as np
from dataclasses import dataclass
from typing import List, Tuple
import queue
import threading
import time

@dataclass
class OptimizationResult:
    params: np.ndarray
    error: float
    function_type: str
    generation: int

class FunctionOptimizer:
    def __init__(self, 
                 max_attempts=1000,
                 population_size=50,
                 mutation_rate=0.1,
                 crossover_rate=0.7,
                 elite_size=2,
                 batch_size=10):
        self.max_attempts = max_attempts
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.elite_size = elite_size
        self.batch_size = batch_size
        self.learning_rate = 0.01
        
    def target_function(self, x, a, b, c, d):
        """Base target function"""
        return (a * np.power(x, 3) + b * np.power(x, 2) + c * x + d) / 4
    
    def error_function(self, params, x, y, critical_points=None):
        """Enhanced error function with critical points consideration"""
        predicted = self.target_function(x, *params)
        mse = np.mean((y - predicted)**2)
        
        # Base regularization
        regularization = 0.01 * np.sum(np.square(params))
        
        # Smoothness constraint
        smoothness = np.mean(np.diff(predicted)**2) if len(predicted) > 1 else 0
        
        # Critical points constraint
        critical_error = 0
        if critical_points:
            for point_type, px, py in critical_points:
                pred_y = self.target_function(px, *params)
                if point_type in ['max', 'min']:
                    # Check if prediction matches local extrema
                    critical_error += abs(pred_y - py)
                elif point_type == 'x_intercept':
                    # Penalize deviation from x-axis
                    critical_error += abs(pred_y)
                elif point_type == 'y_intercept':
                    # Penalize deviation from y-intercept
                    critical_error += abs(pred_y - py)
                    
        return mse + regularization + 0.1 * smoothness + 0.2 * critical_error
    
    def optimize(self, x, y, critical_points=None, update_queue=None):
        """Main optimization loop with real-time updates"""
        # Initialize population
        population = []
        for _ in range(self.population_size):
            params = np.random.uniform(-5, 5, 4)
            population.append(params)
        
        best_params = None
        best_error = float('inf')
        generations_without_improvement = 0
        
        for generation in range(self.max_attempts):
            # Process batch of generations
            for _ in range(self.batch_size):
                population_array = np.array(population)
                errors = np.array([
                    self.error_function(p, x, y, critical_points) 
                    for p in population_array
                ])
                
                # Update best solution
                min_error_idx = np.argmin(errors)
                if errors[min_error_idx] < best_error:
                    best_error = errors[min_error_idx]
                    best_params = population_array[min_error_idx].copy()
                    generations_without_improvement = 0
                else:
                    generations_without_improvement += 1
                
                # Evolution step
                population = self._evolve_population(
                    population_array, errors, generations_without_improvement
                )
                
                # Adaptive learning
                if generations_without_improvement > 20:
                    self.learning_rate *= 0.95
                    generations_without_improvement = 0
                
                # Early stopping
                if best_error < 1e-6:
                    break
            
            # Update progress
            if update_queue:
                result = OptimizationResult(
                    params=best_params.copy(),
                    error=best_error,
                    function_type="cubic",
                    generation=generation * self.batch_size
                )
                update_queue.put(result)
            
            # Brief pause
            time.sleep(0.001)
        
        return best_params, best_error
    
    def _evolve_population(self, population, errors, stagnation):
        """Evolve population using tournament selection and adaptive mutation"""
        new_population = []
        
        # Elitism
        elite_indices = np.argsort(errors)[:self.elite_size]
        elites = population[elite_indices]
        new_population.extend(elites)
        
        # Generate rest of population
        while len(new_population) < self.population_size:
            # Tournament selection
            tournament_size = 3
            tournament_idx = np.random.choice(len(population), tournament_size)
            tournament_errors = errors[tournament_idx]
            parent_idx = tournament_idx[np.argmin(tournament_errors)]
            parent = population[parent_idx]
            
            # Adaptive mutation
            child = parent.copy()
            if np.random.random() < self.mutation_rate:
                # Increase mutation strength during stagnation
                mutation_strength = self.learning_rate * (1 + stagnation / 50)
                mutation = np.random.normal(0, mutation_strength, 4)
                child = child + mutation
            
            new_population.append(child)
        
        return new_population