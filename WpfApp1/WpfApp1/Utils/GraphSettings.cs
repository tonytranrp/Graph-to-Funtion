using System.Windows.Media;

namespace WpfApp1.Utils
{
    public class GraphSettings
    {
        public const int POINTS_PER_UNIT = 10;
        public const double EXTENSION_FACTOR = 2.0;

        public class FunctionCondition
        {
            public required string Name { get; set; }
            public required string Description { get; set; }
            public bool IsEnabled { get; set; }
            public double Value { get; set; }
        }

        public static class Styles
        {
            public static readonly SolidColorBrush MainGridColor = new(Color.FromRgb(240, 240, 240));
            public static readonly SolidColorBrush SubGridColor = new(Color.FromRgb(220, 220, 220));
            public static readonly SolidColorBrush AxisColor = new(Color.FromRgb(0, 0, 0));
            public static readonly SolidColorBrush FunctionColor = new(Color.FromRgb(0, 120, 215));
            public static readonly SolidColorBrush PointColor = new(Color.FromRgb(0, 80, 155));
            public static readonly SolidColorBrush ToolTipBackgroundColor = new(Color.FromRgb(245, 245, 245));
        }
    }
}