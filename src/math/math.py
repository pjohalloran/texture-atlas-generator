

def is_power_of_two(number=0):
    return ((number & (number - 1)) == 0) and number != 0
