import io

from pypdf import PdfReader
from pypdf.errors import PdfReadError


def extract_pages(data: bytes) -> list[str]:
    """Return the text of each page (index 0 = page 1). Raises ValueError for unreadable PDFs."""
    try:
        reader = PdfReader(io.BytesIO(data))
        return [(page.extract_text() or "") for page in reader.pages]
    except PdfReadError as exc:
        raise ValueError("Could not read the PDF.") from exc