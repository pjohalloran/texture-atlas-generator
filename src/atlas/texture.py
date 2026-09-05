from typing import Any, Dict

from geom.rect import Rect


class Texture:
    def __init__(self, width: int, height: int, name: str = "") -> None:
        self.width = width
        self.height = height
        self.x = 0
        self.y = 0
        self.area = width * height
        self.flipped = False
        self.placed = False
        self.longestEdge = width if width > height else height
        self.name = name

    def place_texture(self, x: int, y: int, flipped: bool = False) -> None:
        self.x = x
        self.y = y
        self.flipped = flipped
        self.placed = True

    def flip_dimensions(self) -> None:
        """Swap width and height in place. Callers are responsible for also
        setting self.flipped to record that this texture's pixel content
        needs a matching 90-degree rotation before it's composited.
        """
        self.width, self.height = self.height, self.width

    def to_dict(self) -> Dict[str, Any]:
        tex_dict: Dict[str, Any] = {}
        tex_dict['width'] = self.width
        tex_dict['height'] = self.height
        tex_dict['x'] = self.x
        tex_dict['y'] = self.y
        tex_dict['flipped'] = self.flipped
        tex_dict['name'] = self.name
        return tex_dict

    def get_rect(self) -> Rect:
        return Rect(self.x, self.y, self.x + self.width, self.y + self.height)
