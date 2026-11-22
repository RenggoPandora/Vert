from pathlib import Path
from PIL import Image
from core.image_converter import convert_image


def test_convert_rgba_png_to_jpg(tmp_path):
    src = tmp_path / "test.png"
    # Create RGBA image with transparent pixels
    img = Image.new("RGBA", (100, 100), (255, 0, 0, 128))
    img.save(src, "PNG")

    dst = tmp_path / "test.jpg"
    out = convert_image(src, dst)

    assert out.exists()
    assert out.stat().st_size > 0
    with Image.open(out) as res:
        assert res.format == "JPEG"
        assert res.mode == "RGB"


def test_convert_jpg_to_png(tmp_path):
    src = tmp_path / "test.jpg"
    img = Image.new("RGB", (64, 64), (0, 255, 0))
    img.save(src, "JPEG")

    dst = tmp_path / "test.png"
    out = convert_image(src, dst)

    assert out.exists()
    with Image.open(out) as res:
        assert res.format == "PNG"


def test_convert_png_to_webp(tmp_path):
    src = tmp_path / "test.png"
    img = Image.new("RGBA", (50, 50), (0, 0, 255, 200))
    img.save(src, "PNG")

    dst = tmp_path / "test.webp"
    out = convert_image(src, dst)

    assert out.exists()
    with Image.open(out) as res:
        assert res.format == "WEBP"


def test_convert_png_to_ico(tmp_path):
    src = tmp_path / "test.png"
    img = Image.new("RGBA", (128, 128), (255, 255, 0, 255))
    img.save(src, "PNG")

    dst = tmp_path / "test.ico"
    out = convert_image(src, dst)

    assert out.exists()
    with Image.open(out) as res:
        assert res.format == "ICO"


def test_convert_image_to_pdf(tmp_path):
    src = tmp_path / "test.png"
    img = Image.new("RGBA", (80, 80), (100, 100, 100, 255))
    img.save(src, "PNG")

    dst = tmp_path / "test.pdf"
    out = convert_image(src, dst)

    assert out.exists()
    assert out.stat().st_size > 0
    with open(out, "rb") as f:
        header = f.read(4)
        assert header == b"%PDF"
