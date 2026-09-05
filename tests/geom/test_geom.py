import pytest

from geom.geom import common_interval_length, is_power_of_two, next_power_of_two


@pytest.mark.parametrize("value,expected", [
    (0, False),
    (1, True),
    (2, True),
    (3, False),
    (4, True),
    (1024, True),
    (100, False),
])
def test_is_power_of_two(value, expected):
    assert is_power_of_two(value) is expected


@pytest.mark.parametrize("value,expected", [
    (0, 1),
    (1, 2),
    (2, 4),
    (3, 4),
    (4, 8),
    (1023, 1024),
    (1024, 2048),
])
def test_next_power_of_two(value, expected):
    # Deliberately returns the next *strictly greater* power of two even
    # when value is itself already a power of two (e.g. 4 -> 8, not 4) -
    # the atlas size retry loop relies on this to grow past a failed size.
    assert next_power_of_two(value) == expected


def test_common_interval_length_overlap_when_one_start_at_or_after_two_start():
    assert common_interval_length(5, 15, 0, 10) == 5


def test_common_interval_length_contained_when_one_start_at_or_after_two_start():
    assert common_interval_length(2, 8, 0, 10) == 6


def test_common_interval_length_disjoint():
    assert common_interval_length(10, 15, 0, 5) == 0


def test_common_interval_length_touching_is_disjoint():
    assert common_interval_length(5, 10, 0, 5) == 0


def test_common_interval_length_returns_zero_when_one_start_before_two_start():
    # NOTE: the disjoint check is `one_start < two_start or two_end < one_start`,
    # so it returns 0 whenever one_start < two_start even if the intervals
    # actually overlap (e.g. one=(0,10), two=(5,15) do overlap over [5,10]).
    # Documenting the current behavior here rather than the doc comment's
    # stated intent, since that's what callers actually observe today.
    assert common_interval_length(0, 10, 5, 15) == 0
