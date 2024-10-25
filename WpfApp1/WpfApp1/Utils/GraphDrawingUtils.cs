using System;
using System.Collections.Generic;
using System.Linq;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Media;
using System.Windows.Shapes;

namespace WpfApp1.Utils
{
    public static class GraphDrawingUtils
    {
        public const double GRID_SIZE = 20; // 20 pixels per unit
        public const double POINT_RADIUS = 3;
        public const double MARGIN = 40; // Margin for labels

        public static void DrawCoordinateSystem(Canvas graphCanvas, Polyline connectionLine, List<Point> points)
        {
            graphCanvas.Children.Clear();
            graphCanvas.Children.Add(connectionLine);

            double centerX = graphCanvas.ActualWidth / 2;
            double centerY = graphCanvas.ActualHeight / 2;

            int maxX = (int)(graphCanvas.ActualWidth / (2 * GRID_SIZE));
            int maxY = (int)(graphCanvas.ActualHeight / (2 * GRID_SIZE));

            DrawGridLines(graphCanvas, centerX, centerY, maxX, maxY);
            UpdateConnectionLine(graphCanvas, connectionLine, points);
            foreach (var point in points)
            {
                DrawPoint(graphCanvas, point);
            }
        }

        private static void DrawGridLines(Canvas graphCanvas, double centerX, double centerY, int maxX, int maxY)
        {
            // Draw vertical lines and X-axis labels
            for (int x = -maxX; x <= maxX; x++)
            {
                double xPos = centerX + (x * GRID_SIZE);
                var gridLine = new Line
                {
                    Stroke = x == 0 ? Brushes.Black : Brushes.LightGray,
                    StrokeThickness = x == 0 ? 1.5 : 0.5,
                    X1 = xPos,
                    Y1 = 0,
                    X2 = xPos,
                    Y2 = graphCanvas.ActualHeight
                };
                graphCanvas.Children.Add(gridLine);

                if (x != 0)
                {
                    var textBlock = new TextBlock
                    {
                        Text = x.ToString(),
                        FontSize = 10
                    };
                    Canvas.SetLeft(textBlock, xPos - 5);
                    Canvas.SetTop(textBlock, centerY + 5);
                    graphCanvas.Children.Add(textBlock);
                }
            }

            // Draw horizontal lines and Y-axis labels
            for (int y = -maxY; y <= maxY; y++)
            {
                double yPos = centerY + (y * GRID_SIZE);
                var gridLine = new Line
                {
                    Stroke = y == 0 ? Brushes.Black : Brushes.LightGray,
                    StrokeThickness = y == 0 ? 1.5 : 0.5,
                    X1 = 0,
                    Y1 = yPos,
                    X2 = graphCanvas.ActualWidth,
                    Y2 = yPos
                };
                graphCanvas.Children.Add(gridLine);

                if (y != 0)
                {
                    var textBlock = new TextBlock
                    {
                        Text = (-y).ToString(),
                        FontSize = 10
                    };
                    Canvas.SetLeft(textBlock, centerX + 5);
                    Canvas.SetTop(textBlock, yPos - 7);
                    graphCanvas.Children.Add(textBlock);
                }
            }
        }

        public static void DrawPoint(Canvas graphCanvas, Point graphPoint, Brush color = null)
        {
            double screenX = (graphPoint.X * GRID_SIZE) + graphCanvas.ActualWidth / 2;
            double screenY = -(graphPoint.Y * GRID_SIZE) + graphCanvas.ActualHeight / 2;

            var ellipse = new Ellipse
            {
                Width = POINT_RADIUS * 2,
                Height = POINT_RADIUS * 2,
                Fill = color ?? Brushes.Blue
            };

            Canvas.SetLeft(ellipse, screenX - POINT_RADIUS);
            Canvas.SetTop(ellipse, screenY - POINT_RADIUS);
            graphCanvas.Children.Add(ellipse);
        }
        public static void DrawInfinityPoint(Canvas graphCanvas, Point point, bool positiveDirection)
        {
            double screenX = (point.X * GRID_SIZE) + graphCanvas.ActualWidth / 2;
            double screenY = -(point.Y * GRID_SIZE) + graphCanvas.ActualHeight / 2;

            // Draw point
            var ellipse = new Ellipse
            {
                Width = POINT_RADIUS * 2,
                Height = POINT_RADIUS * 2,
                Fill = Brushes.Red
            };
            Canvas.SetLeft(ellipse, screenX - POINT_RADIUS);
            Canvas.SetTop(ellipse, screenY - POINT_RADIUS);
            graphCanvas.Children.Add(ellipse);

            // Draw arrow
            var arrow = new Line
            {
                X1 = screenX,
                Y1 = screenY,
                X2 = screenX + (positiveDirection ? 20 : -20),
                Y2 = screenY,
                Stroke = Brushes.Red,
                StrokeThickness = 2
            };
            graphCanvas.Children.Add(arrow);

            // Draw arrowhead
            var arrowhead = new Polygon
            {
                Points = new PointCollection
                {
                    new Point(arrow.X2, arrow.Y2),
                    new Point(arrow.X2 + (positiveDirection ? -5 : 5), arrow.Y2 - 3),
                    new Point(arrow.X2 + (positiveDirection ? -5 : 5), arrow.Y2 + 3)
                },
                Fill = Brushes.Red
            };
            graphCanvas.Children.Add(arrowhead);
        }

        public static void UpdateConnectionLine(Canvas graphCanvas, Polyline connectionLine, List<Point> points)
        {
            if (points.Count == 0)
            {
                connectionLine.Points.Clear();
                return;
            }

            var screenPoints = new PointCollection();
            foreach (var point in points.OrderBy(p => p.X))
            {
                double screenX = (point.X * GRID_SIZE) + graphCanvas.ActualWidth / 2;
                double screenY = -(point.Y * GRID_SIZE) + graphCanvas.ActualHeight / 2;
                screenPoints.Add(new Point(screenX, screenY));
            }
            connectionLine.Points = screenPoints;
        }

        public static bool IsValidNewPoint(List<Point> points, Point newPoint)
        {
            return !points.Any(p => Math.Abs(p.X - newPoint.X) < 0.1);
        }

        public static Point ConvertToGraphCoordinates(Canvas graphCanvas, Point screenPoint)
        {
            double graphX = (screenPoint.X - graphCanvas.ActualWidth / 2) / GRID_SIZE;
            double graphY = -(screenPoint.Y - graphCanvas.ActualHeight / 2) / GRID_SIZE;

            // Round to nearest 0.1
            graphX = Math.Round(graphX * 10) / 10;
            graphY = Math.Round(graphY * 10) / 10;

            return new Point(graphX, graphY);
        }
    }
}