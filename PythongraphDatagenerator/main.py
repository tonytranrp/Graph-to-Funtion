
import numpy as np
import matplotlib.pyplot as plt
from random import choice, uniform
from scipy.optimize import fsolve, minimize
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import sympy as sp
import json
from matplotlib.gridspec import GridSpec

class EnhancedFunctionGenerator:
    def __init__(self):
        self.function_types = [
            'logarithmic',
            'exponential',
            'rational',
            'trigonometric',
            'linear'
        ]
        self.current_func = None
        self.current_label = None
        self.current_expr = None
        self.current_symbol = None
        self.setup_gui()

    def setup_gui(self):
        self.root = tk.Tk()
        self.root.title("Enhanced Function Generator")
        self.root.configure(bg='#2b2b2b')
        
        # Main frame with scrolling
        self.main_frame = tk.Frame(self.root, bg='#2b2b2b')
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Control panel
        control_frame = tk.Frame(self.main_frame, bg='#2b2b2b')
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Function type selection with styled dropdown
        tk.Label(control_frame, text="Select function type:", bg='#2b2b2b', fg='white').pack()
        self.func_type_var = tk.StringVar(value=self.function_types[0])
        func_type_menu = tk.OptionMenu(control_frame, self.func_type_var, *self.function_types)
        func_type_menu.configure(width=15, bg='#404040', fg='white')
        func_type_menu.pack(pady=5)
        
        # Range inputs with grid layout
        range_frame = tk.Frame(control_frame, bg='#2b2b2b')
        range_frame.pack(pady=5)
        
        # X range
        tk.Label(range_frame, text="X range:", bg='#2b2b2b', fg='white').grid(row=0, column=0, padx=5)
        self.x_min = tk.Entry(range_frame, width=6, bg='#404040', fg='white')
        self.x_min.insert(0, "-12")
        self.x_min.grid(row=0, column=1)
        tk.Label(range_frame, text="to", bg='#2b2b2b', fg='white').grid(row=0, column=2, padx=5)
        self.x_max = tk.Entry(range_frame, width=6, bg='#404040', fg='white')
        self.x_max.insert(0, "12")
        self.x_max.grid(row=0, column=3)
        
        # Y range
        tk.Label(range_frame, text="Y range:", bg='#2b2b2b', fg='white').grid(row=1, column=0, padx=5)
        self.y_min = tk.Entry(range_frame, width=6, bg='#404040', fg='white')
        self.y_min.insert(0, "-12")
        self.y_min.grid(row=1, column=1)
        tk.Label(range_frame, text="to", bg='#2b2b2b', fg='white').grid(row=1, column=2, padx=5)
        self.y_max = tk.Entry(range_frame, width=6, bg='#404040', fg='white')
        self.y_max.insert(0, "12")
        self.y_max.grid(row=1, column=3)
        
        # Step size input
        step_frame = tk.Frame(control_frame, bg='#2b2b2b')
        step_frame.pack(pady=5)
        tk.Label(step_frame, text="Step size:", bg='#2b2b2b', fg='white').pack(side=tk.LEFT)
        self.step_size = tk.Entry(step_frame, width=8, bg='#404040', fg='white')
        self.step_size.insert(0, "0.001")
        self.step_size.pack(side=tk.LEFT, padx=5)
        
        # Action buttons
        button_frame = tk.Frame(control_frame, bg='#2b2b2b')
        button_frame.pack(pady=5)
        
        button_style = {'bg': '#404040', 'fg': 'white', 'width': 12, 'padx': 5}
        tk.Button(button_frame, text="Generate", command=self.generate_new, **button_style).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Refresh", command=self.refresh, **button_style).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Export Points", command=self.export_points, **button_style).pack(side=tk.LEFT, padx=5)
        
        # Plot area with dark theme
        plt.style.use('dark_background')
        self.fig = plt.Figure(figsize=(10, 8), facecolor='#2b2b2b')
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor('#1c1c1c')
        
        self.plot_canvas = FigureCanvasTkAgg(self.fig, master=control_frame)
        self.plot_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Navigation toolbar
        self.toolbar = NavigationToolbar2Tk(self.plot_canvas, control_frame)
        self.toolbar.update()
        
        # Info text area
        self.info_text = tk.Text(control_frame, height=6, width=50, bg='#404040', fg='white')
        self.info_text.pack(pady=5)

    def generate_random_function(self):
        func_type = self.func_type_var.get()
        x = sp.Symbol('x')
        
        a = round(uniform(0.5, 2), 2)
        b = round(uniform(-2, 2), 2)
        c = round(uniform(-2, 2), 2)
        
        if func_type == 'logarithmic':
            expr = a * sp.log(abs(b * x + c)) + round(uniform(-2, 2), 2)
            label = f'{a:.2f} * ln(|{b:.2f}x + {c:.2f}|) + {round(uniform(-2, 2), 2):.2f}'
            
            def func(x_val):
                try:
                    return float(expr.subs(x, x_val))
                except:
                    return np.nan
                    
        elif func_type == 'exponential':
            expr = a * sp.exp(b * x) + c
            label = f'{a:.2f} * e^({b:.2f}x) + {c:.2f}'
            
            def func(x_val):
                try:
                    return float(expr.subs(x, x_val))
                except:
                    return np.nan
                    
        elif func_type == 'rational':
            d = round(uniform(-2, 2), 2)
            expr = (a * x + b) / (c * x + d)
            label = f'({a:.2f}x + {b:.2f})/({c:.2f}x + {d:.2f})'
            
            def func(x_val):
                try:
                    if abs(c * x_val + d) < 1e-10:
                        return np.nan
                    return float(expr.subs(x, x_val))
                except:
                    return np.nan
                    
        elif func_type == 'trigonometric':
            trig_choice = choice(['sin', 'cos', 'tan'])
            if trig_choice == 'sin':
                expr = a * sp.sin(b * x) + c
            elif trig_choice == 'cos':
                expr = a * sp.cos(b * x) + c
            else:
                expr = a * sp.tan(b * x) + c
            label = f'{a:.2f} * {trig_choice}({b:.2f}x) + {c:.2f}'
            
            def func(x_val):
                try:
                    result = float(expr.subs(x, x_val))
                    if abs(result) > 1e10:
                        return np.nan
                    return result
                except:
                    return np.nan
                    
        else:  # linear
            expr = a * x + b
            label = f'{a:.2f}x + {b:.2f}'
            
            def func(x_val):
                return float(expr.subs(x, x_val))
        
        self.current_expr = expr
        self.current_symbol = x
        self.current_func = func
        self.current_label = label
        
        return func, label

    def find_critical_points(self, func, x_range):
        critical_points = []
        x = self.current_symbol
        expr = self.current_expr
        
        try:
            # Find derivative
            derivative = sp.diff(expr, x)
            
            # Find critical points
            critical_vals = sp.solve(derivative, x)
            real_critical_vals = [float(val.evalf()) for val in critical_vals if val.is_real]
            valid_critical_vals = [val for val in real_critical_vals 
                                 if x_range[0] <= val <= x_range[1]]
            
            # Find x-intercepts
            x_intercepts = sp.solve(expr, x)
            real_x_intercepts = [float(val.evalf()) for val in x_intercepts if val.is_real]
            valid_x_intercepts = [val for val in real_x_intercepts 
                                if x_range[0] <= val <= x_range[1]]
            
            critical_points.append(f"X-intercepts: {[round(x, 6) for x in valid_x_intercepts]}")
            
            # Find y-intercept
            if x_range[0] <= 0 <= x_range[1]:
                y_intercept = float(expr.subs(x, 0))
                critical_points.append(f"Y-intercept: {round(y_intercept, 6)}")
            
            # Evaluate critical points
            for val in valid_critical_vals:
                y_val = float(expr.subs(x, val))
                second_deriv = float(sp.diff(derivative, x).subs(x, val))
                if second_deriv > 0:
                    critical_points.append(f"Local minimum: ({round(val, 6)}, {round(y_val, 6)})")
                elif second_deriv < 0:
                    critical_points.append(f"Local maximum: ({round(val, 6)}, {round(y_val, 6)})")
            
        except Exception as e:
            critical_points.append(f"Error finding critical points: {str(e)}")
            
        return critical_points

    def plot_function(self):
        try:
            x_range = (float(self.x_min.get()), float(self.x_max.get()))
            y_range = (float(self.y_min.get()), float(self.y_max.get()))
            
            func, label = self.generate_random_function()
            
            # Generate points with high resolution
            x = np.linspace(x_range[0], x_range[1], 5000)
            y = np.array([func(xi) for xi in x])
            
            # Filter valid points
            mask = np.isfinite(y)
            x, y = x[mask], y[mask]
            
            # Apply y-range limits
            mask = (y >= y_range[0]) & (y <= y_range[1])
            x, y = x[mask], y[mask]
            
            # Clear and set up plot
            self.ax.clear()
            self.ax.grid(True, linestyle='--', alpha=0.3)
            self.ax.set_title(f'Function: {label}', color='white', pad=10)
            
            # Plot function
            self.ax.plot(x, y, 'cyan', linewidth=2, label='Function')
            
            # Add coordinate axes
            self.ax.axhline(y=0, color='white', linewidth=0.5, alpha=0.5)
            self.ax.axvline(x=0, color='white', linewidth=0.5, alpha=0.5)
            
            # Plot critical points
            critical_points = self.find_critical_points(func, x_range)
            for point in critical_points:
                if "intercept" in point.lower():
                    coords = eval(point.split(": ")[1])
                    if isinstance(coords, list):
                        for x_val in coords:
                            self.ax.plot(x_val, 0, 'ro', markersize=8)
                    else:
                        self.ax.plot(0, coords, 'ro', markersize=8)
                elif "minimum" in point.lower() or "maximum" in point.lower():
                    coords = eval(point.split(": ")[1])
                    self.ax.plot(coords[0], coords[1], 'yo', markersize=8)
                    self.ax.annotate(f'({coords[0]:.2f}, {coords[1]:.2f})',
                                   (coords[0], coords[1]), xytext=(10, 10),
                                   textcoords='offset points', color='white',
                                   bbox=dict(facecolor='#404040', alpha=0.7))
            
            # Set limits and display
            self.ax.set_xlim(x_range)
            self.ax.set_ylim(y_range)
            self.plot_canvas.draw()
            
            # Update info text
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(tk.END, f"Function: {label}\n\n")
            for point in critical_points:
                self.info_text.insert(tk.END, point + "\n")
                
        except Exception as e:
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(tk.END, f"Error: {str(e)}")

    def export_points(self):
        if self.current_func is None:
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(tk.END, "Please generate a function first")
            return
            
        try:
            x_range = (float(self.x_min.get()), float(self.x_max.get()))
            step = float(self.step_size.get())
            
            x = np.arange(x_range[0], x_range[1] + step, step)
            y = np.array([self.current_func(xi) for xi in x])
            
            mask = np.isfinite(y)
            x, y = x[mask], y[mask]
            points = [{'x': float(xi), 'y': float(yi)} for xi, yi in zip(x, y)]
            filename = f"function_points_{self.func_type_var.get()}_{len(points)}.json"
            
            data = {
                'function_type': self.func_type_var.get(),
                'label': self.current_label,
                'x_range': list(x_range),
                'step_size': step,
                'points': points,
                'critical_points': self.find_critical_points(self.current_func, x_range)
            }
            
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
                
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(tk.END, f"Points exported to {filename}\n")
            self.info_text.insert(tk.END, f"Total points: {len(points)}\n")
            
        except Exception as e:
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(tk.END, f"Error exporting points: {str(e)}")

    def generate_new(self):
        self.plot_function()
        
    def refresh(self):
        if self.current_func:
            self.plot_function()
        
    def run(self):
        # Center the window on screen
        window_width = 1200
        window_height = 800
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        center_x = int(screen_width/2 - window_width/2)
        center_y = int(screen_height/2 - window_height/2)
        
        self.root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        
        # Configure grid weights for resizing
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Bind keyboard shortcuts
        self.root.bind('<Control-n>', lambda e: self.generate_new())
        self.root.bind('<Control-r>', lambda e: self.refresh())
        self.root.bind('<Control-e>', lambda e: self.export_points())
        
        # Start the application
        self.generate_new()
        self.root.mainloop()

def create_custom_style():
    """Create custom styling for the application"""
    style = {
        'bg_dark': '#2b2b2b',
        'bg_medium': '#404040',
        'text_color': 'white',
        'accent_color': 'cyan',
        'button_hover': '#505050',
        'critical_point_colors': {
            'intercept': 'red',
            'extreme': 'yellow',
            'inflection': 'green'
        }
    }
    return style

def main():
    try:
        # Set up application
        generator = EnhancedFunctionGenerator()
        generator.run()
    except Exception as e:
        print(f"Error starting application: {str(e)}")
        
if __name__ == "__main__":
    main()