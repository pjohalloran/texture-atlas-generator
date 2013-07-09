import sys

from packing_algorithms.texture_packer import TexturePacker
from math.rect import Rect
from math.math import common_interval_length


class FreeRectChoiceHeuristicEnum:
    (RectBestShortSideFit, RectBestLongSideFit, RectBestAreaFit, RectBottomLeftRule, RectContactPointRule) = range(0, 5)


class TexturePackerMaxRects(TexturePacker):
    used_rect_list = None
    free_rect_list = None
    bin_width = 0
    bin_height = 0
    heuristic = FreeRectChoiceHeuristicEnum.RectBestShortSideFit

    def __init__(self, method, width=0, height=0):
        TexturePacker.__init__(self)
        self.used_rect_list = []
        self.free_rect_list = []
        self.bin_width = width
        self.bin_height = height
        self.free_rect_list.append(Rect.InitWithDim(0, 0, self.bin_width, self.bin_height))
        self.heuristic = method

    def get_occupancy(self):
        usedSurfaceArea = 0

        for rect in self.used_rect_list:
            usedSurfaceArea += rect.get_area()

        return float(usedSurfaceArea) / self._get_bin_area()

    def add_texture(self, width, height, name):
        result = None

        if self.heuristic == FreeRectChoiceHeuristicEnum.RectBestShortSideFit:
            result = self._find_position_for_new_node_best_short_side_fit(width, height)
        elif self.heuristic == FreeRectChoiceHeuristicEnum.RectBestLongSideFit:
            result = self._find_position_for_new_node_best_long_side_fit(width, height)
        elif self.heuristic == FreeRectChoiceHeuristicEnum.RectBestAreaFit:
            result = self._find_position_for_new_node_best_area_fit(width, height)
        elif self.heuristic == FreeRectChoiceHeuristicEnum.RectBottomLeftRule:
            result = self._find_position_for_new_node_bottom_left(width, height)
        elif self.heuristic == FreeRectChoiceHeuristicEnum.RectContactPointRule:
            result = self._find_position_for_new_node_contact_point(width, height)
        else:
            raise NotImplementedError('Unknown MaxRects Heuristic encountered')

        if (result[0].get_height() == 0):
            return result[0]

        self._place_rect(result[0])
        return result[0]

    def pack_textures(self, powerOfTwo, oneBorderPixel):
        raise NotImplementedError('pack_textures() has not been implemented')

    def _get_bin_area(self):
        return self.bin_width * self.bin_height

    def _score_rect(self, width, height, method):
        result = None
        score1 = sys.maxint
        score2 = sys.maxint

        if self.heuristic == FreeRectChoiceHeuristicEnum.RectBestShortSideFit:
            result = self._find_position_for_new_node_best_short_side_fit(width, height)
            score1 = result[1]
            score2 = result[2]
        elif self.heuristic == FreeRectChoiceHeuristicEnum.RectBestLongSideFit:
            result = self._find_position_for_new_node_best_long_side_fit(width, height)
            #TODO: Is score order here correct??
            score2 = result[1]
            score1 = result[2]
        elif self.heuristic == FreeRectChoiceHeuristicEnum.RectBestAreaFit:
            result = self._find_position_for_new_node_best_area_fit(width, height)
            score1 = result[1]
            score2 = result[2]
        elif self.heuristic == FreeRectChoiceHeuristicEnum.RectBottomLeftRule:
            result = self._find_position_for_new_node_bottom_left(width, height)
            score1 = result[1]
            score2 = result[2]
        elif self.heuristic == FreeRectChoiceHeuristicEnum.RectContactPointRule:
            result = self._find_position_for_new_node_contact_point(width, height)
            # Reverse since we are minimizing, but for contact point score bigger is better.
            score1 = -result[1]
            score2 = result[2]
        else:
            raise NotImplementedError('Unknown MaxRects Heuristic encountered')

        if result[0].get_height() == 0:
            score1 = sys.maxint
            score2 = sys.maxint

        return (result[0], score1, score2)

    def _place_rect(self, rect):
        count = len(self.free_rect_list)
        i = 0
        while i < count:
            if (self._split_free_node(self.free_rect_list[i], rect)):
                self.free_rect_list.pop(i)
                --i
                --count
            ++i

        self._prune_free_list()
        self.used_rect_list.append(rect)

    def _prune_free_list(self):
        count = len(self.free_rect_list)

        # Go through each pair and remove any rectangle that is redundant.
        i = 0
        while i < count:
            j = i + 1
            while j < count:
                if self.free_rect_list[i].contains(self.free_rect_list[j]):
                    self.free_rect_list.pop(i)
                    --i
                    break
                if self.free_rect_list[j].contains(self.free_rect_list[i]):
                    self.free_rect_list.pop(j)
                    --j
                ++j
            ++i

    def _contact_point_score_node(self, x, y, width, height):
        score = 0

        if x == 0 or x + width == self.bin_width:
            score += height
        if y == 0 or y + height == self.bin_height:
            score += width

        for rect in self.used_rect_list:
            if (rect.x1 == x + width or rect.x2 == x):
                score += common_interval_length(rect.y1, rect.y2, y, y + height)
            if (rect.y1 == y + height or rect.y2 == y):
                score += common_interval_length(rect.x1, rect.x2, x, x + width)

        return score

    def _split_free_node(self, free_rect, used_rect):
        # Test with SAT if the rectangles even intersect.
        if used_rect.x1 >= free_rect.x2 or used_rect.x2 <= free_rect.x1 or used_rect.y1 >= free_rect.y2 or used_rect.y2 <= free_rect.y1:
            return False

        if used_rect.x1 < free_rect.x2 and used_rect.x2 > free_rect.x1:
            # New node at the top side of the used node.
            if used_rect.y1 > free_rect.y1 and used_rect.y1 < free_rect.y2:
                new_rect = Rect.InitWithDim(free_rect.x1, free_rect.y1, free_rect.get_width(), used_rect.y1 - free_rect.y1)
                self.free_rect_list.append(new_rect)

            # New node at the bottom side of the used node.
            if used_rect.y2 < free_rect.y2:
                new_rect = Rect.InitWithDim(free_rect.x1, used_rect.y2, free_rect.get_width(), free_rect.y2 - used_rect.y2)
                self.free_rect_list.append(new_rect)

        if used_rect.y1 < free_rect.y2 and used_rect.y2 > free_rect.y1:
            # New node at the left side of the used node.
            if used_rect.x1 > free_rect.x1 and used_rect.x1 < free_rect.x2:
                new_rect = Rect.InitWithDim(free_rect.x1, free_rect.y1, used_rect.x1 - free_rect.x1, free_rect.get_height())
                self.free_rect_list.append(new_rect)

            # New node at the right side of the used node.
            if used_rect.x2 < free_rect.x2:
                new_rect = Rect.InitWithDim(used_rect.x2, free_rect.y1, free_rect.x2 - used_rect.x2, free_rect.get_height())
                self.free_rect_list.append(new_rect)

        return True

    def _find_position_for_new_node_bottom_left(self, width, height):
        raise NotImplementedError('_find_position_for_new_node_bottom_left() has not been implemented')

    def _find_position_for_new_node_best_short_side_fit(self, width, height):
        raise NotImplementedError('_find_position_for_new_node_best_short_side_fit() has not been implemented')

    def _find_position_for_new_node_best_long_side_fit(self, width, height):
        raise NotImplementedError('_find_position_for_new_node_best_long_side_fit() has not been implemented')

    def _find_position_for_new_node_best_area_fit(self, width, height):
        raise NotImplementedError('_find_position_for_new_node_best_area_fit() has not been implemented')

    def _find_position_for_new_node_contact_point(self, width, height):
        raise NotImplementedError('_find_position_for_new_node_contact_point() has not been implemented')
