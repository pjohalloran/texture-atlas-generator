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

    def _score_rect(self, width, height, method, score1, score2):
        raise NotImplementedError('_score_rect() has not been implemented')

    def _place_rect(self, rect):
        raise NotImplementedError('_place_rect() has not been implemented')

    def _contact_point_score_node(self, x, y, width, height):
        raise NotImplementedError('_contact_point_score_node() has not been implemented')

    def _find_position_for_new_node_bottom_left(self, width, height, bestY, bestX):
        raise NotImplementedError('_find_position_for_new_node_bottom_left() has not been implemented')

    def _find_position_for_new_node_best_short_side_fit(self, width, height, bestShortSideFit, bestLongSideFit):
        raise NotImplementedError('_find_position_for_new_node_best_short_side_fit() has not been implemented')

    def _find_position_for_new_node_best_long_side_fit(self, width, height, bestShortSideFit, bestLongSideFit):
        raise NotImplementedError('_find_position_for_new_node_best_long_side_fit() has not been implemented')

    def _find_position_for_new_node_best_area_fit(self, width, height, bestAreaFit, bestShortSideFit):
        raise NotImplementedError('_find_position_for_new_node_best_area_fit() has not been implemented')

    def _find_position_for_new_node_contact_point(self, width, height, contactScore):
        raise NotImplementedError('_find_position_for_new_node_contact_point() has not been implemented')

    def _split_free_node(self, freeNode, usedNode):
        raise NotImplementedError('_split_free_node() has not been implemented')

    def _prune_free_list(self):
        raise NotImplementedError('_prune_free_list() has not been implemented')
