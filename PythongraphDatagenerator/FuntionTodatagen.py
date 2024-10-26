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

from Utils.grid_detector import GridDetector
from Utils.image_processing import ImageProcessor
from Utils.function_optimizer import FunctionOptimizer
from Utils.plot_manager import PlotManager
from Utils.math_Utils import MathUtils

class FunctionDecoder:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Function Graph Decoder")
        self.root.geometry("800x600")
        
        # Configure root grid
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        
        # Initialize components
        self.image_processor = ImageProcessor()
        self.function_optimizer = FunctionOptimizer(max_attempts=1000)
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
        main_frame.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=3)
        
        # Setup panels
        self.setup_left_panel(main_frame)
        self.setup_right_panel(main_frame)
        
    def setup_left_panel(self, parent):
        left_panel = ttk.Frame(parent)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        
        # Image display
        image_frame = ttk.LabelFrame(left_panel, text="Input Graph", padding=2)
        image_frame.pack(fill="both", expand=True)
        
        self.image_label = ttk.Label(image_frame)
        self.image_label.pack(padx=2, pady=2)
        
        # Controls
        controls = ttk.Frame(left_panel)
        controls.pack(fill="x", pady=5)
        
        ttk.Button(controls, text="Load", command=self.load_image, width=8).pack(side="left", padx=2)
        ttk.Button(controls, text="Start", command=self.start_processing, width=8).pack(side="left", padx=2)
        ttk.Button(controls, text="Stop", command=self.stop_processing, width=8).pack(side="left", padx=2)
        
        # Grid Detection Toggle
        self.show_grid_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(controls, text="Show Grid", variable=self.show_grid_var,
                       command=self.toggle_grid).pack(side="left", padx=10)
        
        # Status
        self.status_text = tk.StringVar(value="Ready")
        ttk.Label(left_panel, textvariable=self.status_text, font=('Arial', 8)).pack(fill="x")
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(left_panel, variable=self.progress_var, mode='determinate')
        self.progress.pack(fill="x", pady=2)
        
        # Results display
        results_frame = ttk.LabelFrame(left_panel, text="Results", padding=2)
        results_frame.pack(fill="both", expand=True)
        
        self.results_text = tk.Text(results_frame, height=6, width=30, font=('Courier', 8))
        self.results_text.pack(fill="both", expand=True, pady=2)
        
    def setup_right_panel(self, parent):
        right_panel = ttk.Frame(parent)
        right_panel.grid(row=0, column=1, sticky="nsew")
        
        # Embed plot manager's canvas
        self.plot_manager.fig.canvas = FigureCanvasTkAgg(self.plot_manager.fig, master=right_panel)
        self.plot_manager.fig.canvas.draw()
        self.plot_manager.fig.canvas.get_tk_widget().pack(fill="both", expand=True)
        
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
            
            # Display processed image
            display_image = self.image_processor.visualize_results(
                self.current_image, self.grid_info, self.normalized_points
            )
            
            # Convert for display
            image_rgb = cv2.cvtColor(display_image, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(image_rgb)
            
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
        threading.Thread(
            target=self.optimization_thread,
            daemon=True
        ).start()
        
        # Start display updates
        self.update_display()
    
    def optimization_thread(self):
        try:
            # Estimate initial parameters
            initial_params = self.math_Utils.estimate_function_parameters(
                self.normalized_points,
                self.grid_info.critical_points if self.grid_info else None
            )
            
            # Run optimization
            best_params, best_error = self.function_optimizer.optimize(
                self.normalized_points[:, 0],
                self.normalized_points[:, 1],
                self.grid_info.critical_points if self.grid_info else None,
                self.update_queue
            )
            
            # Final update
            self.update_queue.put(None)
            
        except Exception as e:
            self.status_text.set(f"Optimization error: {str(e)}")
            self.is_processing = False
    
    def update_display(self):
        if not self.is_processing:
            return
        
        try:
            while True:
                update = self.update_queue.get_nowait()
                
                if update is None:
                    self.is_processing = False
                    break
                
                # Update progress and status
                self.progress_var.set((update.generation / self.function_optimizer.max_attempts) * 100)
                self.status_text.set(f"Iteration {update.generation + 1}: Error = {update.error:.6f}")
                
                # Update plots
                self.plot_manager.update_plots(
                    self.normalized_points,
                    update.params,
                    [update.error],
                    self.grid_info if self.show_grid_var.get() else None
                )
                
                # Update function text
                if update.generation % 10 == 0:
                    function_str = (f"f(x) = ({update.params[0]:.3f}x³ + "
                                  f"{update.params[1]:.3f}x² + "
                                  f"{update.params[2]:.3f}x + "
                                  f"{update.params[3]:.3f})/4")
                    self.results_text.delete(1.0, tk.END)
                    self.results_text.insert(tk.END, function_str)
                    
                    # Add critical points if available
                    if self.grid_info and self.grid_info.critical_points:
                        self.results_text.insert(tk.END, "\n\nCritical Points:\n")
                        for point_type, x, y in self.grid_info.critical_points:
                            self.results_text.insert(tk.END, f"{point_type}: ({x:.2f}, {y:.2f})\n")
                
        except queue.Empty:
            pass
        
        # Schedule next update
        if self.is_processing:
            self.root.after(20, self.update_display)
    
    def stop_processing(self):
        self.is_processing = False
        self.status_text.set("Processing stopped")
    
    def toggle_grid(self):
        if self.current_image is not None and self.normalized_points is not None:
            self.plot_manager.update_plots(
                self.normalized_points,
                self.function_optimizer.best_params if hasattr(self.function_optimizer, 'best_params') else None,
                [],
                self.grid_info if self.show_grid_var.get() else None
            )
    
    def on_closing(self):
        if self.is_processing:
            self.stop_processing()
        self.root.destroy()
    
    def run(self):
        # Configure window behavior
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Start application
        self.root.mainloop()

if __name__ == "__main__":
    try:
        # Set DPI awareness for Windows
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass
    
    # Start application
    app = FunctionDecoder()
    app.run()