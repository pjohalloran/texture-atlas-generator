

class Rect:
    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

    def intersects(self, r):
        if (self.x2 < r.x1 or self.x1 > r.x2 or self.y2 < r.y1 or self.y1 > r.y2):
            return (False)
        return (True)

    def get_width(self):
        return self.x2 - self.x1

    def get_height(self):
        return self.y2 - self.y1

    def get_area(self):
        return self.width * self.height
