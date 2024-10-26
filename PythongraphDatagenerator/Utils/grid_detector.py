import cv2
import numpy as np
from dataclasses import dataclass

@dataclass
class GridInfo:
    x_lines: np.ndarray
    y_lines: np.ndarray
    origin: tuple
    x_scale: float
    y_scale: float
    x_intercepts: list
    y_intercepts: list
    critical_points: list

class GridDetector:
    def __init__(self):
        self.min_line_length = 100
        self.max_line_gap = 10
        
    def detect_grid(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        
        # Detect lines using HoughLinesP
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, 50,
                               minLineLength=self.min_line_length,
                               maxLineGap=self.max_line_gap)
        
        if lines is None:
            return None
        
        # Separate horizontal and vertical lines
        h_lines = []
        v_lines = []
        
        for line in lines:
            x1, y1, x2, y2 = line[0]
            angle = np.abs(np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi)
            
            if angle < 20:  # Horizontal
                h_lines.append((x1, y1, x2, y2))
            elif angle > 70:  # Vertical
                v_lines.append((x1, y1, x2, y2))
        
        # Find origin (intersection of axes)
        origin = self.find_origin(h_lines, v_lines)
        
        # Calculate scale
        x_scale = self.calculate_scale(v_lines)
        y_scale = self.calculate_scale(h_lines)
        
        return GridInfo(
            x_lines=np.array(v_lines),
            y_lines=np.array(h_lines),
            origin=origin,
            x_scale=x_scale,
            y_scale=y_scale,
            x_intercepts=[],
            y_intercepts=[],
            critical_points=[]
        )
    
    def find_origin(self, h_lines, v_lines):
        # Find the main axes (usually the darkest/most prominent lines)
        main_horizontal = self.find_main_axis(h_lines)
        main_vertical = self.find_main_axis(v_lines)
        
        if main_horizontal and main_vertical:
            # Calculate intersection
            x1, y1, x2, y2 = main_horizontal
            x3, y3, x4, y4 = main_vertical
            
            denominator = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
            if denominator == 0:
                return None
                
            px = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / denominator
            py = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / denominator
            
            return (int(px), int(py))
        
        return None
    
    def find_main_axis(self, lines):
        if not lines:
            return None
            
        # Find the line closest to the center
        center_lines = sorted(lines, key=lambda l: abs(l[1] - l[3]))
        return center_lines[0] if center_lines else None
    
    def calculate_scale(self, lines):
        if len(lines) < 2:
            return 1.0
            
        # Calculate average distance between parallel lines
        distances = []
        for i in range(len(lines)):
            for j in range(i + 1, len(lines)):
                dist = np.abs(lines[i][0] - lines[j][0])  # For vertical lines
                if dist > 10:  # Minimum distance threshold
                    distances.append(dist)
        
        return np.mean(distances) if distances else 1.0
    
    def find_critical_points(self, graph_points, grid_info):
        x = graph_points[:, 0]
        y = graph_points[:, 1]
        
        critical_points = []
        
        # Find local maxima and minima
        for i in range(1, len(x) - 1):
            if y[i-1] < y[i] > y[i+1]:  # Local maximum
                critical_points.append(('max', x[i], y[i]))
            elif y[i-1] > y[i] < y[i+1]:  # Local minimum
                critical_points.append(('min', x[i], y[i]))
        
        # Find x-intercepts
        for i in range(len(x) - 1):
            if (y[i] * y[i+1]) <= 0:  # Sign change indicates crossing x-axis
                x_intercept = x[i] - y[i] * (x[i+1] - x[i]) / (y[i+1] - y[i])
                critical_points.append(('x_intercept', x_intercept, 0))
        
        # Find y-intercepts
        for i in range(len(x) - 1):
            if (x[i] * x[i+1]) <= 0:  # Sign change indicates crossing y-axis
                y_intercept = y[i] - x[i] * (y[i+1] - y[i]) / (x[i+1] - x[i])
                critical_points.append(('y_intercept', 0, y_intercept))
        
        return critical_points

    def overlay_grid(self, image, grid_info):
        """Draw detected grid lines and critical points on the image"""
        result = image.copy()
        
        # Draw horizontal lines
        for line in grid_info.y_lines:
            x1, y1, x2, y2 = line
            cv2.line(result, (x1, y1), (x2, y2), (0, 255, 0), 1)
        
        # Draw vertical lines
        for line in grid_info.x_lines:
            x1, y1, x2, y2 = line
            cv2.line(result, (x1, y1), (x2, y2), (0, 255, 0), 1)
        
        # Draw origin
        if grid_info.origin:
            cv2.circle(result, grid_info.origin, 5, (0, 0, 255), -1)
        
        # Draw critical points
        for point_type, x, y in grid_info.critical_points:
            color = {
                'max': (255, 0, 0),
                'min': (0, 0, 255),
                'x_intercept': (0, 255, 0),
                'y_intercept': (255, 255, 0)
            }.get(point_type, (128, 128, 128))
            
            px = int(x * grid_info.x_scale + grid_info.origin[0])
            py = int(grid_info.origin[1] - y * grid_info.y_scale)
            cv2.circle(result, (px, py), 3, color, -1)
        
        return result