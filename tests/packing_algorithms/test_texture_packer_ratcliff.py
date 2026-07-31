import random

import pytest

from packing_algorithms.ratcliff.texture_packer_ratcliff import TexturePackerRatcliff
from packing_algorithms.texture_packer import PackerError

from helpers import assert_no_overlaps, assert_within_bounds

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

# Regression for a third bug: pack_textures() pads each Texture's width/height
# by 2px for the one-pixel border, but never updated the Texture's own
# longestEdge (set once at construction from the pre-border size). The
# edgeCount==0 placement branch gates its fit/flip decision on that stale
# value, so it could accept a placement that doesn't actually fit once the
# border is accounted for - silently placing a texture partly outside the
# packed bin, with no exception raised.
BORDER_STALE_LONGEST_EDGE_SEQUENCE = [(14, 18), (44, 38)]


def _assert_valid_packing(packer, sizes, width=None, height=None):
    assert all(tex.placed for tex in packer.texArr)
    for tex, (orig_w, orig_h) in zip(packer.texArr, sizes):
        assert tex.width * tex.height == orig_w * orig_h
    rects = [tex.get_rect() for tex in packer.texArr]
    assert_no_overlaps(rects)
    if width is not None:
        assert_within_bounds(rects, width, height)


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
    _assert_valid_packing(packer, RECT_SIZES, width, height)


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

    width, height, _ = packer.pack_textures(True, True)

    _assert_valid_packing(packer, PREVIOUSLY_CRASHING_SEQUENCE, width, height)
    assert packer.get_texture("tex4").flipped is True


def test_perfect_fit_node_is_not_reused_for_a_later_texture():
    packer = TexturePackerRatcliff()
    for i, (w, h) in enumerate(PERFECT_FIT_OVERLAP_SEQUENCE):
        packer.add_texture(w, h, "tex%d" % i)

    width, height, _ = packer.pack_textures(True, True)

    _assert_valid_packing(packer, PERFECT_FIT_OVERLAP_SEQUENCE, width, height)


def test_border_padding_updates_longest_edge_and_no_longer_places_out_of_bounds():
    # This exact sequence doesn't actually fit once the one-pixel border is
    # correctly accounted for - before the fix, the stale longestEdge made
    # the packer wrongly believe it did, silently placing a texture partly
    # outside the returned bin with no error raised. After the fix it
    # raises PackerError instead: a clean, catchable failure rather than
    # corrupted output.
    packer = TexturePackerRatcliff()
    for i, (w, h) in enumerate(BORDER_STALE_LONGEST_EDGE_SEQUENCE):
        packer.add_texture(w, h, "tex%d" % i)

    with pytest.raises(PackerError):
        packer.pack_textures(True, True)


def test_random_sequences_pack_without_overlap_or_area_corruption():
    # Broad regression guard for the overlap/bounds bugs above: packs many
    # random texture-size sequences (some square, so rotation never
    # triggers, and some rectangular, so it does) and checks the core
    # correctness invariants - no overlaps, no out-of-bounds placement, no
    # corrupted dimensions - hold whenever packing succeeds. Ratcliff's
    # single-pass heuristic can legitimately raise PackerError for some
    # inputs (unlike maxrects, it has no retry-at-a-different-size fallback
    # of its own), so those are skipped rather than treated as failures.
    # 1000 trials rather than a smaller count: the stale-longestEdge bounds
    # bug above needed several hundred trials at this size range to surface,
    # so a thin trial count gives false confidence for this class of bug.
    rng = random.Random(1234)
    packed_count = 0
    for _ in range(1000):
        n = rng.randint(1, 12)
        sizes = [(rng.randint(2, 30), rng.randint(2, 30)) for _ in range(n)]

        packer = TexturePackerRatcliff()
        for i, (w, h) in enumerate(sizes):
            packer.add_texture(w, h, "tex%d" % i)
        try:
            width, height, _ = packer.pack_textures(True, True)
        except PackerError:
            continue

        packed_count += 1
        _assert_valid_packing(packer, sizes, width, height)

    assert packed_count > 500, "expected most random trials to pack successfully"
