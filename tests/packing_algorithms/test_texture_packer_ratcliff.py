import random

from packing_algorithms.ratcliff.texture_packer_ratcliff import TexturePackerRatcliff
from packing_algorithms.texture_packer import PackerError

from helpers import assert_no_overlaps

RECT_SIZES = [(10, 10), (10, 10), (8, 8), (16, 4), (4, 16), (5, 5)]

# Used to crash the whole process via exit(1): does_rect_fit() selects a node
# based on whether the texture fits in either orientation, but the placement
# code that used to follow only compared tex.longestEdge against the raw node
# width/height, a narrower check that could disagree. Fixing Texture.flip_dimensions()
# (previously a no-op - see test_texture.py) to actually swap width/height when
# a texture is placed rotated resolved this specific sequence as a side effect.
PREVIOUSLY_CRASHING_SEQUENCE = [(16, 16), (32, 20), (8, 8), (24, 24), (12, 40), (5, 5), (7, 3)]

# Regression for a second bug: the edgeCount==2 "perfect fit" branch placed a
# texture into a free node but never shrank/removed that node afterward
# (unlike the edgeCount 0/1 branches), leaving fully-consumed space marked as
# still free for the next texture to be placed directly on top of.
PERFECT_FIT_OVERLAP_SEQUENCE = [(14, 14), (14, 14), (8, 8)]


def _assert_valid_packing(packer, sizes):
    assert all(tex.placed for tex in packer.texArr)
    for tex, (orig_w, orig_h) in zip(packer.texArr, sizes):
        assert tex.width * tex.height == orig_w * orig_h
    assert_no_overlaps([tex.get_rect() for tex in packer.texArr])


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
    _assert_valid_packing(packer, RECT_SIZES)


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


def test_previously_crashing_sequence_now_packs_cleanly():
    packer = TexturePackerRatcliff()
    for i, (w, h) in enumerate(PREVIOUSLY_CRASHING_SEQUENCE):
        packer.add_texture(w, h, "tex%d" % i)

    packer.pack_textures(True, True)

    _assert_valid_packing(packer, PREVIOUSLY_CRASHING_SEQUENCE)
    assert packer.get_texture("tex4").flipped is True


def test_perfect_fit_node_is_not_reused_for_a_later_texture():
    packer = TexturePackerRatcliff()
    for i, (w, h) in enumerate(PERFECT_FIT_OVERLAP_SEQUENCE):
        packer.add_texture(w, h, "tex%d" % i)

    packer.pack_textures(True, True)

    _assert_valid_packing(packer, PERFECT_FIT_OVERLAP_SEQUENCE)


def test_random_sequences_pack_without_overlap_or_area_corruption():
    # Broad regression guard for the overlap bugs above: packs many random
    # texture-size sequences (some square, so rotation never triggers, and
    # some rectangular, so it does) and checks the core correctness
    # invariant - no overlaps, no corrupted dimensions - holds whenever
    # packing succeeds. Ratcliff's single-pass heuristic can legitimately
    # raise PackerError for some inputs (unlike maxrects, it has no
    # retry-at-a-different-size fallback of its own), so those are skipped
    # rather than treated as failures.
    rng = random.Random(1234)
    packed_count = 0
    for _ in range(200):
        n = rng.randint(1, 12)
        sizes = [(rng.randint(2, 30), rng.randint(2, 30)) for _ in range(n)]

        packer = TexturePackerRatcliff()
        for i, (w, h) in enumerate(sizes):
            packer.add_texture(w, h, "tex%d" % i)
        try:
            packer.pack_textures(True, True)
        except PackerError:
            continue

        packed_count += 1
        _assert_valid_packing(packer, sizes)

    assert packed_count > 100, "expected most random trials to pack successfully"
