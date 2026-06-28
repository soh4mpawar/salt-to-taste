import io
import base64
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import pdf2image
from app.core.config import settings

def detect_image_orientation(image_bytes: bytes) -> bytes:
    img = Image.open(io.BytesIO(image_bytes))
    orig_format = img.format
    img = ImageOps.exif_transpose(img)
    out_buffer = io.BytesIO()
    
    save_format = orig_format or "JPEG"
    if save_format == "JPEG":
        if img.mode == 'RGBA':
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[3])
            img = background
        elif img.mode not in ('RGB', 'L'):
            img = img.convert('RGB')
            
    img.save(out_buffer, format=save_format)
    return out_buffer.getvalue()

def enhance_for_ocr(image_bytes: bytes) -> bytes:
    img = Image.open(io.BytesIO(image_bytes))
    if img.mode != 'L':
        img = img.convert('L')
    
    enhancer_contrast = ImageEnhance.Contrast(img)
    img = enhancer_contrast.enhance(1.5)
    
    enhancer_sharpness = ImageEnhance.Sharpness(img)
    img = enhancer_sharpness.enhance(2.0)
    
    img = img.filter(ImageFilter.SHARPEN)
    
    img = img.convert('RGB')
    
    out_buffer = io.BytesIO()
    img.save(out_buffer, format="JPEG", quality=settings.IMAGE_QUALITY)
    return out_buffer.getvalue()

def validate_image_format(file_bytes: bytes, filename: str) -> tuple[bool, str]:
    if filename:
        ext = filename.lower().split('.')[-1]
        if ext not in ['jpg', 'jpeg', 'png', 'webp', 'pdf']:
            return False, f"Unsupported file extension: {ext}"
            
    # Check magic bytes
    if file_bytes.startswith(b'\xff\xd8\xff'):
        return True, "ok" # JPEG
    elif file_bytes.startswith(b'\x89PNG\r\n\x1a\n'):
        return True, "ok" # PNG
    elif file_bytes.startswith(b'%PDF-'):
        return True, "ok" # PDF
    elif file_bytes.startswith(b'RIFF') and file_bytes[8:12] == b'WEBP':
        return True, "ok" # WEBP
        
    return False, "Unsupported file format or invalid magic bytes"

def preprocess_image(file_bytes: bytes, filename: str) -> tuple[bytes, dict]:
    metadata = {}
    
    if (filename and filename.lower().endswith('.pdf')) or file_bytes.startswith(b'%PDF-'):
        info = pdf2image.pdfinfo_from_bytes(file_bytes)
        num_pages = info.get("Pages", 1)
        
        images = pdf2image.convert_from_bytes(file_bytes, first_page=1, last_page=1)
        if not images:
            raise ValueError("Could not extract image from PDF")
        img = images[0]
        
        if num_pages > 1:
            metadata["pdf_pages_ignored"] = num_pages - 1
            
        metadata["format"] = "pdf"
    else:
        oriented_bytes = detect_image_orientation(file_bytes)
        img = Image.open(io.BytesIO(oriented_bytes))
        metadata["format"] = "image"
        
    if img.mode == 'RGBA':
        background = Image.new('RGB', img.size, (255, 255, 255))
        background.paste(img, mask=img.split()[3])
        img = background
    elif img.mode not in ('RGB', 'L'):
        img = img.convert('RGB')
        
    max_dim = settings.MAX_IMAGE_DIMENSION
    if img.width > max_dim or img.height > max_dim:
        img.thumbnail((max_dim, max_dim), Image.LANCZOS)
        
    out_buffer = io.BytesIO()
    img.save(out_buffer, format="JPEG", quality=settings.IMAGE_QUALITY)
    
    return out_buffer.getvalue(), metadata

def image_to_base64(image_bytes: bytes) -> str:
    return base64.b64encode(image_bytes).decode("utf-8")

def get_image_metadata(image_bytes: bytes) -> dict:
    with Image.open(io.BytesIO(image_bytes)) as img:
        return {
            "width": img.width,
            "height": img.height,
            "format": img.format,
            "mode": img.mode
        }
