import cv2
import numpy as np
from .grid_detector import GridDetector

class ImageProcessor:
    def __init__(self):
        self.grid_detector = GridDetector()
        
    def preprocess_image(self, image):
        """Preprocess image for graph detection"""
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply adaptive thresholding
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        binary = cv2.adaptiveThreshold(
            blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY_INV, 11, 2
        )
        
        # Morphological operations
        kernel = np.ones((3,3), np.uint8)
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
        
        return binary

    def visualize_grid(self, image, grid_info):
        """Visualize only the grid detection results"""
        if grid_info is None:
            return image.copy()
            
        result = image.copy()
        
        # Draw grid lines in different colors
        # Horizontal lines in blue
        for line in grid_info.y_lines:
            x1, y1, x2, y2 = line
            cv2.line(result, (x1, y1), (x2, y2), (255, 0, 0), 1)
        
        # Vertical lines in green
        for line in grid_info.x_lines:
            x1, y1, x2, y2 = line
            cv2.line(result, (x1, y1), (x2, y2), (0, 255, 0), 1)
        
        # Draw origin in red with larger circle
        if grid_info.origin:
            cv2.circle(result, grid_info.origin, 7, (0, 0, 255), -1)
            
        # Add grid scale information
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(result, f"X Scale: {grid_info.x_scale:.2f}", 
                   (10, 30), font, 0.7, (255, 255, 255), 2)
        cv2.putText(result, f"Y Scale: {grid_info.y_scale:.2f}",
                   (10, 60), font, 0.7, (255, 255, 255), 2)
        
        return result

    def visualize_function(self, image, points, grid_info):
        """Visualize only the function detection results"""
        if points is None or len(points) == 0:
            return image.copy()
            
        result = image.copy()
        
        # Draw the function points in red
        if len(points) > 0:
            # Create point coordinates
            coords = []
            for point in points:
                px = int(point[0] * grid_info.x_scale + grid_info.origin[0])
                py = int(grid_info.origin[1] - point[1] * grid_info.y_scale)
                coords.append((px, py))
            
            # Draw points
            for px, py in coords:
                cv2.circle(result, (px, py), 2, (0, 0, 255), -1)
            
            # Draw lines between points for continuity
            coords = np.array(coords)
            cv2.polylines(result, [coords], False, (255, 0, 0), 1)
        
        # Draw critical points
        if grid_info and grid_info.critical_points:
            for point_type, x, y in grid_info.critical_points:
                px = int(x * grid_info.x_scale + grid_info.origin[0])
                py = int(grid_info.origin[1] - y * grid_info.y_scale)
                
                # Different colors for different types of critical points
                color = {
                    'max': (255, 255, 0),  # Yellow for maxima
                    'min': (0, 255, 255),  # Cyan for minima
                    'x_intercept': (0, 255, 0),  # Green for x-intercepts
                    'y_intercept': (255, 0, 255)  # Magenta for y-intercepts
                }.get(point_type, (255, 255, 255))
                
                # Draw larger circles for critical points
                cv2.circle(result, (px, py), 5, color, -1)
                
                # Add labels
                label = {
                    'max': 'Max',
                    'min': 'Min',
                    'x_intercept': 'X-Int',
                    'y_intercept': 'Y-Int'
                }.get(point_type, '')
                
                font = cv2.FONT_HERSHEY_SIMPLEX
                cv2.putText(result, label, (px + 10, py - 10), 
                           font, 0.5, color, 1)
        
        return result

    def visualize_results(self, image, grid_info, graph_points):
        """Visualize complete results with both grid and function"""
        # Start with grid visualization
        result = self.visualize_grid(image, grid_info)
        
        # Add function visualization on top
        if len(graph_points) > 0:
            # Draw function points in a different color
            for point in graph_points:
                px = int(point[0] * grid_info.x_scale + grid_info.origin[0])
                py = int(grid_info.origin[1] - point[1] * grid_info.y_scale)
                cv2.circle(result, (px, py), 1, (255, 165, 0), -1)  # Orange color
        
        return result

    def extract_graph_points(self, image, grid_info):
        """Extract graph points with grid-aware processing"""
        binary = self.preprocess_image(image)
        
        # Find contours
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        if not contours:
            return []
        
        # Get the main graph contour
        graph_contour = max(contours, key=lambda c: cv2.arcLength(c, False))
        
        # Smooth the contour
        epsilon = 0.001 * cv2.arcLength(graph_contour, False)
        smoothed_contour = cv2.approxPolyDP(graph_contour, epsilon, False)
        
        # Convert to points and sort by x coordinate
        points = smoothed_contour.reshape(-1, 2)
        points = points[points[:, 0].argsort()]
        
        # Convert to grid coordinates
        if grid_info and grid_info.origin:
            grid_points = []
            for x, y in points:
                grid_x = (x - grid_info.origin[0]) / grid_info.x_scale
                grid_y = (grid_info.origin[1] - y) / grid_info.y_scale
                grid_points.append([grid_x, grid_y])
            return np.array(grid_points)
        
        return points
    
    def process_image(self, image):
        """Complete image processing pipeline"""
        # Detect grid
        grid_info = self.grid_detector.detect_grid(image)
        
        # Extract graph points
        graph_points = self.extract_graph_points(image, grid_info)
        
        # Find critical points
        if len(graph_points) > 0:
            critical_points = self.grid_detector.find_critical_points(graph_points, grid_info)
            if grid_info:
                grid_info.critical_points = critical_points
        
        return graph_points, grid_info