import sys

from packing_algorithms.texture_packer import TexturePacker
from packing_algorithms.texture_packer import PackerError
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
        TexturePacker.add_texture(self, width, height, name)
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

        if result[0] is None:
            raise PackerError('Failed to fit in %s' % (name))

        if (result[0].get_height() == 0):
            return result[0]

        if (result[0].y2) > self.bin_height:
            raise PackerError('Can not fit in vertically %s' % (str(result[0])))

        if (result[0].x2) > self.bin_width:
            raise PackerError('Can not fit in horizontally %s' % (str(result[0])))

        self._place_rect(result[0])
        return result[0]

    def pack_textures(self, powerOfTwo, oneBorderPixel):
        i = 0

        for rect in self.used_rect_list:
            self.texArr[i].place_texture(rect.x1, rect.y1)
            i += 1

        return (self.bin_width, self.bin_height, 0)

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
                i -= 1
                count -= 1
            i += 1

        self._prune_free_list()
        self.used_rect_list.append(rect)

    def _prune_free_list(self):
        # Go through each pair and remove any rectangle that is redundant.
        i = 0
        while i < len(self.free_rect_list):
            j = i + 1
            while j < len(self.free_rect_list):
                if self.free_rect_list[i].contains(self.free_rect_list[j]):
                    self.free_rect_list.pop(i)
                    i -= 1
                    break
                if self.free_rect_list[j].contains(self.free_rect_list[i]):
                    self.free_rect_list.pop(j)
                    j -= 1
                j += 1
            i += 1

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
        bestRect = None
        bestX = sys.maxint
        bestY = sys.maxint

        for rect in self.free_rect_list:
            # Try to place the rectangle in upright (non-flipped) orientation.
            if rect.get_width() >= width and rect.get_height() >= height:
                topSideY = rect.y1 + height
                if topSideY < bestY and (topSideY == bestY and rect.x1 < bestX):
                    bestRect = Rect.InitWithDim(rect.x1, rect.y1, width, height)
                    bestY = topSideY
                    bestX = rect.x1

            if self.allow_rotations and rect.get_width() >= height and rect.get_height() >= width:
                topSideY = rect.y1 + width
                if topSideY < bestY or (topSideY == bestY and rect.x1 < bestX):
                    bestRect = Rect.InitWithDim(rect.x1, rect.y1, height, width)
                    bestY = topSideY
                    bestX = rect.x1

        return (bestRect, bestX, bestY)

    def _find_position_for_new_node_best_short_side_fit(self, width, height):
        bestNode = None
        bestShortSideFit = sys.maxint
        bestLongSideFit = sys.maxint

        for rect in self.free_rect_list:
            # Try to place the rectangle in upright (non-flipped) orientation.
            if rect.get_width() >= width and rect.get_height() >= height:
                leftoverHoriz = abs(rect.get_width() - width)
                leftoverVert = abs(rect.get_height() - height)
                shortSideFit = min(leftoverHoriz, leftoverVert)
                longSideFit = max(leftoverHoriz, leftoverVert)

                if shortSideFit < bestShortSideFit or (shortSideFit == bestShortSideFit and longSideFit < bestLongSideFit):
                    bestNode = Rect.InitWithDim(rect.x1, rect.y1, width, height)
                    bestShortSideFit = shortSideFit
                    bestLongSideFit = longSideFit

            if self.allow_rotations and rect.get_width() >= height and rect.get_height() >= width:
                flippedLeftoverHoriz = abs(rect.get_width() - height)
                flippedLeftoverVert = abs(rect.get_height() - width)
                flippedShortSideFit = min(flippedLeftoverHoriz, flippedLeftoverVert)
                flippedLongSideFit = max(flippedLeftoverHoriz, flippedLeftoverVert)

                if flippedShortSideFit < bestShortSideFit or (flippedShortSideFit == bestShortSideFit and flippedLongSideFit < bestLongSideFit):
                    bestNode = Rect.InitWithDim(rect.x1, rect.y1, height, width)
                    bestShortSideFit = flippedShortSideFit
                    bestLongSideFit = flippedLongSideFit

        return (bestNode, bestShortSideFit, bestLongSideFit)

    def _find_position_for_new_node_best_long_side_fit(self, width, height):
        bestNode = None
        bestLongSideFit = sys.maxint
        bestShortSideFit = sys.maxint

        for rect in self.free_rect_list:
            # Try to place the rectangle in upright (non-flipped) orientation.
            if rect.get_width() >= width and rect.get_height() >= height:
                leftoverHoriz = abs(rect.get_width() - width)
                leftoverVert = abs(rect.get_height() - height)
                shortSideFit = min(leftoverHoriz, leftoverVert)
                longSideFit = max(leftoverHoriz, leftoverVert)

                if longSideFit < bestLongSideFit or (longSideFit == bestLongSideFit and shortSideFit < bestShortSideFit):
                    bestNode = Rect.InitWithDim(rect.x1, rect.y1, width, height)
                    bestShortSideFit = shortSideFit
                    bestLongSideFit = longSideFit

            if self.allow_rotations and rect.get_width() >= height and rect.get_height() >= width:
                leftoverHoriz = abs(rect.get_width() - height)
                leftoverVert = abs(rect.get_height() - width)
                shortSideFit = min(leftoverHoriz, leftoverVert)
                longSideFit = max(leftoverHoriz, leftoverVert)

                if longSideFit < bestLongSideFit or (longSideFit == bestLongSideFit and shortSideFit < bestShortSideFit):
                    bestNode = Rect.InitWithDim(rect.x1, rect.y1, height, width)
                    bestShortSideFit = shortSideFit
                    bestLongSideFit = longSideFit

        return (bestNode, bestShortSideFit, bestLongSideFit)

    def _find_position_for_new_node_best_area_fit(self, width, height):
        bestNode = None
        bestAreaFit = sys.maxint
        bestShortSideFit = sys.maxint

        for rect in self.free_rect_list:
            areaFit = rect.get_area() - (width * height)

            # Try to place the rectangle in upright (non-flipped) orientation.
            if rect.get_width() >= width and rect.get_height() >= height:
                leftoverHoriz = abs(rect.get_width() - width)
                leftoverVert = abs(rect.get_height() - height)
                shortSideFit = min(leftoverHoriz, leftoverVert)

                if areaFit < bestAreaFit or (areaFit == bestAreaFit and shortSideFit < bestShortSideFit):
                    bestNode = Rect.InitWithDim(rect.x1, rect.y1, width, height)
                    bestShortSideFit = shortSideFit
                    bestAreaFit = areaFit

            if self.allow_rotations and rect.get_width() >= height and rect.get_height() >= width:
                leftoverHoriz = abs(rect.get_width() - height)
                leftoverVert = abs(rect.get_height() - width)
                shortSideFit = min(leftoverHoriz, leftoverVert)

                if areaFit < bestAreaFit or (areaFit == bestAreaFit and shortSideFit < bestShortSideFit):
                    bestNode = Rect.InitWithDim(rect.x1, rect.y1, height, width)
                    bestShortSideFit = shortSideFit
                    bestAreaFit = areaFit

        return (bestNode, bestAreaFit, bestShortSideFit)

    def _find_position_for_new_node_contact_point(self, width, height):
        bestNode = None
        bestContactScore = -1

        for rect in self.free_rect_list:
            # Try to place the rectangle in upright (non-flipped) orientation.
            if (rect.get_width() >= width and rect.get_height() >= height):
                score = self._contact_point_score_node(rect.x1, rect.y1, width, height)
                if score > bestContactScore:
                    bestNode = Rect.InitWithDim(rect.x1, rect.y1, width, height)
                    bestContactScore = score

            if self.allow_rotations and (rect.get_width() >= height and rect.get_height() >= width):
                score = self._contact_point_score_node(rect.x1, rect.y1, height, width)
                if score > bestContactScore:
                    bestNode = Rect.InitWithDim(rect.x1, rect.y1, height, width)
                    bestContactScore = score

        return (bestNode, bestContactScore)
