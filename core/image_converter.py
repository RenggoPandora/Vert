"""Image conversion module powered by Pillow."""

from pathlib import Path
from PIL import Image, ImageOps


def convert_image(
    input_path: Path | str,
    output_path: Path | str,
    quality: int = 90,
) -> Path:
    """Convert an image file to the target format inferred from output_path extension.

    Handles color mode adaptation (e.g. RGBA -> RGB for JPEG/PDF),
    icon generation sizing, and orientation metadata.
    """
    src = Path(input_path).resolve()
    dst = Path(output_path).resolve()
    dst.parent.mkdir(parents=True, exist_ok=True)

    target_ext = dst.suffix.lower()

    with Image.open(src) as img:
        # Correct orientation from EXIF if available
        try:
            img = ImageOps.exif_transpose(img) or img
        except Exception:
            pass

        if target_ext in [".jpg", ".jpeg"]:
            # JPEG cannot handle RGBA, P, or LA transparency directly
            if img.mode in ("RGBA", "LA", "P"):
                # Composite onto white background
                rgb_img = Image.new("RGB", img.size, (255, 255, 255))
                if img.mode == "P":
                    img = img.convert("RGBA")
                rgb_img.paste(img, mask=img.split()[-1] if "A" in img.mode else None)
                rgb_img.save(dst, format="JPEG", quality=quality, optimize=True)
            else:
                img.convert("RGB").save(dst, format="JPEG", quality=quality, optimize=True)

        elif target_ext == ".png":
            img.save(dst, format="PNG", optimize=True)

        elif target_ext == ".webp":
            # WebP supports both RGB and RGBA
            if img.mode not in ("RGB", "RGBA"):
                img = img.convert("RGBA" if "transparency" in img.info else "RGB")
            img.save(dst, format="WEBP", quality=quality)

        elif target_ext == ".bmp":
            # Standard BMP usually RGB
            if img.mode in ("RGBA", "LA", "P"):
                rgb_img = Image.new("RGB", img.size, (255, 255, 255))
                if img.mode == "P":
                    img = img.convert("RGBA")
                rgb_img.paste(img, mask=img.split()[-1] if "A" in img.mode else None)
                rgb_img.save(dst, format="BMP")
            else:
                img.convert("RGB").save(dst, format="BMP")

        elif target_ext == ".ico":
            # Windows icon format supports multiple resolutions up to 256x256
            icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
            # Ensure square or proportional scale
            rgba_img = img.convert("RGBA")
            rgba_img.save(dst, format="ICO", sizes=icon_sizes)

        elif target_ext == ".pdf":
            # Convert single image to PDF page
            if img.mode in ("RGBA", "LA", "P"):
                rgb_img = Image.new("RGB", img.size, (255, 255, 255))
                if img.mode == "P":
                    img = img.convert("RGBA")
                rgb_img.paste(img, mask=img.split()[-1] if "A" in img.mode else None)
                rgb_img.save(dst, format="PDF", resolution=100.0)
            else:
                img.convert("RGB").save(dst, format="PDF", resolution=100.0)

        else:
            # Fallback direct save using Pillow format detection
            img.save(dst)

    return dst
