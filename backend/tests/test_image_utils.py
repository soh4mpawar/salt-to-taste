import pytest
import io
from PIL import Image
from app.utils.image_processing import validate_image_format, image_to_base64, preprocess_image

def test_validate_image_format_png():
    png_bytes = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR'
    valid, msg = validate_image_format(png_bytes, "test.png")
    assert valid is True
    assert msg == "ok"

def test_validate_image_format_txt():
    txt_bytes = b'hello world'
    valid, msg = validate_image_format(txt_bytes, "test.txt")
    assert valid is False

def test_image_to_base64():
    test_bytes = b'hello'
    b64 = image_to_base64(test_bytes)
    assert b64 == "aGVsbG8="

def test_preprocess_image():
    img = Image.new("RGB", (3000, 2000), color="white")
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    original_bytes = buf.getvalue()
    
    processed, meta = preprocess_image(original_bytes, "test.jpg")
    assert processed != original_bytes
    assert processed.startswith(b'\xff\xd8\xff')
    assert meta["format"] == "image"
    
    new_img = Image.open(io.BytesIO(processed))
    from app.core.config import settings
    assert new_img.width <= settings.MAX_IMAGE_DIMENSION
    assert new_img.height <= settings.MAX_IMAGE_DIMENSION
