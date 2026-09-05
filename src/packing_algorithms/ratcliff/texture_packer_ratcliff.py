#
# This packing algorithm is a python
# implementation of the C TexturePacker algorithm
# (c) 2009 by John W. Ratcliff.
#

import logging
from typing import List, Tuple

from packing_algorithms.ratcliff.node import Node
from geom.geom import next_power_of_two
from packing_algorithms.texture_packer import PackerError
from packing_algorithms.texture_packer import TexturePacker

logger = logging.getLogger(__name__)


class TexturePackerRatcliff(TexturePacker):
    freeArr: List[Node] = None
    longestEdge = 0
    totalArea = 0

    def __init__(self) -> None:
        TexturePacker.__init__(self)
        self.freeArr = []
        self.longestEdge = 0
        self.totalArea = 0

    def add_texture(self, width: int, height: int, name: str = "") -> None:
        TexturePacker.add_texture(self, width, height, name)
        self.longestEdge = width if (width > self.longestEdge) else self.longestEdge
        self.longestEdge = height if (height > self.longestEdge) else self.longestEdge
        self.totalArea += width * height

    def add_node(self, x: int, y: int, width: int, height: int) -> None:
        self.freeArr.append(Node(x, y, width, height))

    def merge_nodes(self) -> bool:
        for f in self.freeArr:
            fIdx = 0
            for s in self.freeArr:
                if (f != s):
                    if (f.merge(s)):
                        self.freeArr[fIdx] = f
                        return True
            fIdx += 1

        return False

    def validate(self) -> None:
        for f in self.freeArr:
            for c in self.freeArr:
                if (f != c):
                    f.validate(c)

    def pack_textures(self, forcePowerOfTwo: bool, onePixelBorder: bool) -> Tuple[int, int, int]:
        if (onePixelBorder):
            i = 0
            for t in self.texArr:
                t.width += 2
                t.height += 2
                # Texture.longestEdge is computed once at construction from
                # the pre-border size; without updating it here it stays 2px
                # too small, and the edgeCount==0 placement branch below
                # gates its fit/flip decision on this value - a stale value
                # can wrongly pass a fit check for the bordered size, placing
                # the texture partially outside the packed bin.
                t.longestEdge += 2
                self.texArr[i] = t
                i += 1
            self.longestEdge += 2

        if (forcePowerOfTwo):
            self.longestEdge = next_power_of_two(self.longestEdge)

        width = self.longestEdge
        count = self.totalArea // (self.longestEdge * self.longestEdge)
        height = (count + 2) * self.longestEdge

        self.add_node(0, 0, width, height)

        # We must place_texture each texture
        loopI = 0
        while (loopI < self.get_texture_count()):
            index = 0
            longestEdge = 0
            mostArea = 0

            # We first search for the texture with the longest edge, placing it first.
            # And the most area...
            j = 0
            for texture in self.texArr:
                if (not texture.placed):
                    if (texture.longestEdge > longestEdge):
                        mostArea = texture.area
                        longestEdge = texture.longestEdge
                        index = j
                    elif (texture.longestEdge == longestEdge):
                        if (texture.area > mostArea):
                            mostArea = texture.area
                            index = j
                j += 1

            # For the texture with the longest edge we place_texture it according to this criteria.
            #   (1) If it is a perfect match, we always accept it as it causes the least amount of fragmentation.
            #   (2) A match of one edge with the minimum area left over after the split.
            #   (3) No edges match, so look for the node which leaves the least amount of area left over after the split.
            tex = self.texArr[index]

            leastY = 0x7FFFFFFF
            leastX = 0x7FFFFFFF

            nodeIndex = 0
            idx = 0
            previousBestFitNodeIdx = 0
            bestFitNode = Node(0, 0, 0, 0)
            previousNodeIdx = 0
            edgeCount = 0

            # Walk the singly linked list of free nodes
            # see if it will fit into any currently free space
            for currNode in self.freeArr:
                resultdoes_rect_fitArr = currNode.does_rect_fit(tex.get_rect().get_width(), tex.get_rect().get_height())
                ec = resultdoes_rect_fitArr[1]

                # see if the texture will fit into this slot, and if so how many edges does it share.
                if (resultdoes_rect_fitArr[0] is True):
                    if (ec == 2):
                        previousBestFitNodeIdx = previousNodeIdx
                        bestFitNode = currNode
                        nodeIndex = idx
                        edgeCount = ec
                        break

                    if (currNode.y < leastY):
                        leastY = currNode.y
                        leastX = currNode.x
                        previousBestFitNodeIdx = previousNodeIdx
                        bestFitNode = currNode
                        nodeIndex = idx
                        edgeCount = ec
                    elif (currNode.y == leastY and currNode.x < leastX):
                        leastX = currNode.x
                        previousBestFitNodeIdx = previousNodeIdx
                        bestFitNode = currNode
                        nodeIndex = idx
                        edgeCount = ec

                previousNodeIdx = idx
                idx += 1

            # we should always find a fit location!
            if (bestFitNode.x == 0 and bestFitNode.y == 0 and bestFitNode.get_rect().get_width() == 0 and bestFitNode.get_rect().get_height() == 0):
                raise PackerError('BestFit node not found for %s' % (tex.name))

            self.validate()

            if (edgeCount == 0):
                if (tex.longestEdge <= bestFitNode.get_rect().get_width()):
                    if (tex.height > tex.width):
                        tex.flip_dimensions()
                        tex.flipped = True

                    tex.place_texture(bestFitNode.x, bestFitNode.y, tex.flipped)

                    self.add_node(bestFitNode.x, bestFitNode.y + tex.height, bestFitNode.get_rect().get_width(), bestFitNode.get_rect().get_height() - tex.height)

                    bestFitNode.x += tex.width
                    bestFitNode.width -= tex.width
                    bestFitNode.height = tex.height
                    self.validate()
                else:
                    if (tex.longestEdge <= bestFitNode.height):
                        raise PackerError('%s longest edge does not fit the BestFit node height' % (tex.name))

                    if (tex.height < tex.width):
                        tex.flip_dimensions()
                        tex.flipped = True

                    tex.place_texture(bestFitNode.x, bestFitNode.y, tex.flipped)
                    self.add_node(bestFitNode.x, bestFitNode.y + tex.height, bestFitNode.get_rect().width, bestFitNode.get_rect().height - tex.height)
                    bestFitNode.x += tex.width
                    bestFitNode.width -= tex.width
                    bestFitNode.height = tex.height
                    self.validate()
            elif (edgeCount == 1):
                if (tex.width == bestFitNode.get_rect().get_width()):
                    tex.place_texture(bestFitNode.x, bestFitNode.y, False)
                    bestFitNode.y += tex.height
                    bestFitNode.height -= tex.height
                    self.validate()
                elif (tex.height == bestFitNode.get_rect().get_height()):
                    tex.place_texture(bestFitNode.x, bestFitNode.y, False)
                    bestFitNode.x += tex.width
                    bestFitNode.width -= tex.width
                    self.validate()
                elif (tex.width == bestFitNode.get_rect().get_height()):
                    tex.flip_dimensions()
                    tex.place_texture(bestFitNode.x, bestFitNode.y, True)
                    bestFitNode.x += tex.width
                    bestFitNode.width -= tex.width
                    self.validate()
                elif (tex.height == bestFitNode.get_rect().get_width()):
                    tex.flip_dimensions()
                    tex.place_texture(bestFitNode.x, bestFitNode.y, True)
                    bestFitNode.y += tex.height
                    bestFitNode.height -= tex.height
                    self.validate()
            elif (edgeCount == 2):
                flipped = tex.width != bestFitNode.get_rect().get_width() or tex.height != bestFitNode.get_rect().get_height()
                if flipped:
                    tex.flip_dimensions()
                tex.place_texture(bestFitNode.x, bestFitNode.y, flipped)
                if (previousBestFitNodeIdx >= 0):
                    previousBestFitNodeIdx = index
                # A perfect (both-edges-matched) fit consumes the entire
                # free node, unlike the edgeCount 0/1 cases which carve a
                # smaller node out of a larger one. Shrink it to zero area
                # so it's never selected as free space for a later texture.
                bestFitNode.width = 0
                bestFitNode.height = 0
                self.validate()

            # Save latest version of texture and Node back into lists since python is pass by value
            self.freeArr[nodeIndex] = bestFitNode
            self.texArr[index] = tex

            loopI += 1

        while (self.merge_nodes()):
            logger.debug("Merging nodes")

        index = 0
        height = 0
        for t in self.texArr:
            if (onePixelBorder):
                t.width -= 2
                t.height -= 2
                t.x += 1
                t.y += 1
                self.texArr[index] = t

            y = t.y + t.height

            if (y > height):
                height = y

            index += 1

        if (forcePowerOfTwo):
            height = next_power_of_two(height)

        return (width, height, (width * height) - self.totalArea)
