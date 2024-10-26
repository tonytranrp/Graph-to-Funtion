import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class PlotManager:
    def __init__(self, figure_size=(6, 8), dpi=80):
        # Create figure and subplots
        self.fig = Figure(figsize=figure_size, dpi=dpi)
        self.setup_plots()
        
        # Store history
        self.error_history = []
        self.params_history = []
    
    def setup_plots(self):
        """Initialize plot layout"""
        # Comparison plot
        self.comparison_ax = self.fig.add_subplot(211)
        self.comparison_ax.set_title('Function Comparison', fontsize=8)
        self.comparison_ax.grid(True, linestyle=':')
        
        # Error plot
        self.error_ax = self.fig.add_subplot(212)
        self.error_ax.set_title('Error History', fontsize=8)
        self.error_ax.set_yscale('log')
        self.error_ax.grid(True, linestyle=':')
        
        # Style configuration
        self.comparison_ax.set_prop_cycle(color=['blue', 'red'])
        self.error_ax.set_prop_cycle(color=['green'])
        
        self.fig.tight_layout()
    
    def update_plots(self, original_points, params, error_history, grid_info=None):
        """Update both plots with new data"""
        self._update_comparison_plot(original_points, params, grid_info)
        self._update_error_plot(error_history)
        self.fig.canvas.draw()
    
    def _update_comparison_plot(self, original_points, params, grid_info):
        """Update function comparison plot"""
        self.comparison_ax.clear()
        
        # Plot original points
        self.comparison_ax.scatter(
            original_points[:, 0], original_points[:, 1],
            color='blue', s=1, label='Original', rasterized=True
        )
        
        # Plot generated function
        x_smooth = np.linspace(
            min(original_points[:, 0]),
            max(original_points[:, 0]),
            200
        )
        y_smooth = (params[0] * np.power(x_smooth, 3) + 
                   params[1] * np.power(x_smooth, 2) + 
                   params[2] * x_smooth + params[3]) / 4
        
        self.comparison_ax.plot(
            x_smooth, y_smooth, 'r-',
            label='Generated', linewidth=1, rasterized=True
        )
        
        # Add grid if available
        if grid_info:
            self._add_grid_to_plot(grid_info)
        
        # Configure plot
        self.comparison_ax.grid(True, linestyle=':')
        self.comparison_ax.legend(fontsize=8)
        self.comparison_ax.set_title('Comparison', fontsize=8)
        self.comparison_ax.tick_params(labelsize=6)
    
    def _update_error_plot(self, error_history):
        """Update error history plot"""
        self.error_ax.clear()
        self.error_ax.plot(
            error_history, 'g-',
            linewidth=1, rasterized=True
        )
        self.error_ax.set_yscale('log')
        self.error_ax.grid(True, linestyle=':')
        self.error_ax.set_title('Error History', fontsize=8)
        self.error_ax.tick_params(labelsize=6)
    
    def _add_grid_to_plot(self, grid_info):
        """Add grid lines to comparison plot"""
        # Add major grid lines
        self.comparison_ax.grid(True, which='major', color='gray', 
                              linestyle='-', alpha=0.2)
        
        # Add minor grid lines
        self.comparison_ax.grid(True, which='minor', color='gray',
                              linestyle=':', alpha=0.1)
        
        # Add axes
        if grid_info.origin:
            self.comparison_ax.axhline(y=0, color='black', linewidth=0.5)
            self.comparison_ax.axvline(x=0, color='black', linewidth=0.5)
    
    def resize(self, width, height):
        """Handle plot resize"""
        fig_width = max(width / 120, 5)
        fig_height = max(height / 90, 6)
        self.fig.set_size_inches(fig_width, fig_height)
        self.fig.tight_layout()