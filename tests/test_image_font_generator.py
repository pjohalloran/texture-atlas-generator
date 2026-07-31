import os

import pytest

from packing_algorithms.maxrects.texture_packer_maxrects import TexturePackerMaxRects
from packing_algorithms.ratcliff.texture_packer_ratcliff import TexturePackerRatcliff

import ImageFontGenerator

FONT_FILE = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

pytestmark = pytest.mark.skipif(not os.path.isfile(FONT_FILE), reason="requires a system truetype font")


def test_pack_fonts_defaults_to_maxrects():
    packer, _, _ = ImageFontGenerator.pack_fonts(FONT_FILE, 16, "AB", (0, 0, 0, 0), 64)
    assert isinstance(packer, TexturePackerMaxRects)


def test_pack_fonts_honors_packing_algorithm_argument():
    # Regression test: pack_fonts() used to hardcode get_packer('maxrects', ...),
    # silently ignoring the -a/--packing-algorithm CLI flag entirely.
    packer, _, _ = ImageFontGenerator.pack_fonts(FONT_FILE, 16, "AB", (0, 0, 0, 0), 64, packing_algorithm="ratcliff")
    assert isinstance(packer, TexturePackerRatcliff)
