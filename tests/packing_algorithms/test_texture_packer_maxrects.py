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


def test_allow_rotations_false_rejects_a_texture_that_only_fits_rotated():
    # 20x8 doesn't fit upright in a 10-wide bin, but would fit as 8x20.
    packer = TexturePackerMaxRects(FreeRectChoiceHeuristicEnum.RectBestAreaFit, 10, 20)
    with pytest.raises(PackerError):
        packer.add_texture(20, 8, "tall-when-rotated")


def test_allow_rotations_true_places_and_flips_a_texture_that_only_fits_rotated():
    packer = TexturePackerMaxRects(FreeRectChoiceHeuristicEnum.RectBestAreaFit, 10, 20)
    packer.allow_rotations = True
    packer.add_texture(20, 8, "tall-when-rotated")
    packer.pack_textures(True, True)

    tex = packer.get_texture("tall-when-rotated")
    assert tex.flipped is True
    assert (tex.width, tex.height) == (8, 20)
    assert tex.width * tex.height == 20 * 8


@pytest.mark.parametrize("heuristic", HEURISTICS)
def test_allow_rotations_true_keeps_placements_non_overlapping(heuristic):
    packer = TexturePackerMaxRects(heuristic, 40, 40)
    packer.allow_rotations = True
    sizes = [(30, 6), (6, 30), (20, 5), (5, 20), (10, 10)]
    for i, (w, h) in enumerate(sizes):
        packer.add_texture(w, h, "tex%d" % i)
    packer.pack_textures(True, True)

    assert all(tex.placed for tex in packer.texArr)
    for tex, (orig_w, orig_h) in zip(packer.texArr, sizes):
        assert tex.width * tex.height == orig_w * orig_h
    assert_no_overlaps([tex.get_rect() for tex in packer.texArr])
