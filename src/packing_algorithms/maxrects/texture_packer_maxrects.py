from packing_algorithms.texture_packer import TexturePacker


class FreeRectChoiceHeuristicEnum:
    (RectBestShortSideFit, RectBestLongSideFit, RectBestAreaFit, RectBottomLeftRule, RectContactPointRule) = range(0, 5)


class TexturePackerMaxRects(TexturePacker):
    usedRectList = None
    freeRectList = None
    binWidth = 0
    binHeight = 0

    def __init__(self, width=0, height=0):
        TexturePacker.__init__(self)
        self.usedRectList = []
        self.freeRectList = []
        self.binWidth = width
        self.binHeight = height

    def get_occupancy(self):
        raise NotImplementedError('get_occupancy() has not been implemented')

    def pack_textures(self, powerOfTwo, oneBorderPixel):
        raise NotImplementedError('pack_textures() has not been implemented')
