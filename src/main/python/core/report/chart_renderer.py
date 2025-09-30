"""
Chart Renderer - Data Visualization for PDF Reports

This module provides chart generation capabilities for visualizing
assessment results in PDF reports.

Design Philosophy:
Simple, clear visualizations that communicate insights effectively.
No fancy 3D effects or unnecessary decoration - just clean, readable charts.
"""

from typing import Dict, List, Optional, Tuple
from enum import Enum
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Circle
from reportlab.graphics.charts.barcharts import HorizontalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.legends import Legend
from reportlab.graphics import renderPDF


class ChartType(Enum):
    """Supported chart types."""
    HORIZONTAL_BAR = "horizontal_bar"
    PIE = "pie"
    RADAR = "radar"
    SCORE_BADGE = "score_badge"


class ChartRenderer:
    """
    Renders charts for PDF reports.

    Following the principle of simplicity - provides clean, professional
    charts without unnecessary complexity.
    """

    def __init__(self, width: float = 150 * mm, height: float = 100 * mm):
        """
        Initialize chart renderer.

        Args:
            width: Default chart width in points
            height: Default chart height in points
        """
        self.width = width
        self.height = height

        # Professional color palette
        self.colors = [
            colors.Color(0.2, 0.4, 0.6),  # Primary blue
            colors.Color(0.3, 0.6, 0.8),  # Light blue
            colors.Color(0.9, 0.5, 0.2),  # Orange
            colors.Color(0.2, 0.7, 0.4),  # Green
            colors.Color(0.7, 0.3, 0.5),  # Purple
            colors.Color(0.9, 0.7, 0.2),  # Yellow
        ]

    def render_horizontal_bar_chart(
        self,
        data: Dict[str, float],
        title: str = "",
        max_value: float = 100.0,
        show_values: bool = True
    ) -> Drawing:
        """
        Render horizontal bar chart for strength scores.

        Args:
            data: Dictionary mapping labels to values
            title: Chart title
            max_value: Maximum value for scaling
            show_values: Whether to show value labels

        Returns:
            ReportLab Drawing object
        """
        drawing = Drawing(self.width, self.height)

        # Create chart
        chart = HorizontalBarChart()
        chart.x = 50
        chart.y = 30
        chart.width = self.width - 100
        chart.height = self.height - 60

        # Data preparation
        labels = list(data.keys())
        values = [[data[label]] for label in labels]
        chart.data = values

        # Styling
        chart.categoryAxis.categoryNames = labels
        chart.categoryAxis.labels.fontSize = 9
        chart.categoryAxis.labels.dx = -5

        chart.valueAxis.valueMin = 0
        chart.valueAxis.valueMax = max_value
        chart.valueAxis.valueStep = max_value / 5
        chart.valueAxis.labels.fontSize = 9

        # Bar colors - gradient from primary to secondary
        for i in range(len(values)):
            chart.bars[i].fillColor = self.colors[i % len(self.colors)]

        # Show values on bars if requested
        if show_values:
            chart.barLabels.visible = 1
            chart.barLabels.fontSize = 8
            chart.barLabels.fillColor = colors.white
            chart.barLabels.nudge = 5

        drawing.add(chart)

        # Add title if provided
        if title:
            title_string = String(
                self.width / 2,
                self.height - 20,
                title,
                fontSize=12,
                fillColor=colors.Color(0.2, 0.2, 0.2),
                textAnchor='middle'
            )
            drawing.add(title_string)

        return drawing

    def render_domain_distribution_chart(
        self,
        domain_scores: Dict[str, float],
        title: str = "優勢領域分佈"
    ) -> Drawing:
        """
        Render pie chart for domain distribution.

        Args:
            domain_scores: Dictionary mapping domain names to percentages
            title: Chart title

        Returns:
            ReportLab Drawing object
        """
        drawing = Drawing(self.width, self.height)

        # Create pie chart
        pie = Pie()
        pie.x = self.width / 2 - 60
        pie.y = self.height / 2 - 60
        pie.width = 120
        pie.height = 120

        # Data
        pie.data = list(domain_scores.values())
        pie.labels = list(domain_scores.keys())

        # Styling
        pie.slices.strokeWidth = 1
        pie.slices.strokeColor = colors.white
        for i, color in enumerate(self.colors[:len(domain_scores)]):
            pie.slices[i].fillColor = color

        # Label styling
        pie.slices.labelRadius = 1.25
        pie.slices.fontName = 'Helvetica'
        pie.slices.fontSize = 9

        drawing.add(pie)

        # Add title
        title_string = String(
            self.width / 2,
            self.height - 20,
            title,
            fontSize=12,
            fillColor=colors.Color(0.2, 0.2, 0.2),
            textAnchor='middle'
        )
        drawing.add(title_string)

        # Add legend
        legend = Legend()
        legend.x = 10
        legend.y = self.height / 2 - 40
        legend.dx = 8
        legend.dy = 8
        legend.fontName = 'Helvetica'
        legend.fontSize = 8
        legend.columnMaximum = 10
        legend.colorNamePairs = [
            (pie.slices[i].fillColor, pie.labels[i])
            for i in range(len(pie.data))
        ]

        drawing.add(legend)

        return drawing

    def render_score_badge(
        self,
        score: float,
        label: str,
        max_score: float = 100.0,
        size: float = 80
    ) -> Drawing:
        """
        Render circular score badge for key metrics.

        Args:
            score: Numeric score
            label: Label text
            max_score: Maximum possible score
            size: Badge diameter

        Returns:
            ReportLab Drawing object
        """
        drawing = Drawing(size, size + 20)

        # Calculate percentage and color
        percentage = (score / max_score) * 100
        if percentage >= 75:
            color = colors.Color(0.2, 0.7, 0.4)  # Green
        elif percentage >= 50:
            color = colors.Color(0.9, 0.7, 0.2)  # Yellow
        else:
            color = colors.Color(0.9, 0.5, 0.2)  # Orange

        # Outer circle
        outer_circle = Circle(
            size / 2,
            size / 2 + 10,
            size / 2,
            fillColor=color,
            strokeColor=colors.white,
            strokeWidth=2
        )
        drawing.add(outer_circle)

        # Score text
        score_text = String(
            size / 2,
            size / 2 + 15,
            f"{score:.1f}",
            fontSize=16,
            fillColor=colors.white,
            textAnchor='middle',
            fontName='Helvetica-Bold'
        )
        drawing.add(score_text)

        # Label text
        label_text = String(
            size / 2,
            5,
            label,
            fontSize=9,
            fillColor=colors.Color(0.2, 0.2, 0.2),
            textAnchor='middle'
        )
        drawing.add(label_text)

        return drawing

    def render_strength_comparison(
        self,
        strengths: Dict[str, float],
        title: str = "優勢分數比較",
        benchmark: Optional[float] = None
    ) -> Drawing:
        """
        Render comparison chart with optional benchmark line.

        Args:
            strengths: Dictionary of strength names to scores
            title: Chart title
            benchmark: Optional benchmark value to show as reference line

        Returns:
            ReportLab Drawing object
        """
        drawing = self.render_horizontal_bar_chart(
            data=strengths,
            title=title,
            max_value=100.0,
            show_values=True
        )

        # Add benchmark line if provided
        if benchmark is not None:
            chart_area = drawing.contents[0]
            x_start = chart_area.x
            x_end = chart_area.x + chart_area.width
            y_pos = chart_area.y + (benchmark / 100.0) * chart_area.height

            benchmark_line = Line(
                x_start, y_pos, x_end, y_pos,
                strokeColor=colors.red,
                strokeWidth=2,
                strokeDashArray=[5, 2]
            )
            drawing.add(benchmark_line)

            # Add benchmark label
            label = String(
                x_end + 5,
                y_pos - 3,
                f"基準: {benchmark}",
                fontSize=8,
                fillColor=colors.red
            )
            drawing.add(label)

        return drawing

    def render_percentile_gauge(
        self,
        percentile: float,
        dimension_name: str,
        width: float = 100,
        height: float = 40
    ) -> Drawing:
        """
        Render percentile gauge showing ranking.

        Args:
            percentile: Percentile score (0-100)
            dimension_name: Name of the dimension
            width: Gauge width
            height: Gauge height

        Returns:
            ReportLab Drawing object
        """
        drawing = Drawing(width, height + 15)

        # Background bar
        bg_rect = Rect(
            0, height / 2, width, 10,
            fillColor=colors.Color(0.9, 0.9, 0.9),
            strokeColor=colors.grey,
            strokeWidth=0.5
        )
        drawing.add(bg_rect)

        # Filled bar based on percentile
        fill_width = (percentile / 100.0) * width
        if percentile >= 75:
            fill_color = colors.Color(0.2, 0.7, 0.4)  # Green
        elif percentile >= 50:
            fill_color = colors.Color(0.9, 0.7, 0.2)  # Yellow
        elif percentile >= 25:
            fill_color = colors.Color(0.9, 0.5, 0.2)  # Orange
        else:
            fill_color = colors.Color(0.8, 0.3, 0.3)  # Red

        fill_rect = Rect(
            0, height / 2, fill_width, 10,
            fillColor=fill_color,
            strokeColor=None
        )
        drawing.add(fill_rect)

        # Percentile marker
        marker = Circle(
            fill_width, height / 2 + 5, 3,
            fillColor=colors.white,
            strokeColor=fill_color,
            strokeWidth=2
        )
        drawing.add(marker)

        # Label
        label = String(
            0, 0,
            f"{dimension_name}: {percentile:.0f}%",
            fontSize=9,
            fillColor=colors.Color(0.2, 0.2, 0.2)
        )
        drawing.add(label)

        return drawing

    def save_to_bytes(self, drawing: Drawing) -> BytesIO:
        """
        Convert drawing to bytes for embedding in PDF.

        Args:
            drawing: ReportLab Drawing object

        Returns:
            BytesIO buffer containing rendered chart
        """
        buffer = BytesIO()
        renderPDF.drawToFile(drawing, buffer)
        buffer.seek(0)
        return buffer