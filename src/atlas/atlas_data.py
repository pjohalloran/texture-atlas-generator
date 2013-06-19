class AtlasData:
    texture_dict = {}
    border = 1
    width = 0
    height = 0
    color_mode = ""
    file_type = ""

    def __init__(self, width=512, height=512, border=1, color_mode="RGBA", file_type="TGA"):
        self.border = border
        self.width = width
        self.height = height
        self.color_mode = color_mode
        self.file_type = file_type

    def add_texture(self, texture):
        self.texture_dict[texture.name] = texture

    def get_texture_count(self):
        return len(self.texture_dict)
