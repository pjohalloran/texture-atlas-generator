from geom.rect import Rect


def test_contains_true_when_fully_inside():
    outer = Rect(0, 0, 10, 10)
    inner = Rect(2, 2, 5, 5)
    assert outer.contains(inner) is True


def test_contains_false_when_self_is_smaller():
    small = Rect(2, 2, 5, 5)
    big = Rect(0, 0, 10, 10)
    assert small.contains(big) is False


def test_contains_true_on_exact_equal_bounds():
    a = Rect(0, 0, 10, 10)
    b = Rect(0, 0, 10, 10)
    assert a.contains(b) is True


def test_contains_false_when_only_partially_overlapping():
    a = Rect(0, 0, 10, 10)
    b = Rect(5, 5, 15, 15)
    assert a.contains(b) is False


def test_intersects_true_for_overlapping_rects():
    a = Rect(0, 0, 10, 10)
    b = Rect(5, 5, 15, 15)
    assert a.intersects(b) is True


def test_intersects_true_for_touching_edges():
    a = Rect(0, 0, 10, 10)
    b = Rect(10, 0, 20, 10)
    assert a.intersects(b) is True


def test_intersects_false_for_disjoint_rects():
    a = Rect(0, 0, 10, 10)
    b = Rect(20, 20, 30, 30)
    assert a.intersects(b) is False


def test_init_with_dim_and_dimension_getters():
    r = Rect.InitWithDim(3, 4, 5, 6)
    assert (r.x1, r.y1, r.x2, r.y2) == (3, 4, 8, 10)
    assert r.get_width() == 5
    assert r.get_height() == 6
    assert r.get_area() == 30
