from packing_algorithms.texture_packer import TexturePacker


class TexturePackerMaxRects(TexturePacker):
    texArr = None

    def pack_textures(self, powerOfTwo, oneBorderPixel):
        raise NotImplementedError('pack_textures() has not been implemented')
