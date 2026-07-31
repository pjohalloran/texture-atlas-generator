import json

import pytest

from atlas.atlas_data import AtlasData
from atlas.texture import Texture
from data_parsers.json_parser import JsonParser
from data_parsers.parser import ParserError


def _build_atlas():
    atlas = AtlasData(name="sprites", width=64, height=64, color_mode="RGBA", file_type="png", border=1)
    tex = Texture(10, 20, name="a.png")
    tex.place_texture(1, 2)
    atlas.add_texture(tex)
    return atlas


def test_parse_round_trips_atlas_and_texture_fields():
    parser = JsonParser()
    parser.parse(_build_atlas())

    data = json.loads(parser.parser_output)
    atlas_json = data["Atlas"]
    assert atlas_json["name"] == "sprites"
    assert atlas_json["width"] == 64
    assert atlas_json["height"] == 64
    assert atlas_json["color_mode"] == "RGBA"
    assert atlas_json["file_type"] == "png"

    image_json = atlas_json["texture_dict"]["a.png"]["Image"]
    assert image_json["name"] == "a.png"
    assert image_json["width"] == 10
    assert image_json["height"] == 20
    assert image_json["x"] == 1
    assert image_json["y"] == 2


def test_get_file_ext():
    assert JsonParser().get_file_ext() == "json"


def test_save_writes_parsed_output_to_disk(tmp_path):
    parser = JsonParser()
    parser.parse(_build_atlas())
    out_file = tmp_path / "sprites.json"

    parser.save(str(out_file))

    assert out_file.read_text() == parser.parser_output


def test_save_raises_before_parse_is_called(tmp_path):
    parser = JsonParser()
    with pytest.raises(ParserError):
        parser.save(str(tmp_path / "sprites.json"))
