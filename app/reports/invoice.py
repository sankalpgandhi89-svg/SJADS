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

    print(sale)

    # ==========================
    # Generate PDF
    # ==========================
    c = canvas.Canvas(pdf_path)

    c.setTitle("SJADS Invoice")

    c.setFont("Helvetica-Bold", 18)
    c.drawString(180, 800, "SHANTI JAWA")

    c.setFont("Helvetica", 12)

    c.drawString(50, 760, f"Invoice No : {sale['invoice_no']}")
    c.drawString(50, 740, f"Customer   : {sale['full_name']}")
    c.drawString(50, 720, f"Bike       : {sale['model']}")
    c.drawString(50, 700, f"Quantity   : {sale['quantity']}")
    c.drawString(50, 680, f"Amount     : Rs. {sale['selling_price']}")
    c.drawString(50, 660, f"Payment    : {sale['payment_mode']}")
    c.drawString(50, 640, f"Date       : {sale['sale_date']}")

    c.line(50, 620, 550, 620)

    c.drawString(50, 600, "Thank You For Visiting Shanti Jawa")

    c.save()

    return pdf_path