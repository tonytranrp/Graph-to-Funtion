using System;
using System.Collections.Generic;
using System.Linq;
using System.Windows;

namespace WpfApp1.Utils
{
    public static class GraphUtils
    {
        public class FunctionFit
        {
            public string Expression { get; set; }
            public double Error { get; set; }
        }

        public static double[] SolveLinearSystem(double[,] matrix, double[] vector)
        {
            int n = vector.Length;
            double[] result = new double[n];

            // Gaussian elimination
            for (int i = 0; i < n; i++)
            {
                // Find pivot
                int maxRow = i;
                for (int k = i + 1; k < n; k++)
                {
                    if (Math.Abs(matrix[k, i]) > Math.Abs(matrix[maxRow, i]))
                    {
                        maxRow = k;
                    }
                }

                // Swap maximum row with current row
                for (int k = i; k < n; k++)
                {
                    double tmp = matrix[maxRow, k];
                    matrix[maxRow, k] = matrix[i, k];
                    matrix[i, k] = tmp;
                }
                double tmp2 = vector[maxRow];
                vector[maxRow] = vector[i];
                vector[i] = tmp2;

                // Make all rows below this one 0 in current column
                for (int k = i + 1; k < n; k++)
                {
                    double c = -matrix[k, i] / matrix[i, i];
                    for (int j = i; j < n; j++)
                    {
                        if (i == j)
                            matrix[k, j] = 0;
                        else
                            matrix[k, j] += c * matrix[i, j];
                    }
                    vector[k] += c * vector[i];
                }
            }

            // Back substitution
            for (int i = n - 1; i >= 0; i--)
            {
                double sum = 0.0;
                for (int j = i + 1; j < n; j++)
                {
                    sum += matrix[i, j] * result[j];
                }
                result[i] = (vector[i] - sum) / matrix[i, i];
            }

            return result;
        }
    }

    public static class FunctionFitter
    {
        public static GraphUtils.FunctionFit TryPolynomialFit(List<Point> points, int degree)
        {
            try
            {
                int n = points.Count;
                var matrix = new double[degree + 1, degree + 1];
                var vector = new double[degree + 1];

                // Build the normal equations matrix
                for (int i = 0; i <= degree; i++)
                {
                    for (int j = 0; j <= degree; j++)
                    {
                        double sum = 0;
                        for (int k = 0; k < n; k++)
                        {
                            sum += Math.Pow(points[k].X, i + j);
                        }
                        matrix[i, j] = sum;
                    }

                    double vectorSum = 0;
                    for (int k = 0; k < n; k++)
                    {
                        vectorSum += points[k].Y * Math.Pow(points[k].X, i);
                    }
                    vector[i] = vectorSum;
                }

                // Solve using Gaussian elimination
                var coefficients = GraphUtils.SolveLinearSystem(matrix, vector);
                if (coefficients == null) return new GraphUtils.FunctionFit { Error = double.MaxValue };

                // Calculate error
                double error = 0;
                for (int i = 0; i < n; i++)
                {
                    double y = 0;
                    for (int j = 0; j <= degree; j++)
                    {
                        y += coefficients[j] * Math.Pow(points[i].X, j);
                    }
                    error += Math.Pow(y - points[i].Y, 2);
                }

                // Generate function expression
                string expression = "";
                for (int i = degree; i >= 0; i--)
                {
                    if (Math.Abs(coefficients[i]) < 0.0001) continue;

                    string term = "";
                    if (i > 0)
                    {
                        term = i == 1 ? "x" : $"x^{i}";
                        term = $"{coefficients[i]:F2}{term}";
                    }
                    else
                    {
                        term = $"{coefficients[i]:F2}";
                    }

                    if (expression != "" && coefficients[i] > 0)
                        expression += " + ";
                    expression += term;
                }

                return new GraphUtils.FunctionFit { Expression = expression, Error = error };
            }
            catch
            {
                return new GraphUtils.FunctionFit { Error = double.MaxValue };
            }
        }

        public static GraphUtils.FunctionFit TryExponentialFit(List<Point> points)
        {
            try
            {
                var validPoints = points.Where(p => p.Y > 0).ToList();
                if (validPoints.Count < 2) return new GraphUtils.FunctionFit { Error = double.MaxValue };

                double sumX = 0, sumY = 0, sumXY = 0, sumXX = 0;
                foreach (var p in validPoints)
                {
                    double lnY = Math.Log(p.Y);
                    sumX += p.X;
                    sumY += lnY;
                    sumXY += p.X * lnY;
                    sumXX += p.X * p.X;
                }

                int n = validPoints.Count;
                double b = (n * sumXY - sumX * sumY) / (n * sumXX - sumX * sumX);
                double lnA = (sumY - b * sumX) / n;
                double a = Math.Exp(lnA);

                // Calculate error
                double error = 0;
                foreach (var p in points)
                {
                    double y = a * Math.Exp(b * p.X);
                    error += Math.Pow(y - p.Y, 2);
                }

                return new GraphUtils.FunctionFit
                {
                    Expression = $"{a:F2}e^({b:F2}x)",
                    Error = error
                };
            }
            catch
            {
                return new GraphUtils.FunctionFit { Error = double.MaxValue };
            }
        }

        public static GraphUtils.FunctionFit TryLogarithmicFit(List<Point> points)
        {
            try
            {
                var validPoints = points.Where(p => p.X > 0).ToList();
                if (validPoints.Count < 2) return new GraphUtils.FunctionFit { Error = double.MaxValue };

                double sumLnX = 0, sumY = 0, sumYLnX = 0, sumLnXLnX = 0;
                foreach (var p in validPoints)
                {
                    double lnX = Math.Log(p.X);
                    sumLnX += lnX;
                    sumY += p.Y;
                    sumYLnX += p.Y * lnX;
                    sumLnXLnX += lnX * lnX;
                }

                int n = validPoints.Count;
                double a = (n * sumYLnX - sumLnX * sumY) / (n * sumLnXLnX - sumLnX * sumLnX);
                double b = (sumY - a * sumLnX) / n;

                // Calculate error
                double error = 0;
                foreach (var p in validPoints)
                {
                    double y = a * Math.Log(p.X) + b;
                    error += Math.Pow(y - p.Y, 2);
                }

                return new GraphUtils.FunctionFit
                {
                    Expression = $"{a:F2}ln(x) + {b:F2}",
                    Error = error
                };
            }
            catch
            {
                return new GraphUtils.FunctionFit { Error = double.MaxValue };
            }
        }

        public static GraphUtils.FunctionFit TryTrigonometricFit(List<Point> points, bool useSine = true)
        {
            try
            {
                double maxY = points.Max(p => p.Y);
                double minY = points.Min(p => p.Y);
                double amplitude = (maxY - minY) / 2;
                double offset = (maxY + minY) / 2;

                double bestFreq = 1.0;
                double bestPhase = 0.0;
                double minError = double.MaxValue;

                for (double freq = 0.1; freq <= 5.0; freq += 0.1)
                {
                    for (double phase = 0; phase <= Math.PI * 2; phase += Math.PI / 4)
                    {
                        double error = 0;
                        foreach (var p in points)
                        {
                            double y = amplitude * (useSine ?
                                Math.Sin(freq * p.X + phase) :
                                Math.Cos(freq * p.X + phase)) + offset;
                            error += Math.Pow(y - p.Y, 2);
                        }

                        if (error < minError)
                        {
                            minError = error;
                            bestFreq = freq;
                            bestPhase = phase;
                        }
                    }
                }

                string funcName = useSine ? "sin" : "cos";
                return new GraphUtils.FunctionFit
                {
                    Expression = $"{amplitude:F2}{funcName}({bestFreq:F2}x + {bestPhase:F2}) + {offset:F2}",
                    Error = minError
                };
            }
            catch
            {
                return new GraphUtils.FunctionFit { Error = double.MaxValue };
            }
        }
    }
}