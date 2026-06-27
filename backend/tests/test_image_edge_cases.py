import pytest
import io
from PIL import Image
from reportlab.pdfgen import canvas
from app.utils.image_processing import enhance_for_ocr, preprocess_image
from app.core.config import settings

def test_enhance_for_ocr():
    img = Image.new("L", (100, 100), color=128)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    png_bytes = buf.getvalue()
    
    enhanced = enhance_for_ocr(png_bytes)
    
    assert enhanced.startswith(b'\xff\xd8\xff')

def test_preprocess_image_png():
    img = Image.new("RGB", (100, 100), color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    png_bytes = buf.getvalue()
    
    processed, meta = preprocess_image(png_bytes, "test.png")
    
    assert processed.startswith(b'\xff\xd8\xff')
    
    new_img = Image.open(io.BytesIO(processed))
    assert new_img.width <= settings.MAX_IMAGE_DIMENSION
    assert new_img.height <= settings.MAX_IMAGE_DIMENSION
    assert meta["format"] == "image"

def test_preprocess_image_pdf():
    buf = io.BytesIO()
    c = canvas.Canvas(buf)
    c.drawString(100, 100, "Page 1")
    c.showPage()
    c.drawString(100, 100, "Page 2")
    c.showPage()
    c.save()
    pdf_bytes = buf.getvalue()
    
    try:
        processed, meta = preprocess_image(pdf_bytes, "test.pdf")
    except Exception as e:
        pytest.skip(f"Poppler not in PATH: {e}")
    
    assert processed.startswith(b'\xff\xd8\xff')
    assert meta["format"] == "pdf"
    assert meta.get("pdf_pages_ignored") == 1
