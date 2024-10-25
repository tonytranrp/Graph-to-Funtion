using System;
using System.Collections.Generic;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Media;
using System.Windows.Shapes;

namespace WpfApp1.Utils
{
    public static class FunctionRenderer
    {
        public static List<Point> GenerateContinuousPoints(
            Canvas graphCanvas,
            Func<double, double> function,
            double minX,
            double maxX)
        {
            var points = new List<Point>();
            double step = 1.0 / GraphSettings.POINTS_PER_UNIT;

            // Extend beyond visible area for smooth transitions
            double extendedMinX = minX * GraphSettings.EXTENSION_FACTOR;
            double extendedMaxX = maxX * GraphSettings.EXTENSION_FACTOR;

            for (double x = extendedMinX; x <= extendedMaxX; x += step)
            {
                try
                {
                    double y = function(x);
                    if (!double.IsInfinity(y) && !double.IsNaN(y))
                    {
                        points.Add(new Point(x, y));
                    }
                }
                catch
                {
                    // Skip points where function is undefined
                }
            }
            return points;
        }

        public static Polyline CreateSmoothCurve(List<Point> points, Canvas graphCanvas)
        {
            var screenPoints = new PointCollection();
            foreach (var point in points)
            {
                double screenX = (point.X * GraphDrawingUtils.GRID_SIZE) + graphCanvas.ActualWidth / 2;
                double screenY = -(point.Y * GraphDrawingUtils.GRID_SIZE) + graphCanvas.ActualHeight / 2;
                screenPoints.Add(new Point(screenX, screenY));
            }

            return new Polyline
            {
                Points = screenPoints,
                Stroke = GraphSettings.Styles.FunctionColor,
                StrokeThickness = 2,
                StrokeLineJoin = PenLineJoin.Round
            };
        }

        public static Path CreateBezierCurve(List<Point> points, Canvas graphCanvas)
        {
            if (points.Count < 2) return null;

            var geometry = new PathGeometry();
            var figure = new PathFigure();

            // Convert first point to screen coordinates
            double screenX = (points[0].X * GraphDrawingUtils.GRID_SIZE) + graphCanvas.ActualWidth / 2;
            double screenY = -(points[0].Y * GraphDrawingUtils.GRID_SIZE) + graphCanvas.ActualHeight / 2;
            figure.StartPoint = new Point(screenX, screenY);

            for (int i = 1; i < points.Count; i++)
            {
                screenX = (points[i].X * GraphDrawingUtils.GRID_SIZE) + graphCanvas.ActualWidth / 2;
                screenY = -(points[i].Y * GraphDrawingUtils.GRID_SIZE) + graphCanvas.ActualHeight / 2;
                var endPoint = new Point(screenX, screenY);

                // Calculate control points for smooth curve
                var controlPoint1 = new Point(
                    (figure.StartPoint.X + endPoint.X) / 2,
                    figure.StartPoint.Y
                );
                var controlPoint2 = new Point(
                    (figure.StartPoint.X + endPoint.X) / 2,
                    endPoint.Y
                );

                var segment = new BezierSegment(controlPoint1, controlPoint2, endPoint, true);
                figure.Segments.Add(segment);
                figure.StartPoint = endPoint;
            }

            geometry.Figures.Add(figure);
            return new Path
            {
                Data = geometry,
                Stroke = GraphSettings.Styles.FunctionColor,
                StrokeThickness = 2
            };
        }
    }
}