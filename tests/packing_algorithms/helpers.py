def rects_overlap(a, b):
    return not (a.x2 <= b.x1 or a.x1 >= b.x2 or a.y2 <= b.y1 or a.y1 >= b.y2)


def assert_no_overlaps(rects):
    for i in range(len(rects)):
        for j in range(i + 1, len(rects)):
            assert not rects_overlap(rects[i], rects[j]), \
                "Rects overlap: %s and %s" % (vars(rects[i]), vars(rects[j]))


def assert_within_bounds(rects, width, height):
    for r in rects:
        assert r.x1 >= 0 and r.y1 >= 0 and r.x2 <= width and r.y2 <= height, \
            "Rect out of bounds (%dx%d bin): %s" % (width, height, vars(r))
