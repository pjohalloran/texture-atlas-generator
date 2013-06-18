

def is_power_of_two(number):
    return ((number & (number - 1)) == 0) and number != 0


def next_power_of_two(number):
    p = 1
    while (p < number):
        p *= 2
    return p
