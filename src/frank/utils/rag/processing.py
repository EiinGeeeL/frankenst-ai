import base64
import io
from PIL import Image

def parse_docs(docs: list) -> dict:
    """Split base64-encoded images and texts/tables"""
    b64 = []
    text = []
    for doc in docs:
        try:
            base64.b64decode(doc)
            b64.append(doc)
        except Exception as e:
            text.append(doc)
    return {"images": b64, "texts": text}

def show_base64_image(base64_string: str) -> dict:
    # Remove any header like "data:image/png;base64," if present
    if ',' in base64_string:
        base64_string = base64_string.split(',')[1]
    image_data = base64.b64decode(base64_string)
    image = Image.open(io.BytesIO(image_data))
    image.show()