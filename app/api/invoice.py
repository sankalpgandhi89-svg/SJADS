from fastapi import APIRouter
from fastapi.responses import FileResponse

from app.reports.invoice import generate_invoice

router = APIRouter(
    prefix="/invoice",
    tags=["Invoice"]
)


@router.get("/{sale_id}")
def download_invoice(sale_id: int):

    pdf = generate_invoice(sale_id)

    return FileResponse(
        pdf,
        media_type="application/pdf",
        filename=f"Invoice_{sale_id}.pdf"
    )