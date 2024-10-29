import tkinter as tk
from tkinter import filedialog, ttk
import cv2
import numpy as np
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import queue
import threading
import time
from scipy.optimize import curve_fit, minimize
from scipy import interpolate
import numpy.linalg as la

from Utils.grid_detector import GridDetector
from Utils.image_processing import ImageProcessor
from Utils.plot_manager import PlotManager
from Utils.math_Utils import MathUtils
from Utils.function_optimizer import OptimizationResult

class EnhancedFunctionDecoder:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Enhanced Function Graph Decoder")
        self.root.geometry("1200x800")
        
        # Configure root grid
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        
        # Initialize components
        self.image_processor = ImageProcessor()
        self.plot_manager = PlotManager()
        self.math_Utils = MathUtils()
        
        # Variables
        self.current_image = None
        self.grid_info = None
        self.normalized_points = None
        self.is_processing = False
        self.update_queue = queue.Queue()
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding=5)
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Configure grid layout
        main_frame.rowconfigure(0, weight=1)
        for i in range(3):
            main_frame.columnconfigure(i, weight=1)
        
        # Setup three panels
        self.setup_control_panel(main_frame)
        self.setup_grid_panel(main_frame)
        self.setup_function_panel(main_frame)
        
    def setup_control_panel(self, parent):
        control_panel = ttk.LabelFrame(parent, text="Controls", padding=5)
        control_panel.grid(row=0, column=0, sticky="nsew", padx=5)
        
        # Image display
        image_frame = ttk.LabelFrame(control_panel, text="Input Graph", padding=2)
        image_frame.pack(fill="both", expand=True)
        
        self.image_label = ttk.Label(image_frame)
        self.image_label.pack(padx=2, pady=2)
        
        # Controls
        controls = ttk.Frame(control_panel)
        controls.pack(fill="x", pady=5)
        
        ttk.Button(controls, text="Load", command=self.load_image, width=8).pack(side="left", padx=2)
        ttk.Button(controls, text="Start", command=self.start_processing, width=8).pack(side="left", padx=2)
        ttk.Button(controls, text="Stop", command=self.stop_processing, width=8).pack(side="left", padx=2)
        
        # Optimization method selection
        method_frame = ttk.Frame(control_panel)
        method_frame.pack(fill="x", pady=5)
        ttk.Label(method_frame, text="Optimization Method:").pack(side="left")
        self.method_var = tk.StringVar(value="vectorized")
        ttk.Radiobutton(method_frame, text="Vectorized", variable=self.method_var, 
                       value="vectorized").pack(side="left")
        ttk.Radiobutton(method_frame, text="Curve Fit", variable=self.method_var,
                       value="curve_fit").pack(side="left")
        
        # Status and progress
        self.status_text = tk.StringVar(value="Ready")
        ttk.Label(control_panel, textvariable=self.status_text).pack(fill="x")
        
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(control_panel, variable=self.progress_var, mode='determinate')
        self.progress.pack(fill="x", pady=2)
        
        # Results display
        results_frame = ttk.LabelFrame(control_panel, text="Results", padding=2)
        results_frame.pack(fill="both", expand=True)
        
        self.results_text = tk.Text(results_frame, height=6, width=30, font=('Courier', 8))
        self.results_text.pack(fill="both", expand=True, pady=2)
        
    def setup_grid_panel(self, parent):
        grid_panel = ttk.LabelFrame(parent, text="Grid Detection", padding=5)
        grid_panel.grid(row=0, column=1, sticky="nsew", padx=5)
        
        self.grid_canvas = FigureCanvasTkAgg(plt.Figure(figsize=(6, 8)), master=grid_panel)
        self.grid_canvas.get_tk_widget().pack(fill="both", expand=True)
        self.grid_ax = self.grid_canvas.figure.add_subplot(111)
        
    def setup_function_panel(self, parent):
        function_panel = ttk.LabelFrame(parent, text="Function Detection", padding=5)
        function_panel.grid(row=0, column=2, sticky="nsew", padx=5)
        
        self.function_canvas = FigureCanvasTkAgg(plt.Figure(figsize=(6, 8)), master=function_panel)
        self.function_canvas.get_tk_widget().pack(fill="both", expand=True)
        self.function_ax = self.function_canvas.figure.add_subplot(111)
        
    def vectorized_optimization(self, x, y, critical_points=None):
        """Optimized vectorized parameter estimation"""
        # Create design matrix for cubic function
        X = np.vstack([x**3, x**2, x, np.ones_like(x)]).T
        
        # Use SVD for stable solution
        U, S, Vh = la.svd(X, full_matrices=False)
        
        # Calculate parameters using pseudo-inverse
        params = Vh.T @ (1/S * (U.T @ y))
        params = params / 4  # Scale parameters
        
        # Refine using L-BFGS-B if critical points are available
        if critical_points:
            def objective(p):
                pred = self.target_function(x, *p)
                mse = np.mean((y - pred)**2)
                
                # Add critical points constraint
                critical_error = 0
                for point_type, px, py in critical_points:
                    pred_y = self.target_function(np.array([px]), *p)
                    critical_error += np.abs(pred_y - py)[0]
                
                return mse + 0.1 * critical_error
            
            result = minimize(objective, params, method='L-BFGS-B')
            params = result.x
            
        return params
    
    def curve_fit_optimization(self, x, y, critical_points=None):
        """Optimization using scipy's curve_fit"""
        def target_func(x, a, b, c, d):
            return (a * np.power(x, 3) + b * np.power(x, 2) + c * x + d) / 4
        
        # Get initial parameter estimates
        p0 = self.vectorized_optimization(x, y)
        
        # Perform curve fitting
        params, _ = curve_fit(target_func, x, y, p0=p0, maxfev=1000)
        
        return params
    
    def target_function(self, x, a, b, c, d):
        """Vectorized target function"""
        return (a * np.power(x, 3) + b * np.power(x, 2) + c * x + d) / 4
    
    def optimization_thread(self):
        try:
            x = self.normalized_points[:, 0]
            y = self.normalized_points[:, 1]
            
            # Choose optimization method
            if self.method_var.get() == "vectorized":
                params = self.vectorized_optimization(x, y, self.grid_info.critical_points)
            else:
                params = self.curve_fit_optimization(x, y, self.grid_info.critical_points)
            
            # Calculate error
            pred_y = self.target_function(x, *params)
            error = np.mean((y - pred_y)**2)
            
            # Update display
            self.update_queue.put(OptimizationResult(params, error, "cubic", 0))
            self.update_queue.put(None)
            
        except Exception as e:
            self.status_text.set(f"Optimization error: {str(e)}")
            self.is_processing = False
    
    def update_visualizations(self):
        if self.current_image is None:
            return
        
    # Update grid visualization
        grid_image = self.image_processor.visualize_grid(self.current_image, self.grid_info)
        self.grid_ax.clear()
        self.grid_ax.imshow(cv2.cvtColor(grid_image, cv2.COLOR_BGR2RGB))
        self.grid_ax.axis('off')
        self.grid_canvas.draw()
    
    # Update function visualization
        function_image = self.image_processor.visualize_function(
            self.current_image, self.normalized_points, self.grid_info
        )
        self.function_ax.clear()
        self.function_ax.imshow(cv2.cvtColor(function_image, cv2.COLOR_BGR2RGB))
        self.function_ax.axis('off')
        self.function_canvas.draw()
    
    def load_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp")]
        )
        if not file_path:
            return
            
        try:
            self.status_text.set("Loading image...")
            
            # Load and process image
            self.current_image = cv2.imread(file_path)
            if self.current_image is None:
                raise ValueError("Failed to load image")
            
            # Process image and detect grid
            self.normalized_points, self.grid_info = self.image_processor.process_image(self.current_image)
            
            # Update visualizations
            self.update_visualizations()
            
            # Display input image
            display_image = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(display_image)
            
            # Resize maintaining aspect ratio
            display_height = 200
            aspect_ratio = pil_image.width / pil_image.height
            display_width = int(display_height * aspect_ratio)
            pil_image = pil_image.resize((display_width, display_height), Image.Resampling.LANCZOS)
            
            # Update display
            photo = ImageTk.PhotoImage(pil_image)
            self.image_label.configure(image=photo)
            self.image_label.image = photo
            
            self.status_text.set("Image loaded successfully")
            
        except Exception as e:
            self.status_text.set(f"Error: {str(e)}")
    
    def start_processing(self):
        if self.current_image is None:
            self.status_text.set("Please load an image first")
            return
        
        if not self.normalized_points.size:
            self.status_text.set("No graph points detected")
            return
        
        self.is_processing = True
        self.results_text.delete(1.0, tk.END)
        self.progress_var.set(0)
        
        # Start optimization in background thread
        threading.Thread(target=self.optimization_thread, daemon=True).start()
        
        # Start display updates
        self.update_display()
    
    def update_display(self):
        if not self.is_processing:
            return
        
        try:
            while True:
                update = self.update_queue.get_nowait()
                
                if update is None:
                    self.is_processing = False
                    break
                
                # Update progress
                self.progress_var.set(100)
                self.status_text.set(f"Optimization complete: Error = {update.error:.6f}")
                
                # Update function text
                function_str = (f"f(x) = ({update.params[0]:.3f}x³ + "
                              f"{update.params[1]:.3f}x² + "
                              f"{update.params[2]:.3f}x + "
                              f"{update.params[3]:.3f})/4")
                self.results_text.delete(1.0, tk.END)
                self.results_text.insert(tk.END, function_str)
                
                # Add critical points
                if self.grid_info and self.grid_info.critical_points:
                    self.results_text.insert(tk.END, "\n\nCritical Points:\n")
                    for point_type, x, y in self.grid_info.critical_points:
                        self.results_text.insert(tk.END, f"{point_type}: ({x:.2f}, {y:.2f})\n")
                        
                # Update visualizations
                self.update_visualizations()
                
        except queue.Empty:
            pass
        
        # Schedule next update
        if self.is_processing:
            self.root.after(20, self.update_display)
    
    def stop_processing(self):
        self.is_processing = False
        self.status_text.set("Processing stopped")
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    try:
        # Set DPI awareness for Windows
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass
    
    # Start application
    app = EnhancedFunctionDecoder()
    app.run()