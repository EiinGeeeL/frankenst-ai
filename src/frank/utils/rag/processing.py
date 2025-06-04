import base64
import io
from PIL import Image

def parse_docs(docs: list) -> dict:
    """Split base64-encoded images and texts/tables unstructured composite elements"""
    b64 = []
    text = []
    for doc in docs:
        try:
            base64.b64decode(doc)
            b64.append(doc)
        except Exception as e:
            text.append(doc)
    return {"images": b64, "texts": text}

def parse_context(docs_by_type: dict) -> dict:
    """Built texts and images context from unstructured composite elements."""
    context_text = ""
    context_images = []

    if len(docs_by_type["texts"]) > 0:
        for text_element in docs_by_type["texts"]:
            context_text += text_element.text + "\n"

    if len(docs_by_type["images"]) > 0:
        for image in docs_by_type["images"]:
            context_images.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{image}"}
            })

    return {
        "texts": context_text.strip(),
        "images": context_images
    }

def show_base64_image(base64_string: str) -> dict:
    # Remove any header like "data:image/png;base64," if present
    if ',' in base64_string:
        base64_string = base64_string.split(',')[1]
    image_data = base64.b64decode(base64_string)
    image = Image.open(io.BytesIO(image_data))
    image.show()