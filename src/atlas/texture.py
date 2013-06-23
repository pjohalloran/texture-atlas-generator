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

    def flip_dimensions(self):
        if(self.flipped):
            tmp = self.width
            self.width = self.height
            self.height = tmp

    def to_dict(self):
        tex_dict = {}
        tex_dict['width'] = self.width
        tex_dict['height'] = self.height
        tex_dict['x'] = self.x
        tex_dict['y'] = self.y
        tex_dict['flipped'] = self.flipped
        tex_dict['name'] = self.name
        return tex_dict

    def get_rect(self):
        return Rect(self.x, self.y, self.x + self.width, self.y + self.height)
