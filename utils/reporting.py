"""
Reporting & Export Utility Module for InsightAI.
Generates multi-sheet formatted Excel workbooks, CSV files, and executive summaries using OpenPyXL and Pandas.
"""

import io
from typing import Dict, Any, Optional
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from utils.logger import logger

def export_to_csv(df: pd.DataFrame) -> bytes:
    """Exports DataFrame to raw CSV bytes for Streamlit downloading."""
    return df.to_csv(index=False).encode("utf-8")

def export_to_excel(
    df: pd.DataFrame,
    kpis: Dict[str, Any],
    category_df: Optional[pd.DataFrame] = None,
    rfm_df: Optional[pd.DataFrame] = None
) -> bytes:
    """
    Creates a styled multi-sheet Excel workbook:
    - Sheet 1: Executive Summary KPIs
    - Sheet 2: Cleaned Sales Data
    - Sheet 3: Category Breakdown
    - Sheet 4: Customer RFM Clusters
    """
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        # Sheet 1: Executive Summary
        kpi_rows = [
            {"Metric": "Total Sales Revenue", "Value": f"${kpis.get('total_revenue', 0):,.2f}"},
            {"Metric": "Total Net Profit", "Value": f"${kpis.get('total_profit', 0):,.2f}"},
            {"Metric": "Overall Profit Margin", "Value": f"{kpis.get('profit_margin', 0):.2f}%"},
            {"Metric": "Total Orders Placed", "Value": f"{kpis.get('total_orders', 0):,}"},
            {"Metric": "Total Unique Customers", "Value": f"{kpis.get('total_customers', 0):,}"},
            {"Metric": "Average Order Value (AOV)", "Value": f"${kpis.get('aov', 0):,.2f}"},
            {"Metric": "MoM Revenue Growth", "Value": f"{kpis.get('rev_growth_mom', 0):.2f}%"},
        ]
        summary_df = pd.DataFrame(kpi_rows)
        summary_df.to_excel(writer, sheet_name="Executive Summary", index=False)

        # Sheet 2: Data
        df.to_excel(writer, sheet_name="Sales Dataset", index=False)

        # Sheet 3: Category
        if category_df is not None and not category_df.empty:
            category_df.to_excel(writer, sheet_name="Category Performance", index=False)

        # Sheet 4: Customer Segments
        if rfm_df is not None and not rfm_df.empty:
            rfm_df.to_excel(writer, sheet_name="Customer RFM Clusters", index=False)

    # Apply openpyxl styling to Executive Summary
    buffer.seek(0)
    wb = openpyxl_style_workbook(buffer)
    
    out_buffer = io.BytesIO()
    wb.save(out_buffer)
    return out_buffer.getvalue()

def openpyxl_style_workbook(excel_buffer: io.BytesIO) -> Workbook:
    """Applies professional dark-header styling and column auto-fit using OpenPyXL."""
    wb = openpyxl_load_workbook(excel_buffer)
    
    header_fill = PatternFill(start_color="1F2937", end_color="1F2937", fill_type="solid")
    header_font = Font(name="Segoe UI", size=11, bold=True, color="F9FAFB")
    data_font = Font(name="Segoe UI", size=10, color="1F2937")
    thin_border = Border(
        left=Side(style='thin', color='E5E7EB'),
        right=Side(style='thin', color='E5E7EB'),
        top=Side(style='thin', color='E5E7EB'),
        bottom=Side(style='thin', color='E5E7EB')
    )

    for sheet in wb.worksheets:
        # Header formatting
        for cell in sheet[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center", vertical="center")

        # Data formatting & column width auto-adjust
        for row in sheet.iter_rows(min_row=2):
            for cell in row:
                cell.font = data_font
                cell.border = thin_border

        for col in sheet.columns:
            max_len = max(len(str(cell.value or '')) for cell in col)
            col_letter = col[0].column_letter
            sheet.column_dimensions[col_letter].width = max(max_len + 4, 12)

    return wb

def openpyxl_load_workbook(buffer: io.BytesIO) -> Workbook:
    """Helper to safely load workbook from bytes buffer."""
    buffer.seek(0)
    from openpyxl import load_workbook
    return load_workbook(buffer)

def generate_text_report(kpis: Dict[str, Any], insights: list) -> str:
    """Generates Markdown executive report summary text."""
    report = []
    report.append("# InsightAI - Executive Business Intelligence Report")
    report.append(f"**Generated:** Automatically from retail dataset\n")
    report.append("---")
    report.append("## Executive Key Performance Indicators")
    report.append(f"- **Total Sales Revenue:** ${kpis.get('total_revenue', 0):,.2f}")
    report.append(f"- **Total Net Profit:** ${kpis.get('total_profit', 0):,.2f}")
    report.append(f"- **Profit Margin:** {kpis.get('profit_margin', 0):.2f}%")
    report.append(f"- **Total Orders:** {kpis.get('total_orders', 0):,}")
    report.append(f"- **Unique Customers:** {kpis.get('total_customers', 0):,}")
    report.append(f"- **Average Order Value (AOV):** ${kpis.get('aov', 0):,.2f}")
    report.append(f"- **MoM Revenue Growth Rate:** {kpis.get('rev_growth_mom', 0):.2f}%\n")
    report.append("---")
    report.append("## Strategic AI Business Recommendations")
    
    for i, ins in enumerate(insights, 1):
        report.append(f"### {i}. {ins['title']} [{ins['type'].upper()}]")
        report.append(f"- **Category:** {ins['category']}")
        report.append(f"- **Insight:** {ins['message']}")
        report.append(f"- **Action Plan:** {ins['recommendation']}")
        report.append(f"- **Key Impact:** {ins['metric']}\n")

    report.append("---")
    report.append("*InsightAI BI Engine - Powered by Python & Machine Learning*")
    return "\n".join(report)
