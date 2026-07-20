from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer
)

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

from sqlalchemy import text

from app.database.database import engine

import os


def generate_invoice_v2(sale_id: int):

    # ==========================
    # PDF Save Location
    # ==========================
    folder = "invoices"

    if not os.path.exists(folder):
        os.makedirs(folder)

    pdf_path = os.path.join(
        folder,
        f"Invoice_{sale_id}.pdf"
    )

    # ==========================
    # Get Sale Details
    # ==========================
    query = text("""
        SELECT
            s.invoice_no,
            s.sale_date,
            s.quantity,
            s.selling_price,
            s.payment_mode,
            c.full_name,
            b.model
        FROM sales s
        JOIN customers c
            ON s.customer_id = c.customer_id
        JOIN bikes b
            ON s.bike_id = b.bike_id
        WHERE s.sale_id = :sale_id
        AND s.is_active = 1
    """)

    with engine.connect() as conn:

        sale = conn.execute(
            query,
            {
                "sale_id": sale_id
            }
        ).mappings().first()

    if sale is None:
        raise Exception("Sale Not Found")

    # ==========================
    # Styles
    # ==========================
    styles = getSampleStyleSheet()

    title_style = styles["Title"]
    heading_style = styles["Heading2"]
    normal_style = styles["BodyText"]

    # ==========================
    # PDF Document
    # ==========================
    doc = SimpleDocTemplate(pdf_path)

    elements = []

    # ==========================
    # Header
    # ==========================
    elements.append(
        Paragraph(
            "SHANTI JAWA",
            title_style
        )
    )

    elements.append(
        Paragraph(
            "Authorized Jawa & Yezdi Dealership",
            heading_style
        )
    )

    elements.append(
        Paragraph(
            "Near Bus Stand, Morena (M.P.)",
            normal_style
        )
    )

    elements.append(
        Paragraph(
            "Phone : +91-9876543210",
            normal_style
        )
    )

    elements.append(
        Paragraph(
            "Email : info@shantijawa.com",
            normal_style
        )
    )

    elements.append(
        Spacer(1, 0.30 * inch)
    )

    # ==========================
    # Invoice Title
    # ==========================
    elements.append(
        Paragraph(
            "<b>TAX INVOICE</b>",
            heading_style
        )
    )

    elements.append(
        Spacer(1, 0.20 * inch)
    )

    # ==========================
    # Invoice Details
    # ==========================
    elements.append(
        Paragraph(
            f"<b>Invoice No :</b> {sale['invoice_no']}",
            normal_style
        )
    )

    elements.append(
        Paragraph(
            f"<b>Date :</b> {sale['sale_date']}",
            normal_style
        )
    )

    elements.append(
        Paragraph(
            f"<b>Customer :</b> {sale['full_name']}",
            normal_style
        )
    )

    elements.append(
        Paragraph(
            f"<b>Payment :</b> {sale['payment_mode']}",
            normal_style
        )
    )

    elements.append(
        Spacer(1, 0.25 * inch)
    )
        # ==========================
    # Product Table
    # ==========================
    data = [
        ["Bike Model", "Qty", "Price", "Total"],
        [
            sale["model"],
            str(sale["quantity"]),
            f"Rs. {sale['selling_price']}",
            f"Rs. {sale['selling_price'] * sale['quantity']}"
        ]
    ]

    table = Table(data)

    table.setStyle(TableStyle([

        ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),

        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),

        ("ALIGN", (0, 0), (-1, -1), "CENTER"),

        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),

        ("FONTSIZE", (0, 0), (-1, -1), 11),

        ("BOTTOMPADDING", (0, 0), (-1, 0), 10),

        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),

        ("GRID", (0, 0), (-1, -1), 1, colors.black)

    ]))

    elements.append(table)

    elements.append(
        Spacer(1, 0.30 * inch)
    )

    # ==========================
    # Grand Total
    # ==========================
    elements.append(
        Paragraph(
            f"<b>Grand Total : Rs. {sale['selling_price'] * sale['quantity']}</b>",
            heading_style
        )
    )

    elements.append(
        Spacer(1, 0.40 * inch)
    )

    # ==========================
    # Footer
    # ==========================
    elements.append(
        Paragraph(
            "<b>Authorized Signature</b>",
            normal_style
        )
    )

    elements.append(
        Spacer(1, 0.50 * inch)
    )

    elements.append(
        Paragraph(
            "Thank You For Visiting Shanti Jawa",
            heading_style
        )
    )

    elements.append(
        Paragraph(
            "Ride Safe • Ride Jawa",
            normal_style
        )
    )

    # ==========================
    # Generate PDF
    # ==========================
    doc.build(elements)

    return pdf_path