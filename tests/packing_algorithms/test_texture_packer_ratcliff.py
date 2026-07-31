from packing_algorithms.ratcliff.texture_packer_ratcliff import TexturePackerRatcliff

from helpers import assert_no_overlaps

RECT_SIZES = [(10, 10), (10, 10), (8, 8), (16, 4), (4, 16), (5, 5)]


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
