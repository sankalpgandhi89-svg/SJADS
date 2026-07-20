from reportlab.pdfgen import canvas
from sqlalchemy import text
from app.database.database import engine
import os


def generate_invoice(sale_id: int):

    # ==========================
    # PDF Save Location
    # ==========================
    folder = "invoices"

    if not os.path.exists(folder):
        os.makedirs(folder)

    pdf_path = os.path.join(folder, f"Invoice_{sale_id}.pdf")

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
    # Generate PDF
    # ==========================
    c = canvas.Canvas(pdf_path)

    c.setTitle("SJADS Invoice")

    # ==========================
    # Header
    # ==========================
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(300, 800, "SHANTI JAWA")

    c.setFont("Helvetica", 11)
    c.drawCentredString(300, 782, "Authorized Jawa & Yezdi Dealership")
    c.drawCentredString(300, 766, "Near Bus Stand, Morena (M.P.)")
    c.drawCentredString(300, 750, "Phone : +91-9876543210")
    c.drawCentredString(300, 734, "Email : info@shantijawa.com")

    c.line(40, 720, 555, 720)

    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(300, 700, "TAX INVOICE")

    # ==========================
# Invoice Details Box
# ==========================

    c.rect(40, 520, 520, 150)

    c.setFont("Helvetica", 12)

    c.drawString(60, 645, f"Invoice No : {sale['invoice_no']}")
    c.drawString(320, 645, f"Date : {sale['sale_date']}")

    c.drawString(60, 620, f"Customer : {sale['full_name']}")
    c.drawString(320, 620, f"Payment : {sale['payment_mode']}")

# ==========================
# Product Table
# ==========================

    c.line(40, 500, 560, 500)

    c.setFont("Helvetica-Bold", 12)

    c.drawString(60, 485, "Bike Model")
    c.drawString(280, 485, "Qty")
    c.drawString(360, 485, "Price")
    c.drawString(470, 485, "Total")

    c.line(40, 475, 560, 475)

    c.setFont("Helvetica", 12)

    c.drawString(60, 455, sale["model"])
    c.drawString(290, 455, str(sale["quantity"]))
    c.drawString(360, 455, str(sale["selling_price"]))
    c.drawString(
    470,
    455,
    str(sale["selling_price"] * sale["quantity"])
)

    c.line(40, 440, 560, 440)


    # ==========================
# Footer
# ==========================

    c.setFont("Helvetica-Bold", 12)
    c.drawString(60, 390, "Authorized Signature")

    c.line(60, 385, 220, 385)

    c.drawRightString(550, 390, "Thank You For Visiting Shanti Jawa")

    c.setFont("Helvetica", 10)
    c.drawRightString(550, 372, "Ride Safe. Ride Jawa.")