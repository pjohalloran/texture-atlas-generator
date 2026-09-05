import xml.dom.minidom

import pytest

from atlas.atlas_data import AtlasData
from atlas.texture import Texture
from data_parsers.parser import ParserError
from data_parsers.xml_parser import XmlParser


def _build_atlas():
    atlas = AtlasData(name="sprites", width=64, height=64, color_mode="RGBA", file_type="png", border=1)
    tex = Texture(10, 20, name="a.png")
    tex.place_texture(1, 2)
    atlas.add_texture(tex)
    return atlas


def test_parse_produces_atlas_and_image_elements_with_expected_attributes():
    parser = XmlParser()
    parser.parse(_build_atlas())

    doc = xml.dom.minidom.parseString(parser.parser_output)
    atlas_elements = doc.getElementsByTagName("Atlas")
    assert len(atlas_elements) == 1
    atlas_el = atlas_elements[0]
    assert atlas_el.getAttribute("name") == "sprites"
    assert atlas_el.getAttribute("mode") == "RGBA"
    assert atlas_el.getAttribute("type") == "png"
    assert atlas_el.getAttribute("border") == "1"
    assert atlas_el.getAttribute("width") == "64"
    assert atlas_el.getAttribute("height") == "64"

    image_elements = doc.getElementsByTagName("Image")
    assert len(image_elements) == 1
    image_el = image_elements[0]
    assert image_el.getAttribute("name") == "a.png"
    assert image_el.getAttribute("width") == "10"
    assert image_el.getAttribute("height") == "20"
    assert image_el.getAttribute("x") == "1"
    assert image_el.getAttribute("y") == "2"


def test_get_file_ext():
    assert XmlParser().get_file_ext() == "xml"


def test_save_writes_parsed_output_to_disk(tmp_path):
    parser = XmlParser()
    parser.parse(_build_atlas())
    out_file = tmp_path / "sprites.xml"

    parser.save(str(out_file))

    assert out_file.read_text() == parser.parser_output


def test_save_raises_before_parse_is_called(tmp_path):
    parser = XmlParser()
    with pytest.raises(ParserError):
        parser.save(str(tmp_path / "sprites.xml"))
