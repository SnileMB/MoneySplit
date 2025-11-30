"""
PDF Report Generator for MoneySplit.
Creates professional PDF reports for projects, summaries, and forecasts.
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
    PageBreak,
)
from reportlab.platypus import Image as RLImage
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from datetime import datetime
import os


def generate_project_pdf(
    record_data, people_data, filepath="reports/project_report.pdf"
):
    """Generate PDF report for a single project/record."""
    os.makedirs("reports", exist_ok=True)

    doc = SimpleDocTemplate(filepath, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        fontSize=24,
        textColor=colors.HexColor("#2c3e50"),
        spaceAfter=30,
        alignment=TA_CENTER,
    )

    heading_style = ParagraphStyle(
        "CustomHeading",
        parent=styles["Heading2"],
        fontSize=16,
        textColor=colors.HexColor("#34495e"),
        spaceAfter=12,
    )

    # Title
    story.append(Paragraph("🤑 MoneySplit Project Report", title_style))
    story.append(Spacer(1, 0.2 * inch))

    # Project Info
    story.append(Paragraph("Project Information", heading_style))

    project_info = [
        ["Record ID:", str(record_data[0])],
        ["Date:", record_data[8]],
        ["Country:", record_data[1]],
        ["Tax Type:", record_data[2]],
        ["Number of People:", str(record_data[9])],
    ]

    project_table = Table(project_info, colWidths=[2 * inch, 4 * inch])
    project_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#ecf0f1")),
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 1, colors.grey),
            ]
        )
    )
    story.append(project_table)
    story.append(Spacer(1, 0.3 * inch))

    # Financial Summary
    story.append(Paragraph("Financial Summary", heading_style))

    financial_data = [
        ["Item", "Amount"],
        ["Revenue", f"${record_data[3]:,.2f}"],
        ["Total Costs", f"${record_data[4]:,.2f}"],
        ["Group Income", f"${record_data[10]:,.2f}"],
        ["Tax Amount", f"${record_data[5]:,.2f}"],
        ["Net Income (Group)", f"${record_data[6]:,.2f}"],
        ["Net Income (Per Person)", f"${record_data[7]:,.2f}"],
    ]

    financial_table = Table(financial_data, colWidths=[3 * inch, 3 * inch])
    financial_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#3498db")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("ALIGN", (1, 1), (1, -1), "RIGHT"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                ("GRID", (0, 0), (-1, -1), 1, colors.grey),
                ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#2ecc71")),
                ("TEXTCOLOR", (0, -1), (-1, -1), colors.whitesmoke),
                ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
            ]
        )
    )
    story.append(financial_table)
    story.append(Spacer(1, 0.3 * inch))

    # Team Breakdown
    story.append(Paragraph("Team Breakdown", heading_style))

    team_data = [["Name", "Work Share", "Gross Income", "Tax Paid", "Net Income"]]
    for person in people_data:
        team_data.append(
            [
                person[1],  # name
                f"{person[2]*100:.1f}%",  # work_share
                f"${person[3]:,.2f}",  # gross_income
                f"${person[4]:,.2f}",  # tax_paid
                f"${person[5]:,.2f}",  # net_income
            ]
        )

    team_table = Table(
        team_data,
        colWidths=[1.5 * inch, 1.2 * inch, 1.3 * inch, 1.3 * inch, 1.3 * inch],
    )
    team_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#3498db")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (0, -1), "LEFT"),
                ("ALIGN", (1, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("GRID", (0, 0), (-1, -1), 1, colors.grey),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ]
        )
    )
    story.append(team_table)

    # Footer
    story.append(Spacer(1, 0.5 * inch))
    footer_text = (
        f"Generated by MoneySplit on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    footer_style = ParagraphStyle(
        "Footer",
        parent=styles["Normal"],
        fontSize=8,
        textColor=colors.grey,
        alignment=TA_CENTER,
    )
    story.append(Paragraph(footer_text, footer_style))

    # Build PDF
    doc.build(story)
    return filepath


def generate_summary_pdf(records, stats, filepath="reports/summary_report.pdf"):
    """Generate PDF summary report for all records."""
    os.makedirs("reports", exist_ok=True)

    doc = SimpleDocTemplate(filepath, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        fontSize=24,
        textColor=colors.HexColor("#2c3e50"),
        spaceAfter=30,
        alignment=TA_CENTER,
    )

    heading_style = ParagraphStyle(
        "CustomHeading",
        parent=styles["Heading2"],
        fontSize=16,
        textColor=colors.HexColor("#34495e"),
        spaceAfter=12,
    )

    # Title
    story.append(Paragraph("🤑 MoneySplit Summary Report", title_style))
    story.append(Spacer(1, 0.2 * inch))

    # Overall Statistics
    story.append(Paragraph("Overall Statistics", heading_style))

    stats_data = [
        ["Metric", "Value"],
        ["Total Records", str(stats["total_records"])],
        ["Total Revenue", f"${stats['total_revenue']:,.2f}"],
        ["Total Costs", f"${stats['total_costs']:,.2f}"],
        ["Total Tax Paid", f"${stats['total_tax']:,.2f}"],
        ["Total Net Income", f"${stats['total_net_income']:,.2f}"],
        ["Average Tax Rate", f"{stats['average_tax_rate']:.2f}%"],
        ["Unique People", str(stats["unique_people"])],
    ]

    stats_table = Table(stats_data, colWidths=[3 * inch, 3 * inch])
    stats_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#3498db")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (0, -1), "LEFT"),
                ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 1, colors.grey),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.beige, colors.white]),
            ]
        )
    )
    story.append(stats_table)
    story.append(Spacer(1, 0.4 * inch))

    # Recent Records
    story.append(Paragraph(f"Recent Records (Last {len(records)})", heading_style))

    records_data = [
        ["ID", "Date", "Country", "Tax Type", "Revenue", "Tax", "Net Income"]
    ]
    for r in records:
        records_data.append(
            [
                str(r[0]),
                r[8][:10],  # date only
                r[1],
                r[2],
                f"${r[3]:,.0f}",
                f"${r[5]:,.0f}",
                f"${r[6]:,.0f}",
            ]
        )

    records_table = Table(
        records_data,
        colWidths=[
            0.5 * inch,
            1 * inch,
            1 * inch,
            1.2 * inch,
            1.2 * inch,
            1 * inch,
            1.2 * inch,
        ],
    )
    records_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#3498db")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("GRID", (0, 0), (-1, -1), 1, colors.grey),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ]
        )
    )
    story.append(records_table)

    # Footer
    story.append(Spacer(1, 0.5 * inch))
    footer_text = (
        f"Generated by MoneySplit on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    footer_style = ParagraphStyle(
        "Footer",
        parent=styles["Normal"],
        fontSize=8,
        textColor=colors.grey,
        alignment=TA_CENTER,
    )
    story.append(Paragraph(footer_text, footer_style))

    # Build PDF
    doc.build(story)
    return filepath


def generate_forecast_pdf(forecast_data, filepath="reports/forecast_report.pdf"):
    """Generate PDF forecast report with predictions."""
    os.makedirs("reports", exist_ok=True)

    doc = SimpleDocTemplate(filepath, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        fontSize=24,
        textColor=colors.HexColor("#2c3e50"),
        spaceAfter=30,
        alignment=TA_CENTER,
    )

    heading_style = ParagraphStyle(
        "CustomHeading",
        parent=styles["Heading2"],
        fontSize=16,
        textColor=colors.HexColor("#34495e"),
        spaceAfter=12,
    )

    # Title
    story.append(Paragraph("🤑 MoneySplit Forecast Report", title_style))
    story.append(Spacer(1, 0.2 * inch))

    # Predictions
    story.append(Paragraph("Revenue Predictions (Next 3 Months)", heading_style))

    predictions_data = [["Month", "Predicted Revenue", "Confidence"]]
    for pred in forecast_data["predictions"]:
        predictions_data.append(
            [pred["month"], f"${pred['revenue']:,.2f}", pred["confidence"]]
        )

    pred_table = Table(predictions_data, colWidths=[2 * inch, 2.5 * inch, 2 * inch])
    pred_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#3498db")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 1, colors.grey),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.lightblue, colors.white]),
            ]
        )
    )
    story.append(pred_table)
    story.append(Spacer(1, 0.3 * inch))

    # Recommendations
    if "recommendations" in forecast_data:
        story.append(Paragraph("💡 Recommendations", heading_style))
        for rec in forecast_data["recommendations"]:
            story.append(Paragraph(f"• {rec}", styles["BodyText"]))
            story.append(Spacer(1, 0.1 * inch))

    # Footer
    story.append(Spacer(1, 0.5 * inch))
    footer_text = (
        f"Generated by MoneySplit on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    footer_style = ParagraphStyle(
        "Footer",
        parent=styles["Normal"],
        fontSize=8,
        textColor=colors.grey,
        alignment=TA_CENTER,
    )
    story.append(Paragraph(footer_text, footer_style))

    # Build PDF
    doc.build(story)
    return filepath
