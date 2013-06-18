from math.rect import Rect


class Texture:
    def __init__(self, width, height, name=""):
        self.width = width
        self.height = height
        self.x = 0
        self.y = 0
        self.area = width * height
        self.flipped = False
        self.placed = False
        self.longestEdge = width if width > height else height
        self.name = name

    def place_texture(self, x, y, flipped=False):
        self.x = x
        self.y = y
        self.flipped = flipped
        self.placed = True
        print "Placing ", self.name, "at ", self.x, self.y

    def flip_dimensions(self):
        if(self.flipped):
            tmp = self.width
            self.width = self.height
            self.height = tmp

    def get_rect(self):
        return Rect(self.x, self.y, self.x + self.width, self.y + self.height)
