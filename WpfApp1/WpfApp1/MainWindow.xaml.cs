using System;
using System.Collections.Generic;
using System.Linq;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Shapes;
using WpfApp1.Utils;

namespace WpfApp1
{
    public partial class MainWindow : Window
    {
        private List<Point> points = new List<Point>();
        private Canvas graphCanvas;
        private Polyline connectionLine;
        private Path functionPath;
        private TextBox xMinAsymptote;
        private TextBox xMaxAsymptote;
        private TextBox yMinAsymptote;
        private TextBox yMaxAsymptote;
        private ComboBox functionType;
        private List<Point> infinityPoints = new List<Point>();
        private ToolTipManager toolTipManager;
        private GraphUtils.FunctionFit currentFit;
        private Dictionary<string, CheckBox> conditions = new Dictionary<string, CheckBox>();

        public MainWindow()
        {
            InitializeComponent();
            SetupWindow();
        }

        private void SetupWindow()
        {
            Title = "Graph Function Generator";
            Width = 800;
            Height = 700;
            Background = GraphSettings.Styles.MainGridColor;

            var mainGrid = CreateMainGrid();
            Content = mainGrid;

            var controlPanel = CreateControlPanel();
            mainGrid.Children.Add(controlPanel);

            var border = CreateGraphBorder();
            Grid.SetRow(border, 1);
            mainGrid.Children.Add(border);

            SetupGraphCanvas(border);
            InitializeTooltips();
        }

        private Grid CreateMainGrid()
        {
            var mainGrid = new Grid();
            mainGrid.RowDefinitions.Add(new RowDefinition { Height = new GridLength(100) });
            mainGrid.RowDefinitions.Add(new RowDefinition { Height = new GridLength(1, GridUnitType.Star) });
            return mainGrid;
        }

        private void InitializeTooltips()
        {
            toolTipManager = new ToolTipManager(graphCanvas);
            toolTipManager.AddCondition("Domain", "Function is defined for all real numbers", true);
            toolTipManager.AddCondition("Continuity", "Function is continuous", true);
        }

        private StackPanel CreateControlPanel()
        {
            var controlPanel = new StackPanel
            {
                Orientation = Orientation.Horizontal,
                Margin = new Thickness(10),
                Background = GraphSettings.Styles.ToolTipBackgroundColor
            };

            controlPanel.Children.Add(CreateFunctionTypePanel());
            controlPanel.Children.Add(CreateAsymptotePanel());
            controlPanel.Children.Add(CreateConditionsPanel());

            var infinityButton = new Button
            {
                Content = "Add Infinity Point",
                Margin = new Thickness(10, 0, 10, 0),
                Padding = new Thickness(5),
                Background = GraphSettings.Styles.FunctionColor,
                Foreground = Brushes.White
            };
            infinityButton.Click += AddInfinityPoint_Click;
            controlPanel.Children.Add(infinityButton);

            var generateButton = new Button
            {
                Content = "Generate Function",
                Width = 100,
                Height = 30,
                Margin = new Thickness(10),
                VerticalAlignment = VerticalAlignment.Center,
                Background = GraphSettings.Styles.FunctionColor,
                Foreground = Brushes.White
            };
            generateButton.Click += GenerateFunction_Click;
            controlPanel.Children.Add(generateButton);

            return controlPanel;
        }

        private StackPanel CreateFunctionTypePanel()
        {
            var typePanel = new StackPanel
            {
                Margin = new Thickness(10, 0, 10, 0)
            };
            typePanel.Children.Add(new TextBlock { Text = "Function Type:" });

            functionType = new ComboBox
            {
                Width = 120,
                Margin = new Thickness(0, 5, 0, 0)
            };
            functionType.Items.Add("Polynomial");
            functionType.Items.Add("Logarithmic");
            functionType.Items.Add("Exponential");
            functionType.Items.Add("Trigonometric");
            functionType.SelectedIndex = 0;

            typePanel.Children.Add(functionType);
            return typePanel;
        }

        private StackPanel CreateAsymptotePanel()
        {
            var asymptotePanel = new StackPanel
            {
                Margin = new Thickness(10, 0, 10, 0)
            };
            asymptotePanel.Children.Add(new TextBlock { Text = "Asymptotes:" });

            var asymptoteGrid = new Grid();
            asymptoteGrid.ColumnDefinitions.Add(new ColumnDefinition { Width = GridLength.Auto });
            asymptoteGrid.ColumnDefinitions.Add(new ColumnDefinition { Width = new GridLength(60) });

            for (int i = 0; i < 4; i++)
                asymptoteGrid.RowDefinitions.Add(new RowDefinition());

            AddAsymptoteInput(asymptoteGrid, 0, "X Min → ", out xMinAsymptote);
            AddAsymptoteInput(asymptoteGrid, 1, "X Max → ", out xMaxAsymptote);
            AddAsymptoteInput(asymptoteGrid, 2, "Y Min → ", out yMinAsymptote);
            AddAsymptoteInput(asymptoteGrid, 3, "Y Max → ", out yMaxAsymptote);

            asymptotePanel.Children.Add(asymptoteGrid);
            return asymptotePanel;
        }

        private StackPanel CreateConditionsPanel()
        {
            var conditionsPanel = new StackPanel
            {
                Margin = new Thickness(10, 0, 10, 0)
            };
            conditionsPanel.Children.Add(new TextBlock { Text = "Conditions:" });

            var conditionsGrid = new Grid();
            conditionsGrid.ColumnDefinitions.Add(new ColumnDefinition { Width = GridLength.Auto });
            conditionsGrid.ColumnDefinitions.Add(new ColumnDefinition { Width = new GridLength(100) });

            AddConditionRow(conditionsGrid, 0, "Continuous", true);
            AddConditionRow(conditionsGrid, 1, "Differentiable", true);
            AddConditionRow(conditionsGrid, 2, "Periodic", false);
            AddConditionRow(conditionsGrid, 3, "Bounded", false);

            conditionsPanel.Children.Add(conditionsGrid);
            return conditionsPanel;
        }

        private void AddConditionRow(Grid grid, int row, string label, bool defaultChecked)
        {
            grid.RowDefinitions.Add(new RowDefinition());

            var checkbox = new CheckBox
            {
                Content = label,
                IsChecked = defaultChecked,
                Margin = new Thickness(0, 5, 0, 0)
            };
            Grid.SetRow(checkbox, row);
            grid.Children.Add(checkbox);

            conditions[label] = checkbox;
            checkbox.Checked += (s, e) => UpdateConditions();
            checkbox.Unchecked += (s, e) => UpdateConditions();
        }

        private void AddAsymptoteInput(Grid grid, int row, string label, out TextBox textBox)
        {
            var textBlock = new TextBlock
            {
                Text = label,
                Margin = new Thickness(0, 5, 0, 0)
            };
            Grid.SetRow(textBlock, row);
            grid.Children.Add(textBlock);

            textBox = new TextBox
            {
                Width = 50,
                Margin = new Thickness(0, 5, 0, 0)
            };
            Grid.SetRow(textBox, row);
            Grid.SetColumn(textBox, 1);
            grid.Children.Add(textBox);
        }

        private Border CreateGraphBorder()
        {
            return new Border
            {
                BorderBrush = Brushes.Black,
                BorderThickness = new Thickness(2),
                Margin = new Thickness(GraphDrawingUtils.MARGIN)
            };
        }

        private void SetupGraphCanvas(Border border)
        {
            graphCanvas = new Canvas
            {
                Background = Brushes.White,
                ClipToBounds = true
            };
            border.Child = graphCanvas;

            connectionLine = new Polyline
            {
                Stroke = GraphSettings.Styles.FunctionColor,
                StrokeThickness = 2,
                StrokeLineJoin = PenLineJoin.Round
            };
            graphCanvas.Children.Add(connectionLine);

            graphCanvas.Loaded += (s, e) => GraphDrawingUtils.DrawCoordinateSystem(graphCanvas, connectionLine, points);
            graphCanvas.MouseLeftButtonDown += Canvas_MouseLeftButtonDown;
            graphCanvas.MouseMove += (s, e) =>
            {
                var point = e.GetPosition(graphCanvas);
                if (currentFit != null)
                {
                    var graphPoint = GraphDrawingUtils.ConvertToGraphCoordinates(graphCanvas, point);
                    toolTipManager.UpdateTooltip(graphPoint, point);
                }
            };
        }

        private void UpdateConditions()
        {
            var activeConditions = conditions
                .Where(c => c.Value.IsChecked == true)
                .Select(c => c.Key)
                .ToList();

            toolTipManager.ClearConditions();
            foreach (var condition in activeConditions)
            {
                toolTipManager.AddCondition(condition, $"Function is {condition.ToLower()}", true);
            }

            RedrawFunction();
        }

        private void RedrawFunction()
        {
            if (currentFit == null) return;

            if (functionPath != null)
                graphCanvas.Children.Remove(functionPath);

            double minX = -graphCanvas.ActualWidth / (2 * GraphDrawingUtils.GRID_SIZE);
            double maxX = graphCanvas.ActualWidth / (2 * GraphDrawingUtils.GRID_SIZE);

            Func<double, double> function = CreateFunctionFromFit(currentFit);
            var points = FunctionRenderer.GenerateContinuousPoints(graphCanvas, function, minX, maxX);
            functionPath = FunctionRenderer.CreateBezierCurve(points, graphCanvas);

            if (functionPath != null)
                graphCanvas.Children.Add(functionPath);
        }

        private Func<double, double> CreateFunctionFromFit(GraphUtils.FunctionFit fit)
        {
            return x =>
            {
                try
                {
                    // Basic function evaluation - expand this based on your needs
                    switch (functionType.SelectedItem as string)
                    {
                        case "Logarithmic":
                            return Math.Log(x);
                        case "Exponential":
                            return Math.Exp(x);
                        case "Trigonometric":
                            return Math.Sin(x);
                        default:
                            return x; // Linear by default
                    }
                }
                catch
                {
                    return double.NaN;
                }
            };
        }

        private void AddInfinityPoint_Click(object sender, RoutedEventArgs e)
        {
            var dialog = CreateInfinityPointDialog();
            dialog.ShowDialog();
        }

        private Window CreateInfinityPointDialog()
        {
            var dialog = new Window
            {
                Title = "Add Infinity Point",
                Width = 300,
                Height = 200,
                WindowStartupLocation = WindowStartupLocation.CenterOwner,
                Owner = this,
                Background = GraphSettings.Styles.MainGridColor
            };

            var panel = new StackPanel { Margin = new Thickness(10) };

            var (xInput, yInput) = CreateInfinityPointInputs();
            var directionCombo = CreateDirectionComboBox();
            var addButton = CreateAddInfinityPointButton(dialog, xInput, yInput, directionCombo);

            AddControlsToInfinityPointPanel(panel, xInput, yInput, directionCombo, addButton);

            dialog.Content = panel;
            return dialog;
        }

        private (TextBox xInput, TextBox yInput) CreateInfinityPointInputs()
        {
            var xInput = new TextBox { Margin = new Thickness(5) };
            var yInput = new TextBox { Margin = new Thickness(5) };
            return (xInput, yInput);
        }

        private ComboBox CreateDirectionComboBox()
        {
            var directionCombo = new ComboBox { Margin = new Thickness(5) };
            directionCombo.Items.Add("→ ∞");
            directionCombo.Items.Add("→ -∞");
            directionCombo.SelectedIndex = 0;
            return directionCombo;
        }

        private Button CreateAddInfinityPointButton(Window dialog, TextBox xInput, TextBox yInput, ComboBox directionCombo)
        {
            var addButton = new Button
            {
                Content = "Add Point",
                Margin = new Thickness(5),
                Background = GraphSettings.Styles.FunctionColor,
                Foreground = Brushes.White
            };

            addButton.Click += (s, e) =>
            {
                if (double.TryParse(xInput.Text, out double x) && double.TryParse(yInput.Text, out double y))
                {
                    infinityPoints.Add(new Point(x, y));
                    GraphDrawingUtils.DrawInfinityPoint(graphCanvas, new Point(x, y), directionCombo.SelectedIndex == 0);
                    dialog.Close();
                }
            };

            return addButton;
        }

        private void AddControlsToInfinityPointPanel(StackPanel panel, TextBox xInput, TextBox yInput, ComboBox directionCombo, Button addButton)
        {
            panel.Children.Add(new TextBlock { Text = "X value:", Margin = new Thickness(5) });
            panel.Children.Add(xInput);
            panel.Children.Add(new TextBlock { Text = "Y value:", Margin = new Thickness(5) });
            panel.Children.Add(yInput);
            panel.Children.Add(new TextBlock { Text = "Direction:", Margin = new Thickness(5) });
            panel.Children.Add(directionCombo);
            panel.Children.Add(addButton);
        }

        private void Canvas_MouseLeftButtonDown(object sender, MouseButtonEventArgs e)
        {
            var screenPoint = e.GetPosition(graphCanvas);
            var graphPoint = GraphDrawingUtils.ConvertToGraphCoordinates(graphCanvas, screenPoint);

            if (GraphDrawingUtils.IsValidNewPoint(points, graphPoint))
            {
                points.Add(graphPoint);
                GraphDrawingUtils.DrawPoint(graphCanvas, graphPoint);
                GraphDrawingUtils.UpdateConnectionLine(graphCanvas, connectionLine, points);
            }
            else
            {
                MessageBox.Show("Points must have different X coordinates.", "Invalid Point");
            }
        }

        private void GenerateFunction_Click(object sender, RoutedEventArgs e)
        {
            if (points.Count < 2)
            {
                MessageBox.Show("Please plot at least 2 points.");
                return;
            }

            var fits = new List<GraphUtils.FunctionFit>();

            switch (functionType.SelectedItem as string)
            {
                case "Logarithmic":
                    fits.Add(FunctionFitter.TryLogarithmicFit(points));
                    break;
                case "Exponential":
                    fits.Add(FunctionFitter.TryExponentialFit(points));
                    break;
                case "Trigonometric":
                    fits.Add(FunctionFitter.TryTrigonometricFit(points, true)); // Sine
                    fits.Add(FunctionFitter.TryTrigonometricFit(points, false)); // Cosine
                    break;
                default: // Polynomial
                    fits.Add(FunctionFitter.TryPolynomialFit(points, 1));
                    fits.Add(FunctionFitter.TryPolynomialFit(points, 2));
                    fits.Add(FunctionFitter.TryPolynomialFit(points, 3));
                    break;
            }

            currentFit = fits
                .Where(f => !string.IsNullOrEmpty(f.Expression))
                .OrderBy(f => f.Error)
                .FirstOrDefault();

            if (currentFit != null)
            {
                RedrawFunction();
                ShowBestFit(fits);
            }
            else
            {
                MessageBox.Show("Could not find a suitable function fit.", "Error");
            }
        }

        private void ShowBestFit(List<GraphUtils.FunctionFit> fits)
        {
            var bestFit = fits
                .Where(f => !string.IsNullOrEmpty(f.Expression))
                .OrderBy(f => f.Error)
                .FirstOrDefault();

            if (bestFit != null)
            {
                string function = BuildFunctionString(bestFit.Expression);
                var resultWindow = new Window
                {
                    Title = "Generated Function",
                    Width = 400,
                    Height = 300,
                    WindowStartupLocation = WindowStartupLocation.CenterOwner,
                    Owner = this,
                    Background = GraphSettings.Styles.MainGridColor
                };

                var scrollViewer = new ScrollViewer();
                var textBlock = new TextBlock
                {
                    Text = function,
                    Margin = new Thickness(10),
                    TextWrapping = TextWrapping.Wrap
                };
                scrollViewer.Content = textBlock;
                resultWindow.Content = scrollViewer;

                resultWindow.ShowDialog();
            }
            else
            {
                MessageBox.Show("Could not find a suitable function fit.", "Error");
            }
        }

        private string BuildFunctionString(string expression)
        {
            var builder = new System.Text.StringBuilder();
            builder.AppendLine($"Function Expression:");
            builder.AppendLine($"f(x) = {expression}");
            builder.AppendLine();

            // Add conditions information
            builder.AppendLine("Function Properties:");
            foreach (var condition in conditions)
            {
                if (condition.Value.IsChecked == true)
                {
                    builder.AppendLine($"• {condition.Key}");
                }
            }
            builder.AppendLine();

            // Add asymptote information if specified
            builder.AppendLine("Asymptotes:");
            if (!string.IsNullOrEmpty(xMinAsymptote.Text))
                builder.AppendLine($"• As x → -∞, f(x) → {xMinAsymptote.Text}");
            if (!string.IsNullOrEmpty(xMaxAsymptote.Text))
                builder.AppendLine($"• As x → ∞, f(x) → {xMaxAsymptote.Text}");
            if (!string.IsNullOrEmpty(yMinAsymptote.Text))
                builder.AppendLine($"• Vertical asymptote: x = {yMinAsymptote.Text}");
            if (!string.IsNullOrEmpty(yMaxAsymptote.Text))
                builder.AppendLine($"• Vertical asymptote: x = {yMaxAsymptote.Text}");
            builder.AppendLine();

            // Add infinity points information
            if (infinityPoints.Any())
            {
                builder.AppendLine("Infinity Points:");
                foreach (var point in infinityPoints)
                {
                    builder.AppendLine($"• Point at ({point.X:F2}, {point.Y:F2})");
                }
                builder.AppendLine();
            }

            // Add error information
            builder.AppendLine($"Fit Error: {currentFit?.Error:F4}");

            return builder.ToString();
        }

        private void UpdateFunctionDisplay()
        {
            if (currentFit == null) return;

            // Clear existing function visualization
            graphCanvas.Children.Clear();
            graphCanvas.Children.Add(connectionLine);

            // Redraw coordinate system
            GraphDrawingUtils.DrawCoordinateSystem(graphCanvas, connectionLine, points);

            // Calculate visible area
            double minX = -graphCanvas.ActualWidth / (2 * GraphDrawingUtils.GRID_SIZE);
            double maxX = graphCanvas.ActualWidth / (2 * GraphDrawingUtils.GRID_SIZE);

            // Create continuous function points
            var functionPoints = new List<Point>();
            double step = 1.0 / GraphSettings.POINTS_PER_UNIT;

            for (double x = minX * GraphSettings.EXTENSION_FACTOR;
                 x <= maxX * GraphSettings.EXTENSION_FACTOR;
                 x += step)
            {
                try
                {
                    double y = EvaluateFunction(x);
                    if (!double.IsInfinity(y) && !double.IsNaN(y))
                    {
                        functionPoints.Add(new Point(x, y));
                    }
                }
                catch
                {
                    // Skip undefined points
                }
            }

            // Create and add the smooth curve
            var curve = FunctionRenderer.CreateBezierCurve(functionPoints, graphCanvas);
            if (curve != null)
            {
                graphCanvas.Children.Add(curve);
            }

            // Redraw points on top
            foreach (var point in points)
            {
                GraphDrawingUtils.DrawPoint(graphCanvas, point);
            }
        }

        private double EvaluateFunction(double x)
        {
            // This is a simplified implementation
            // You would need to add proper expression parsing and evaluation
            switch (functionType.SelectedItem as string)
            {
                case "Logarithmic":
                    return Math.Log(x);
                case "Exponential":
                    return Math.Exp(x);
                case "Trigonometric":
                    return Math.Sin(x);
                default: // Polynomial
                    return x; // Linear by default
            }
        }
    }
}