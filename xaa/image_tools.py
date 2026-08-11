from __future__ import annotations

from io import BytesIO
from pathlib import Path

from PIL import Image, ImageOps

from .errors import GenerationError


def prepare_final_image(
    base_image: bytes,
    destination: Path,
    *,
    max_upload_mb: float,
) -> None:
    try:
        base = ImageOps.exif_transpose(Image.open(BytesIO(base_image))).convert("RGB")
    except Exception as exc:
        raise GenerationError(f"Could not process the generated image: {exc}") from exc

    destination.parent.mkdir(parents=True, exist_ok=True)

    byte_limit = int(max_upload_mb * 1024 * 1024)
    for quality in (92, 88, 84, 78, 70):
        base.save(destination, format="JPEG", quality=quality, optimize=True, progressive=True)
        if destination.stat().st_size <= byte_limit:
            return
    raise GenerationError(
        f"The image is still larger than {max_upload_mb:.1f} MB after compression. "
        "Reduce generation.image_size."
    )
