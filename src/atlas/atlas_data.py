from typing import Dict

from atlas.texture import Texture


class AtlasData:
    texture_dict: Dict[str, Texture] = None
    border = 1
    width = 0
    height = 0
    color_mode = ""
    file_type = ""
    name = ""

    def __init__(self, name: str, width: int = 512, height: int = 512, border: int = 1, color_mode: str = "RGBA", file_type: str = "tga") -> None:
        self.texture_dict = {}
        self.name = name
        self.border = border
        self.width = width
        self.height = height
        self.color_mode = color_mode
        self.file_type = file_type

    def add_texture(self, texture: Texture) -> None:
        self.texture_dict[texture.name] = texture

    def get_texture_count(self) -> int:
        return len(self.texture_dict)
