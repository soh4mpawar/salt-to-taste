import io
import pytesseract
from PIL import Image
from app.core.config import settings

async def extract_text_tesseract(image_bytes: bytes) -> tuple[str, float]:
    img = Image.open(io.BytesIO(image_bytes))
    
    try:
        data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
    except Exception as e:
        # If tesseract is not installed or crashes, return empty
        return "", 0.0
    confidences = []
    for i, conf in enumerate(data.get('conf', [])):
        text = data['text'][i].strip()
        if text and int(conf) != -1:
            confidences.append(float(conf))
            
    mean_conf = sum(confidences) / len(confidences) if confidences else 0.0
    
    try:
        extracted_text = pytesseract.image_to_string(img).strip()
    except Exception as e:
        extracted_text = ""
        
    return extracted_text, mean_conf

async def should_use_tesseract(image_bytes: bytes) -> tuple[bool, str, float]:
    extracted_text, mean_conf = await extract_text_tesseract(image_bytes)
    
    if mean_conf >= settings.TESSERACT_CONFIDENCE_THRESHOLD and len(extracted_text) > 200:
        return True, extracted_text, mean_conf
        
    return False, "", mean_conf
