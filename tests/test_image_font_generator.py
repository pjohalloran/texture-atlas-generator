import os
import xml.dom.minidom

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


def test_pack_fonts_dedupes_repeated_characters():
    # Regression test: a repeated character used to add multiple same-named
    # Textures to the packer. image_dict (a real dict) collapsed to one
    # entry per name, but get_texture() returns the first match while
    # AtlasData.add_texture() keeps the last - so the manifest and the
    # pasted pixels disagreed on where that character actually was.
    packer, _, image_dict = ImageFontGenerator.pack_fonts(FONT_FILE, 16, "AAB", (0, 0, 0, 0), 64)

    names = [tex.name for tex in packer.texArr]
    assert len(names) == len(set(names)) == 2
    assert len(image_dict) == 2


def test_create_imagefont_manifest_has_one_entry_per_character(tmp_path):
    ImageFontGenerator.create_fonts_dir(str(tmp_path))
    ImageFontGenerator.create_imagefont(str(tmp_path), FONT_FILE, 16, "AAB", (0, 0, 0, 0), "png", "xml")

    manifest_path = tmp_path / "fonts" / "DejaVuSans_16.xml"
    doc = xml.dom.minidom.parse(str(manifest_path))
    image_names = [el.getAttribute("name") for el in doc.getElementsByTagName("Image")]

    # One manifest entry per unique character, not one per occurrence in the
    # input text - and no two entries claiming the same name/position.
    assert len(image_names) == len(set(image_names)) == 2
