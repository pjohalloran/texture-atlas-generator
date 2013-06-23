class AtlasData:
    texture_dict = None
    border = 1
    width = 0
    height = 0
    color_mode = ""
    file_type = ""
    name = ""

    def __init__(self, name, width=512, height=512, border=1, color_mode="RGBA", file_type="tga"):
        self.texture_dict = {}
        self.name = name
        self.border = border
        self.width = width
        self.height = height
        self.color_mode = color_mode
        self.file_type = file_type

    def add_texture(self, texture):
        self.texture_dict[texture.name] = texture

    def get_texture_count(self):
        return len(self.texture_dict)
