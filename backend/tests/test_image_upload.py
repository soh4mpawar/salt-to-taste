import pytest
import io
from PIL import Image
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.mark.asyncio
async def test_image_upload_endpoint():
    img = Image.new("RGB", (100, 100), color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    png_bytes = buf.getvalue()
    
    response = client.post(
        "/api/v1/recipes/image-upload",
        data={"user_id": "00000000-0000-0000-0000-000000000001"},
        files={"file": ("test.png", png_bytes, "image/png")}
    )
    
    assert response.status_code not in (413, 415, 500)
    assert response.status_code in (201, 422)
    
    if response.status_code == 201:
        data = response.json()
        assert "id" in data
        assert "extraction_method" in data
