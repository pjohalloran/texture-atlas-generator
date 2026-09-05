from atlas.texture import Texture


def test_init_sets_defaults():
    tex = Texture(10, 20, name="foo.png")
    assert tex.width == 10
    assert tex.height == 20
    assert tex.x == 0
    assert tex.y == 0
    assert tex.area == 200
    assert tex.flipped is False
    assert tex.placed is False
    assert tex.longestEdge == 20
    assert tex.name == "foo.png"


def test_place_texture_marks_placed_and_sets_position():
    tex = Texture(10, 20, name="foo.png")
    tex.place_texture(5, 7)
    assert (tex.x, tex.y) == (5, 7)
    assert tex.placed is True
    assert tex.flipped is False


def test_place_texture_with_flipped_true():
    tex = Texture(10, 20, name="foo.png")
    tex.place_texture(5, 7, flipped=True)
    assert tex.flipped is True


def test_flip_dimensions_always_swaps_width_and_height():
    # flip_dimensions() is an unconditional swap - callers decide when to
    # call it (typically alongside setting .flipped = True) rather than it
    # deciding for itself based on .flipped, since callers need it to run
    # before .flipped is necessarily set (e.g. before place_texture()).
    tex = Texture(10, 20, name="foo.png")
    tex.flip_dimensions()
    assert (tex.width, tex.height) == (20, 10)


def test_flip_dimensions_twice_is_a_round_trip():
    tex = Texture(10, 20, name="foo.png")
    tex.flip_dimensions()
    tex.flip_dimensions()
    assert (tex.width, tex.height) == (10, 20)


def test_to_dict_contains_expected_fields():
    tex = Texture(10, 20, name="foo.png")
    tex.place_texture(3, 4, flipped=True)
    result = tex.to_dict()
    assert result == {
        'width': 10,
        'height': 20,
        'x': 3,
        'y': 4,
        'flipped': True,
        'name': 'foo.png',
    }


def test_get_rect_matches_position_and_size():
    tex = Texture(10, 20, name="foo.png")
    tex.place_texture(3, 4)
    rect = tex.get_rect()
    assert (rect.x1, rect.y1, rect.x2, rect.y2) == (3, 4, 13, 24)
