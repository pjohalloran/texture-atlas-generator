import os

import pytest

from data_parsers.json_parser import JsonParser
from data_parsers.parser import ParserError
from data_parsers.xml_parser import XmlParser
from packing_algorithms.maxrects.texture_packer_maxrects import (
    FreeRectChoiceHeuristicEnum,
    TexturePackerMaxRects,
)
from packing_algorithms.ratcliff.texture_packer_ratcliff import TexturePackerRatcliff
from util.utils import (
    clear_atlas_dir,
    get_atlas_path,
    get_color,
    get_maxrects_heuristic,
    get_packer,
    get_parser,
)


def test_get_color_parses_comma_separated_rgba():
    assert get_color("128,128,128,255") == (128, 128, 128, 255)


def test_get_color_parses_rgb():
    assert get_color("1,2,3") == (1, 2, 3)


def test_get_parser_xml_and_json():
    assert isinstance(get_parser("xml"), XmlParser)
    assert isinstance(get_parser("json"), JsonParser)


def test_get_parser_unknown_type_raises():
    with pytest.raises(ParserError):
        get_parser("yaml")


@pytest.mark.parametrize("name,expected", [
    ("shortside", FreeRectChoiceHeuristicEnum.RectBestShortSideFit),
    ("longside", FreeRectChoiceHeuristicEnum.RectBestLongSideFit),
    ("area", FreeRectChoiceHeuristicEnum.RectBestAreaFit),
    ("bottomleft", FreeRectChoiceHeuristicEnum.RectBottomLeftRule),
    ("contactpoint", FreeRectChoiceHeuristicEnum.RectContactPointRule),
])
def test_get_maxrects_heuristic(name, expected):
    assert get_maxrects_heuristic(name) == expected


def test_get_maxrects_heuristic_unknown_raises():
    with pytest.raises(NotImplementedError):
        get_maxrects_heuristic("nonsense")


def test_get_packer_maxrects_uses_given_size_and_heuristic():
    packer = get_packer("maxrects", size=128, heuristic="area")
    assert isinstance(packer, TexturePackerMaxRects)
    assert packer.bin_width == 128
    assert packer.bin_height == 128
    assert packer.heuristic == FreeRectChoiceHeuristicEnum.RectBestAreaFit


def test_get_packer_ratcliff():
    assert isinstance(get_packer("ratcliff"), TexturePackerRatcliff)


def test_get_packer_unknown_algorithm_raises():
    with pytest.raises(NotImplementedError):
        get_packer("unknown-algo")


def test_get_atlas_path_joins_resource_path():
    assert get_atlas_path("/tmp/game") == os.path.join("/tmp/game", "atlases")


def test_clear_atlas_dir_creates_missing_directory(tmp_path):
    target = tmp_path / "atlases"
    clear_atlas_dir(str(target))
    assert target.is_dir()


def test_clear_atlas_dir_wipes_existing_contents(tmp_path):
    target = tmp_path / "atlases"
    target.mkdir()
    (target / "stale.xml").write_text("old data")

    clear_atlas_dir(str(target))

    assert target.is_dir()
    assert list(target.iterdir()) == []
