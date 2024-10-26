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
        
    def visualize_results(self, image, grid_info, graph_points):
        """Visualize detected grid and graph"""
        # Draw grid
        result = self.grid_detector.overlay_grid(image, grid_info)
        
        # Draw graph points
        if len(graph_points) > 0:
            for point in graph_points:
                px = int(point[0] * grid_info.x_scale + grid_info.origin[0])
                py = int(grid_info.origin[1] - point[1] * grid_info.y_scale)
                cv2.circle(result, (px, py), 1, (255, 0, 0), -1)
        
        return result