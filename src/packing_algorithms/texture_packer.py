from atlas.texture import Texture


class PackerError(Exception):
    pass


class TexturePacker:
    """Base class for texture packing algorithms.

    Subclasses queue up textures via add_texture() and, once pack_textures()
    has run, expose each texture's placement through its Texture.x/y fields
    (or via get_texture()).
    """

    texArr = None
    allow_rotations = False

    def __init__(self):
        self.texArr = []

    def add_texture(self, width, height, name):
        """Queue a texture of the given size for packing."""
        self.texArr.append(Texture(width, height, name))

    def get_texture(self, name):
        """Return the packed Texture with this name, or None if not found.

        The returned Texture's width/height already reflect its placed
        orientation (i.e. already swapped if .flipped is True) - callers
        compositing pixel data should rotate it to match when .flipped.
        """
        for t in self.texArr:
            if (t.name == name):
                return t
        return None

    def get_texture_count(self):
        return len(self.texArr)

    def pack_textures(self, powerOfTwo, oneBorderPixel):
        """Place every queued texture and return (bin_width, bin_height, wasted_area).

        Raises PackerError if the queued textures can't all fit.
        """
        raise NotImplementedError('pack_textures() has not been implemented')
