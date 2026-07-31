from packing_algorithms.ratcliff.node import Node


def test_does_rect_fit_true_when_smaller():
    node = Node(0, 0, 20, 10)
    fits, edge_count = node.does_rect_fit(7, 3)
    assert fits is True
    assert edge_count == 0


def test_does_rect_fit_true_when_fits_only_rotated():
    node = Node(0, 0, 20, 10)
    fits, edge_count = node.does_rect_fit(10, 20)
    assert fits is True


def test_does_rect_fit_false_when_too_big_in_both_orientations():
    node = Node(0, 0, 5, 5)
    fits, edge_count = node.does_rect_fit(10, 20)
    assert fits is False


def test_does_rect_fit_edge_count_for_perfect_match():
    node = Node(0, 0, 20, 10)
    fits, edge_count = node.does_rect_fit(20, 10)
    assert fits is True
    assert edge_count == 2


def test_merge_stacks_node_directly_above_and_returns_true():
    # Regression test: merge() used to access node.get_rect().height, but
    # Rect has no .height attribute (only get_height()), so any merge that
    # actually matched one of these adjacency conditions raised
    # AttributeError instead of merging. Node already stores width/height
    # directly, so node.height/node.width is both correct and simpler.
    self_node = Node(0, 10, 5, 5)
    other = Node(0, 4, 5, 5)

    merged = self_node.merge(other)

    assert merged is True
    assert self_node.y == other.y
    assert self_node.height == 5 + other.height


def test_merge_extends_node_downward_and_returns_true():
    self_node = Node(0, 4, 5, 5)
    other = Node(0, 10, 5, 5)

    merged = self_node.merge(other)

    assert merged is True
    assert self_node.height == 5 + other.height


def test_merge_extends_node_leftward_and_returns_true():
    self_node = Node(10, 0, 5, 5)
    other = Node(4, 0, 5, 5)

    merged = self_node.merge(other)

    assert merged is True
    assert self_node.x == other.x
    assert self_node.width == 5 + other.width


def test_merge_extends_node_rightward_and_returns_true():
    self_node = Node(4, 0, 5, 5)
    other = Node(10, 0, 5, 5)

    merged = self_node.merge(other)

    assert merged is True
    assert self_node.width == 5 + other.width


def test_merge_returns_false_for_unrelated_nodes():
    self_node = Node(0, 0, 5, 5)
    other = Node(100, 100, 5, 5)

    merged = self_node.merge(other)

    assert merged is False
    assert (self_node.x, self_node.y, self_node.width, self_node.height) == (0, 0, 5, 5)
