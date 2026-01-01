from pathlib import Path
import sys

from PIL import Image

# Make sure the project root (the directory containing resize_worker.py) is on sys.path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
    
from resize_worker import resize_image


def _create_image(path: Path, size=(800, 600), mode: str = "RGBA") -> None:
    """
    Create a simple solid-color image. For RGBA we include an alpha channel
    to exercise the transparency-handling branch in resize_image.
    """
    if mode == "RGBA":
        color = (10, 20, 30, 128)  # semi-transparent
    else:
        color = (10, 20, 30)

    img = Image.new(mode, size, color)
    img.save(path)


def test_resize_image_creates_file_and_respects_max_width(tmp_path: Path) -> None:
    src = tmp_path / "src.png"
    dst = tmp_path / "dst.png"

    # Create a relatively large RGBA image (with alpha channel)
    _create_image(src, size=(800, 600), mode="RGBA")

    # Run the resize-worker's resize logic
    resize_image(src, dst, max_width=400)

    # The resized file must exist
    assert dst.exists(), "Resized image file should be created"

    with Image.open(dst) as im:
        # Width must be at most the requested max_width
        assert im.size[0] <= 400
        assert im.size[0] > 0
        assert im.size[1] > 0

        # The resize-worker always normalises output to RGB (no alpha)
        assert im.mode == "RGB"
