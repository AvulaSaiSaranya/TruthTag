"""Validate product image uploads and report current catalog matching capability."""

import io
import warnings

from PIL import Image, UnidentifiedImageError

from .models import ImageIdentificationResponse

MAX_IMAGE_SIZE_BYTES = 10 * 1024 * 1024
MAX_IMAGE_PIXELS = 25_000_000
ALLOWED_CONTENT_TYPES = {
    "image/jpeg": "JPEG",
    "image/png": "PNG",
    "image/webp": "WEBP",
    "image/gif": "GIF",
}

IMAGE_DISCLAIMER = (
    "IMAGE RECOGNITION DISCLAIMER: This demo does not have verified reference-image baselines, "
    "so it does not produce visual matches or authenticity assessments from uploaded images. "
    "Use a product serial, SKU, or batch identifier for a registry lookup."
)


def identify_product_image(
    file_bytes: bytes,
    file_name: str,
    content_type: str
) -> ImageIdentificationResponse:
    """Validate an uploaded image without inventing a match score or candidate."""
    if len(file_bytes) > MAX_IMAGE_SIZE_BYTES:
        raise ValueError("Image file exceeds maximum allowable size of 10MB.")

    if len(file_bytes) < 100:
        raise ValueError("File is too small or corrupted.")

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            image = Image.open(io.BytesIO(file_bytes))
            if image.format != ALLOWED_CONTENT_TYPES.get(content_type):
                raise ValueError("Image content does not match the declared file format.")
            if image.width * image.height > MAX_IMAGE_PIXELS:
                raise ValueError("Image dimensions exceed the maximum allowable pixel count.")
            image.verify()
    except ValueError:
        raise
    except (Image.DecompressionBombError, Image.DecompressionBombWarning):
        raise ValueError("Image dimensions exceed the maximum allowable pixel count.")
    except (UnidentifiedImageError, OSError):
        raise ValueError("Uploaded file is not a valid image.")

    return ImageIdentificationResponse(
        status="unavailable",
        message=(
            "The image passed file validation, but this catalog has no verified visual "
            "baselines. No image match was attempted. Search by the product's printed "
            "serial number, SKU, or batch code instead."
        ),
        uploaded_file_name=file_name,
        candidates=[],
        manual_search_recommended=True,
        disclaimer=IMAGE_DISCLAIMER
    )
