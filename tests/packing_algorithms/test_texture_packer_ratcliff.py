import pytest

from packing_algorithms.ratcliff.texture_packer_ratcliff import TexturePackerRatcliff
from packing_algorithms.texture_packer import PackerError

from helpers import assert_no_overlaps

RECT_SIZES = [(10, 10), (10, 10), (8, 8), (16, 4), (4, 16), (5, 5)]

# Reproduces a real crash found via manual testing: does_rect_fit() selects a
# node based on whether the texture fits in either orientation, but the
# placement code that follows only compares tex.longestEdge against the raw
# node width/height, a narrower check. For this exact sequence of sizes the
# two disagree, and the algorithm used to call exit(1) - killing the whole
# process - instead of raising a catchable error.
UNPLACEABLE_SEQUENCE = [(16, 16), (32, 20), (8, 8), (24, 24), (12, 40), (5, 5), (7, 3)]


def test_pack_places_all_textures_without_overlap():
    packer = TexturePackerRatcliff()
    for i, (w, h) in enumerate(RECT_SIZES):
        packer.add_texture(w, h, "tex%d" % i)

    result = packer.pack_textures(True, True)

    assert len(result) == 3
    width, height, wasted_area = result
    assert width > 0
    assert height > 0
    assert wasted_area >= 0
    assert all(tex.placed for tex in packer.texArr)
    assert_no_overlaps([tex.get_rect() for tex in packer.texArr])


def test_add_texture_tracks_total_area_and_longest_edge():
    packer = TexturePackerRatcliff()
    packer.add_texture(10, 4, "a")
    packer.add_texture(3, 7, "b")
    assert packer.totalArea == (10 * 4) + (3 * 7)
    assert packer.longestEdge == 10


def test_get_texture_returns_named_texture_and_none_for_unknown():
    packer = TexturePackerRatcliff()
    packer.add_texture(10, 10, "a")
    packer.pack_textures(True, True)
    assert packer.get_texture("a").name == "a"
    assert packer.get_texture("does-not-exist") is None


def test_unplaceable_sequence_raises_packer_error_instead_of_exiting():
    packer = TexturePackerRatcliff()
    for i, (w, h) in enumerate(UNPLACEABLE_SEQUENCE):
        packer.add_texture(w, h, "tex%d" % i)

    with pytest.raises(PackerError):
        packer.pack_textures(True, True)
