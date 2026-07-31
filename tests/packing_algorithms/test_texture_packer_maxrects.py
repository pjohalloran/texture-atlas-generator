import pytest

from packing_algorithms.maxrects.texture_packer_maxrects import (
    FreeRectChoiceHeuristicEnum,
    TexturePackerMaxRects,
)
from packing_algorithms.texture_packer import PackerError

from helpers import assert_no_overlaps

HEURISTICS = [
    FreeRectChoiceHeuristicEnum.RectBestShortSideFit,
    FreeRectChoiceHeuristicEnum.RectBestLongSideFit,
    FreeRectChoiceHeuristicEnum.RectBestAreaFit,
    FreeRectChoiceHeuristicEnum.RectBottomLeftRule,
    FreeRectChoiceHeuristicEnum.RectContactPointRule,
]

RECT_SIZES = [(10, 10), (10, 10), (8, 8), (16, 4), (4, 16), (5, 5)]


@pytest.mark.parametrize("heuristic", HEURISTICS)
def test_pack_places_all_textures_without_overlap(heuristic):
    packer = TexturePackerMaxRects(heuristic, 64, 64)
    for i, (w, h) in enumerate(RECT_SIZES):
        packer.add_texture(w, h, "tex%d" % i)

    bin_width, bin_height, _ = packer.pack_textures(True, True)

    assert bin_width == 64
    assert bin_height == 64
    assert all(tex.placed for tex in packer.texArr)
    assert_no_overlaps([tex.get_rect() for tex in packer.texArr])


def test_bottom_left_heuristic_can_place_a_single_texture_in_an_empty_bin():
    # Regression test: _find_position_for_new_node_bottom_left() used an
    # 'and' where it should have used 'or' when comparing topSideY to
    # bestY, so bestRect could never be assigned and this heuristic always
    # raised PackerError, even for a texture that trivially fits.
    packer = TexturePackerMaxRects(FreeRectChoiceHeuristicEnum.RectBottomLeftRule, 64, 64)
    packer.add_texture(10, 10, "a")
    assert packer.texArr[0] is not None


def test_add_texture_raises_packer_error_when_too_big_for_bin():
    packer = TexturePackerMaxRects(FreeRectChoiceHeuristicEnum.RectBestAreaFit, 4, 4)
    with pytest.raises(PackerError):
        packer.add_texture(10, 10, "too-big")


def test_add_texture_raises_packer_error_once_bin_is_full():
    packer = TexturePackerMaxRects(FreeRectChoiceHeuristicEnum.RectBestAreaFit, 8, 8)
    packer.add_texture(8, 8, "fills-bin")
    with pytest.raises(PackerError):
        packer.add_texture(1, 1, "no-room-left")


def test_get_occupancy_reflects_used_area():
    packer = TexturePackerMaxRects(FreeRectChoiceHeuristicEnum.RectBestAreaFit, 32, 32)
    packer.add_texture(10, 10, "a")
    packer.add_texture(8, 8, "b")
    expected = float(10 * 10 + 8 * 8) / (32 * 32)
    assert packer.get_occupancy() == expected


def test_get_texture_returns_named_texture_and_none_for_unknown():
    packer = TexturePackerMaxRects(FreeRectChoiceHeuristicEnum.RectBestAreaFit, 32, 32)
    packer.add_texture(10, 10, "a")
    assert packer.get_texture("a").name == "a"
    assert packer.get_texture("does-not-exist") is None
