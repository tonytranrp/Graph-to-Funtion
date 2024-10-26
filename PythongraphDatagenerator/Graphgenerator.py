import numpy as np
from scipy.interpolate import make_interp_spline
import json
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import tkinter as tk
from tkinter import ttk
import webbrowser
import tempfile
import os

class ModernFunctionViewer:
    def __init__(self):
        self.points = None
        self.spline_function = None
        self.x_range = None
        self.y_range = None
        self.critical_points = None
        
    def load_points_from_json(self, filename):
        """Load points from a JSON file"""
        with open(filename, 'r') as f:
            data = json.load(f)
            self.points = [(point['x'], point['y']) for point in data['points']]
            self.x_range = data['x_range']
            y_coords = [p[1] for p in self.points]
            self.y_range = [min(y_coords), max(y_coords)]
            
    def generate_function(self):
        """Generate a smooth function from points"""
        if not self.points:
            raise ValueError("No points loaded")
            
        x_coords, y_coords = zip(*self.points)
        x_coords = np.array(x_coords)
        y_coords = np.array(y_coords)
        
        self.spline_function = make_interp_spline(x_coords, y_coords, k=3)
        self._find_critical_points()
        
    def _find_critical_points(self):
        """Find all critical points of the function"""
        x_coords, y_coords = zip(*self.points)
        
        self.critical_points = {
            'x_intercepts': [],
            'y_intercept': None,
            'minimum': None,
            'maximum': None
        }
        
        # Find intercepts and extrema
        for i in range(len(self.points)-1):
            x1, y1 = self.points[i]
            x2, y2 = self.points[i+1]
            
            # X-intercepts
            if y1 * y2 <= 0:
                x_intercept = x1 - y1 * (x2 - x1) / (y2 - y1)
                self.critical_points['x_intercepts'].append((x_intercept, 0))
                
            # Y-intercept
            if x1 * x2 <= 0:
                y_intercept = y1 - x1 * (y2 - y1) / (x2 - x1)
                self.critical_points['y_intercept'] = (0, y_intercept)
        
        # Find global minimum and maximum
        y_coords = [p[1] for p in self.points]
        min_idx = np.argmin(y_coords)
        max_idx = np.argmax(y_coords)
        self.critical_points['minimum'] = self.points[min_idx]
        self.critical_points['maximum'] = self.points[max_idx]
        
    def create_interactive_plot(self):
        """Create an interactive plot using Plotly"""
        x_coords, y_coords = zip(*self.points)
        
        # Create a smoother curve for plotting
        x_smooth = np.linspace(min(x_coords), max(x_coords), 1000)
        y_smooth = self.spline_function(x_smooth)
        
        # Create the main function trace
        fig = go.Figure()
        
        # Add the main function curve
        fig.add_trace(go.Scatter(
            x=x_smooth,
            y=y_smooth,
            mode='lines',
            name='Function',
            line=dict(color='rgb(0, 100, 255)', width=2)
        ))
        
        # Add critical points
        if self.critical_points:
            # X-intercepts
            if self.critical_points['x_intercepts']:
                x_int, y_int = zip(*self.critical_points['x_intercepts'])
                fig.add_trace(go.Scatter(
                    x=x_int,
                    y=y_int,
                    mode='markers+text',
                    name='X-intercepts',
                    marker=dict(size=8, color='red'),
                    text=[f'({x:.3f}, 0)' for x in x_int],
                    textposition='top center'
                ))
            
            # Y-intercept
            if self.critical_points['y_intercept']:
                x, y = self.critical_points['y_intercept']
                fig.add_trace(go.Scatter(
                    x=[x],
                    y=[y],
                    mode='markers+text',
                    name='Y-intercept',
                    marker=dict(size=8, color='green'),
                    text=f'(0, {y:.3f})',
                    textposition='top center'
                ))
            
            # Minimum point
            if self.critical_points['minimum']:
                x, y = self.critical_points['minimum']
                fig.add_trace(go.Scatter(
                    x=[x],
                    y=[y],
                    mode='markers+text',
                    name='Minimum',
                    marker=dict(size=8, color='purple'),
                    text=f'Min: ({x:.3f}, {y:.3f})',
                    textposition='bottom center'
                ))
            
            # Maximum point
            if self.critical_points['maximum']:
                x, y = self.critical_points['maximum']
                fig.add_trace(go.Scatter(
                    x=[x],
                    y=[y],
                    mode='markers+text',
                    name='Maximum',
                    marker=dict(size=8, color='orange'),
                    text=f'Max: ({x:.3f}, {y:.3f})',
                    textposition='top center'
                ))
        
        # Update layout for better appearance
        fig.update_layout(
            title='Interactive Function Viewer',
            plot_bgcolor='rgb(240, 240, 240)',
            showlegend=True,
            hovermode='closest',
            xaxis=dict(
                showgrid=True,
                gridcolor='white',
                gridwidth=1,
                zeroline=True,
                zerolinecolor='black',
                zerolinewidth=2,
                title='x'
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor='white',
                gridwidth=1,
                zeroline=True,
                zerolinecolor='black',
                zerolinewidth=2,
                title='y'
            )
        )
        
        # Save to temporary HTML file and open in browser
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.html')
        fig.write_html(temp_file.name)
        webbrowser.open('file://' + temp_file.name)
        
        return fig

def main():
    viewer = ModernFunctionViewer()
    viewer.load_points_from_json('function_points_logarithmic_24001.json')
    viewer.generate_function()
    viewer.create_interactive_plot()

if __name__ == "__main__":
    main()