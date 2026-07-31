def is_power_of_two(number: int) -> bool:
    return ((number & (number - 1)) == 0) and number != 0


def next_power_of_two(number: int) -> int:
    p = 1
    while (p <= number):
        p *= 2
    return p


# Returns 0 if the two intervals i1 and i2 are disjoint, or the length of their overlap otherwise.
def common_interval_length(one_start: int, one_end: int, two_start: int, two_end: int) -> int:
    if one_start < two_start or two_end < one_start:
        return 0
    return min(one_end, two_end) - max(one_start, two_start)
