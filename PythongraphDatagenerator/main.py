import numpy as np
import matplotlib.pyplot as plt
from random import choice, uniform
from scipy.optimize import fsolve
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy.misc import derivative
import json

class InteractiveFunctionGenerator:
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
        self.setup_gui()
        
    def setup_gui(self):
        self.root = tk.Tk()
        self.root.title("Function Generator")
        
        main_frame = tk.Frame(self.root)
        main_frame.pack(padx=10, pady=10)
        
        tk.Label(main_frame, text="Select function type:").pack()
        self.func_type_var = tk.StringVar(value=self.function_types[0])
        func_type_menu = tk.OptionMenu(main_frame, self.func_type_var, *self.function_types)
        func_type_menu.pack()
        
        range_frame = tk.Frame(main_frame)
        range_frame.pack(pady=10)
        
        tk.Label(range_frame, text="X range:").grid(row=0, column=0)
        self.x_min = tk.Entry(range_frame, width=5)
        self.x_min.insert(0, "-5")
        self.x_min.grid(row=0, column=1)
        tk.Label(range_frame, text="to").grid(row=0, column=2)
        self.x_max = tk.Entry(range_frame, width=5)
        self.x_max.insert(0, "12")
        self.x_max.grid(row=0, column=3)
        
        tk.Label(range_frame, text="Y range:").grid(row=1, column=0)
        self.y_min = tk.Entry(range_frame, width=5)
        self.y_min.insert(0, "-5")
        self.y_min.grid(row=1, column=1)
        tk.Label(range_frame, text="to").grid(row=1, column=2)
        self.y_max = tk.Entry(range_frame, width=5)
        self.y_max.insert(0, "5")
        self.y_max.grid(row=1, column=3)
        
        button_frame = tk.Frame(main_frame)
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="Generate", command=self.generate_new).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Refresh", command=self.refresh).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Export Points", command=self.export_points).pack(side=tk.LEFT, padx=5)
        
        step_frame = tk.Frame(main_frame)
        step_frame.pack(pady=5)
        tk.Label(step_frame, text="Step size:").pack(side=tk.LEFT)
        self.step_size = tk.Entry(step_frame, width=5)
        self.step_size.insert(0, "0.1")
        self.step_size.pack(side=tk.LEFT, padx=5)
        
        self.fig, self.ax = plt.subplots(figsize=(8, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=main_frame)
        self.canvas.get_tk_widget().pack()
        
        self.info_text = tk.Text(main_frame, height=6, width=50)
        self.info_text.pack(pady=10)

    def generate_points(self, func, x_range, step):
        points = []
        x = np.arange(x_range[0], x_range[1] + step, step)
        
        try:
            y = func(x)
            mask = np.isfinite(y)
            x, y = x[mask], y[mask]
            
            for xi, yi in zip(x, y):
                points.append({
                    'x': round(float(xi), 6),
                    'y': round(float(yi), 6)
                })
                
        except Exception as e:
            print(f"Error generating points: {e}")
            
        return points

    def export_points(self):
        if self.current_func is None:
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(tk.END, "Please generate a function first")
            return
            
        try:
            x_range = (float(self.x_min.get()), float(self.x_max.get()))
            step = float(self.step_size.get())
            
            points = self.generate_points(self.current_func, x_range, step)
            
            filename = f"function_points_{self.func_type_var.get()}_{len(points)}.json"
            
            with open(filename, 'w') as f:
                json.dump({
                    'function_type': self.func_type_var.get(),
                    'label': self.current_label,
                    'x_range': list(x_range),
                    'step_size': step,
                    'points': points
                }, f, indent=2)
                
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(tk.END, f"Points exported to {filename}\n")
            self.info_text.insert(tk.END, f"Total points: {len(points)}\n")
            
        except ValueError:
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(tk.END, "Please enter valid numbers for ranges and step size")
            
    def generate_random_function(self):
        func_type = self.func_type_var.get()
        
        a = uniform(0.5, 2)
        b = uniform(-2, 2)
        c = uniform(-2, 2)
        
        if func_type == 'logarithmic':
            def func(x):
                return a * np.log(np.abs(b * x + c)) + uniform(-2, 2)
            label = f'{a:.2f} * ln(|{b:.2f}x + {c:.2f}|) + {uniform(-2, 2):.2f}'
            
        elif func_type == 'exponential':
            def func(x):
                return a * np.exp(b * x) + c
            label = f'{a:.2f} * e^({b:.2f}x) + {c:.2f}'
            
        elif func_type == 'rational':
            d = uniform(-2, 2)
            def func(x):
                return (a * x + b) / (c * x + d)
            label = f'({a:.2f}x + {b:.2f})/({c:.2f}x + {d:.2f})'
            
        elif func_type == 'trigonometric':
            trig_func = choice([np.sin, np.cos, np.tan])
            func_name = trig_func.__name__
            def func(x):
                return a * trig_func(b * x) + c
            label = f'{a:.2f} * {func_name}({b:.2f}x) + {c:.2f}'
            
        else:  # linear
            def func(x):
                return a * x + b
            label = f'{a:.2f}x + {b:.2f}'
        
        self.current_func = func
        self.current_label = label
        return func, label

    def find_critical_points(self, func, x_range):
        """Find critical points of the function"""
        critical_points = []
        x = np.linspace(x_range[0], x_range[1], 1000)
        
        # Find x-intercepts
        try:
            x_intercepts = []
            for x_i in x[::100]:  # Sample points to try
                root = fsolve(func, x_i)
                if x_range[0] <= root[0] <= x_range[1]:
                    y_val = abs(func(root[0]))
                    if y_val < 0.01:  # Threshold for considering it zero
                        x_intercepts.append(round(root[0], 3))
            x_intercepts = list(set([x_i for x_i in x_intercepts]))
            critical_points.append(f"X-intercepts: {x_intercepts}")
        except:
            critical_points.append("X-intercepts: Unable to calculate")
            
        # Find y-intercept
        try:
            y_intercept = func(0)
            critical_points.append(f"Y-intercept: {round(y_intercept, 3)}")
        except:
            critical_points.append("Y-intercept: Unable to calculate")
            
        # Find local extrema
        try:
            # Calculate derivative
            def deriv(x):
                h = 1e-7
                return (func(x + h) - func(x)) / h
                
            potential_extrema = []
            for x_i in x[1:-1]:
                if abs(deriv(x_i)) < 0.01:  # Close to zero derivative
                    potential_extrema.append((x_i, func(x_i)))
                    
            if potential_extrema:
                critical_points.append(f"Local extrema: {[(round(x, 3), round(y, 3)) for x, y in potential_extrema]}")
        except:
            critical_points.append("Local extrema: Unable to calculate")
            
        return critical_points

    def plot_function(self):
        try:
            x_range = (float(self.x_min.get()), float(self.x_max.get()))
            y_range = (float(self.y_min.get()), float(self.y_max.get()))
        except ValueError:
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(tk.END, "Please enter valid numbers for ranges")
            return
            
        func, label = self.generate_random_function()
        
        x = np.linspace(x_range[0], x_range[1], 1000)
        
        try:
            y = func(x)
            
            mask = np.isfinite(y)
            x, y = x[mask], y[mask]
            
            mask = (y >= y_range[0]) & (y <= y_range[1])
            x, y = x[mask], y[mask]
            
            self.ax.clear()
            
            self.ax.plot(x, y, label=label)
            self.ax.grid(True)
            self.ax.set_xlabel('x')
            self.ax.set_ylabel('y')
            self.ax.set_title(f'Random {self.func_type_var.get().capitalize()} Function')
            self.ax.legend()
            self.ax.axhline(y=0, color='k', linestyle='-', alpha=0.3)
            self.ax.axvline(x=0, color='k', linestyle='-', alpha=0.3)
            
            self.ax.set_xlim(x_range)
            self.ax.set_ylim(y_range)
            
            self.canvas.draw()
            
            critical_points = self.find_critical_points(func, x_range)
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(tk.END, f"Function: {label}\n\n")
            for point in critical_points:
                self.info_text.insert(tk.END, point + "\n")
                
        except Exception as e:
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(tk.END, f"Error generating function: {e}")

    def generate_new(self):
        self.plot_function()
        
    def refresh(self):
        self.plot_function()
        
    def run(self):
        self.generate_new()
        self.root.mainloop()

if __name__ == "__main__":
    generator = InteractiveFunctionGenerator()
    generator.run()