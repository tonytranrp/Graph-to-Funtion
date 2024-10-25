using System;
using System.Collections.Generic;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Media;

namespace WpfApp1.Utils
{
    public class ToolTipManager
    {
        private readonly Canvas graphCanvas;
        private readonly TextBlock toolTipText;
        private readonly Border toolTipBorder;
        private readonly List<GraphSettings.FunctionCondition> conditions;

        public ToolTipManager(Canvas graphCanvas)
        {
            this.graphCanvas = graphCanvas;
            this.conditions = new List<GraphSettings.FunctionCondition>();

            toolTipText = new TextBlock
            {
                Padding = new Thickness(5),
                Background = GraphSettings.Styles.ToolTipBackgroundColor
            };

            toolTipBorder = new Border
            {
                Child = toolTipText,
                BorderBrush = Brushes.Gray,
                BorderThickness = new Thickness(1),
                Background = GraphSettings.Styles.ToolTipBackgroundColor,
                Visibility = Visibility.Collapsed
            };

            Canvas.SetZIndex(toolTipBorder, 1000);
            graphCanvas.Children.Add(toolTipBorder);
        }

        public void AddCondition(string name, string description, bool isEnabled = true)
        {
            conditions.Add(new GraphSettings.FunctionCondition
            {
                Name = name,
                Description = description,
                IsEnabled = isEnabled
            });
        }

        public void ClearConditions()
        {
            conditions.Clear();
        }

        public void UpdateTooltip(Point graphPoint, Point screenPoint)
        {
            var sb = new System.Text.StringBuilder();
            sb.AppendLine($"Coordinates: ({graphPoint.X:F2}, {graphPoint.Y:F2})");

            if (conditions.Count > 0)
            {
                sb.AppendLine("\nActive Conditions:");
                foreach (var condition in conditions.Where(c => c.IsEnabled))
                {
                    sb.AppendLine($"• {condition.Name}: {condition.Description}");
                }
            }

            toolTipText.Text = sb.ToString().TrimEnd();

            Canvas.SetLeft(toolTipBorder, screenPoint.X + 10);
            Canvas.SetTop(toolTipBorder, screenPoint.Y + 10);
            toolTipBorder.Visibility = Visibility.Visible;
        }

        public void Hide()
        {
            toolTipBorder.Visibility = Visibility.Collapsed;
        }
    }
}