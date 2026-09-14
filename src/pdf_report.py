"""
PDF report generator for business leads
"""

import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import List
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT

logger = logging.getLogger(__name__)


class PDFReportGenerator:
    """Generates PDF reports for business leads"""

    def __init__(self, db_manager, output_dir: str = "output"):
        """
        Initialize PDF report generator

        Args:
            db_manager: Database manager instance
            output_dir: Output directory path
        """
        self.db_manager = db_manager
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_pdf(self, filename: str = "verified_businesses.pdf") -> str:
        """
        Generate PDF report

        Args:
            filename: Output filename

        Returns:
            Path to generated PDF
        """
        logger.info(f"Generating PDF report: {filename}")

        output_path = self.output_dir / filename

        # Create PDF document
        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=landscape(letter),
            rightMargin=0.5*inch,
            leftMargin=0.5*inch,
            topMargin=0.5*inch,
            bottomMargin=0.5*inch
        )

        # Get styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.darkblue,
            alignment=TA_CENTER,
            spaceAfter=20
        )

        # Build content
        content = []

        # Title page
        content.append(Paragraph("Verified Business Leads", title_style))
        content.append(Paragraph(f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}",
                                styles['Normal']))
        content.append(PageBreak())

        # Get statistics
        stats = self.db_manager.get_statistics()
        all_businesses = self.db_manager.get_all_businesses()

        # Summary statistics
        content.append(Paragraph("Summary Statistics", styles['Heading2']))

        summary_data = [
            ['Metric', 'Value'],
            ['Total Records', str(stats['total'])],
            ['UAE Businesses', str(stats['by_country'].get('UAE', 0))],
            ['USA Businesses', str(stats['by_country'].get('USA', 0))],
            ['Websites Checked', str(stats['websites_checked'])],
            ['Working Websites', str(stats['working_websites'])],
            ['Public Emails', str(stats['public_emails'])],
            ['Public Phones', str(stats['public_phones'])],
            ['Duplicates', str(stats['duplicates'])],
            ['Rejected', str(stats['rejected'])],
        ]

        summary_table = Table(summary_data, colWidths=[2*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))

        content.append(summary_table)
        content.append(PageBreak())

        # Business data table
        content.append(Paragraph("Business Leads", styles['Heading2']))

        # Prepare business data - all_businesses are now already dictionaries
        business_data = [['Business', 'Category', 'City', 'Country', 'Phone',
                         'Email', 'Website', 'Rating', 'Lead Score',
                         'Website Status', 'Source']]

        for business_dict in all_businesses:
            if business_dict.get('duplicate') != 'true':  # Skip duplicates
                row = [
                    business_dict.get('business_name') or '',
                    business_dict.get('category') or '',
                    business_dict.get('city') or '',
                    business_dict.get('country') or '',
                    business_dict.get('phone') or '',
                    business_dict.get('email') or '',
                    business_dict.get('website') or '',
                    str(business_dict.get('rating')) if business_dict.get('rating') else '',
                    str(business_dict.get('lead_score')) if business_dict.get('lead_score') else '',
                    business_dict.get('website_status') or '',
                    business_dict.get('source') or ''
                ]
                business_data.append(row)

        # Create table
        table = Table(business_data, colWidths=[1.5*inch, 1*inch, 1*inch, 0.8*inch,
                                              1*inch, 1.2*inch, 1.5*inch, 0.6*inch,
                                              0.7*inch, 1*inch, 1*inch])

        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))

        content.append(table)

        # Build PDF
        doc.build(content)

        logger.info(f"PDF report generated: {output_path}")
        return str(output_path)
