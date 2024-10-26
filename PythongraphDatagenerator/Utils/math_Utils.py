import numpy as np
from typing import List, Tuple

class MathUtils:
    @staticmethod
    def find_intersections(func1, func2, x_range):
        """Find intersection points between two functions"""
        x = np.linspace(x_range[0], x_range[1], 1000)
        y1 = func1(x)
        y2 = func2(x)
        
        # Find sign changes
        sign_changes = np.where(np.diff(np.signbit(y1 - y2)))[0]
        
        intersections = []
        for idx in sign_changes:
            x_intersect = x[idx]
            y_intersect = func1(x_intersect)
            intersections.append((x_intersect, y_intersect))
        
        return intersections
    
    @staticmethod
    def find_extrema(func, x_range, num_points=1000):
        """Find local extrema of a function"""
        x = np.linspace(x_range[0], x_range[1], num_points)
        y = func(x)
        
        # Find local maxima and minima
        maxima = []
        minima = []
        
        for i in range(1, len(x) - 1):
            if y[i-1] < y[i] > y[i+1]:
                maxima.append((x[i], y[i]))
            elif y[i-1] > y[i] < y[i+1]:
                minima.append((x[i], y[i]))
        
        return maxima, minima
    
    @staticmethod
    def normalize_points(points, grid_info):
        """Normalize points based on grid information"""
        if not grid_info or not grid_info.origin:
            return points
            
        normalized = []
        for x, y in points:
            norm_x = (x - grid_info.origin[0]) / grid_info.x_scale
            norm_y = (grid_info.origin[1] - y) / grid_info.y_scale
            normalized.append([norm_x, norm_y])
            
        return np.array(normalized)
    
    @staticmethod
    def denormalize_points(points, grid_info):
        """Convert normalized points back to image coordinates"""
        if not grid_info or not grid_info.origin:
            return points
            
        denormalized = []
        for x, y in points:
            img_x = x * grid_info.x_scale + grid_info.origin[0]
            img_y = grid_info.origin[1] - y * grid_info.y_scale
            denormalized.append([img_x, img_y])
            
        return np.array(denormalized)
    
    @staticmethod
    def estimate_function_parameters(points, critical_points):
        """Estimate initial function parameters based on points and critical points"""
        x = points[:, 0]
        y = points[:, 1]
        
        # Basic statistics
        x_mean = np.mean(x)
        y_mean = np.mean(y)
        x_range = np.max(x) - np.min(x)
        y_range = np.max(y) - np.min(y)
        
        # Estimate initial parameters
        a = y_range / (x_range ** 3)  # Cubic coefficient
        b = -3 * a * x_mean  # Quadratic coefficient
        c = 3 * a * x_mean ** 2  # Linear coefficient
        d = y_mean - (a * x_mean ** 3 + b * x_mean ** 2 + c * x_mean)  # Constant
        
        # Adjust based on critical points
        if critical_points:
            for point_type, px, py in critical_points:
                if point_type in ['max', 'min']:
                    # Adjust coefficients to better match extrema
                    a *= py / (a * px**3 + b * px**2 + c * px + d)
                    d += py - (a * px**3 + b * px**2 + c * px + d)
        
        return np.array([a, b, c, d])