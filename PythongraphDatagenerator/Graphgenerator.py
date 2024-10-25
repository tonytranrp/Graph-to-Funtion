import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline, BSpline
import json

class PointBasedFunctionGenerator:
    def __init__(self):
        self.points = None
        self.spline_function = None
        
    def load_points_from_json(self, filename):
        """Load points from a JSON file"""
        with open(filename, 'r') as f:
            data = json.load(f)
            self.points = [(point['x'], point['y']) for point in data['points']]
            
    def generate_function(self):
        """Generate a smooth function from points using B-spline interpolation"""
        if not self.points:
            raise ValueError("No points loaded")
            
        # Separate x and y coordinates
        x_coords, y_coords = zip(*self.points)
        x_coords = np.array(x_coords)
        y_coords = np.array(y_coords)
        
        # Create B-spline representation
        # k=3 gives cubic spline, smoother curve
        self.spline_function = make_interp_spline(x_coords, y_coords, k=3)
        
    def plot_function(self, show_points=True):
        """Plot the generated function"""
        if not self.spline_function:
            raise ValueError("Generate function first")
            
        # Create a finer x array for smooth plotting
        x_coords, y_coords = zip(*self.points)
        x_new = np.linspace(min(x_coords), max(x_coords), 1000)
        y_new = self.spline_function(x_new)
        
        plt.figure(figsize=(12, 8))
        
        # Plot the smooth curve
        plt.plot(x_new, y_new, 'b-', label='Interpolated Function')
        
        # Optionally plot original points
        if show_points:
            plt.plot(x_coords, y_coords, 'r.', alpha=0.5, 
                    markersize=4, label='Original Points')
        
        plt.grid(True)
        plt.xlabel('x')
        plt.ylabel('y')
        plt.title('Reconstructed Function from Points')
        plt.legend()
        plt.show()
        
    def evaluate_at(self, x):
        """Evaluate the function at a specific x value"""
        if not self.spline_function:
            raise ValueError("Generate function first")
        return float(self.spline_function(x))
    
    def get_critical_points(self):
        """Find approximate critical points"""
        if not self.points:
            return None
            
        x_coords, y_coords = zip(*self.points)
        
        critical_points = {
            'x_intercepts': [],
            'y_intercept': None,
            'local_maxima': [],
            'local_minima': []
        }
        
        # Find y-intercept (closest point to x=0)
        closest_to_zero = min(self.points, key=lambda p: abs(p[0]))
        critical_points['y_intercept'] = closest_to_zero[1]
        
        # Find x-intercepts (points where y is close to 0)
        for i in range(len(self.points)-1):
            if self.points[i][1] * self.points[i+1][1] <= 0:
                # Linear interpolation to find more precise x-intercept
                x1, y1 = self.points[i]
                x2, y2 = self.points[i+1]
                x_intercept = x1 - y1 * (x2 - x1) / (y2 - y1)
                critical_points['x_intercepts'].append(round(x_intercept, 6))
        
        # Find local maxima and minima
        for i in range(1, len(self.points)-1):
            prev_y = self.points[i-1][1]
            curr_y = self.points[i][1]
            next_y = self.points[i+1][1]
            
            if prev_y < curr_y > next_y:
                critical_points['local_maxima'].append(self.points[i])
            elif prev_y > curr_y < next_y:
                critical_points['local_minima'].append(self.points[i])
                
        return critical_points

def main():
    # Create generator instance
    generator = PointBasedFunctionGenerator()
    
    # Load points from your JSON file
    generator.load_points_from_json('function_points_logarithmic_1701.json')
    
    # Generate and plot the function
    generator.generate_function()
    generator.plot_function(show_points=True)
    
    # Print critical points
    critical_points = generator.get_critical_points()
    if critical_points:
        print("\nCritical Points:")
        print(f"Y-intercept: {critical_points['y_intercept']:.6f}")
        print(f"X-intercepts: {[f'{x:.6f}' for x in critical_points['x_intercepts']]}")
        print("\nLocal Maxima:", [(f"{p[0]:.2f}", f"{p[1]:.2f}") for p in critical_points['local_maxima']])
        print("Local Minima:", [(f"{p[0]:.2f}", f"{p[1]:.2f}") for p in critical_points['local_minima']])
        
    # Test some point evaluations
    test_x = 2.5
    print(f"\nValue at x={test_x}: {generator.evaluate_at(test_x):.6f}")

if __name__ == "__main__":
    main()