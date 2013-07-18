from atlas.texture import Texture


class PackerError(Exception):
    pass


class TexturePacker:
    texArr = None
    allow_rotations = False

    def __init__(self):
        self.texArr = []

    def add_texture(self, width, height, name):
        self.texArr.append(Texture(width, height, name))

    def get_texture(self, name):
        tex = None
        for t in self.texArr:
            if (t.name == name):
                tex = t
                if (tex.flipped):
                    tex.flip_dimensions()
                return tex
        return None

    def get_texture_count(self):
        return len(self.texArr)

    def pack_textures(self, powerOfTwo, oneBorderPixel):
        raise NotImplementedError('pack_textures() has not been implemented')
