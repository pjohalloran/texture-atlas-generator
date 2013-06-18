from util.node import Node
from util.texture import Texture
from math.math import next_power_of_two


class TexturePacker:
    def __init__(self):
        self.reset()

    def reset(self):
        self.texArr = []
        self.freeArr = []
        self.longestEdge = 0
        self.totalArea = 0

    def get_texture_count(self):
        return len(self.texArr)

    def add_texture(self, width, height, name=""):
        self.texArr.append(Texture(width, height, name))
        self.longestEdge = width if (width > self.longestEdge) else self.longestEdge
        self.longestEdge = height if (height > self.longestEdge) else self.longestEdge
        self.totalArea += width * height

    def add_node(self, x, y, width, height):
        self.freeArr.append(Node(x, y, width, height))

    def get_texture_by_name(self, name=""):
        if (len(name) == 0):
            return None

        index = 0
        tex = None
        for t in self.texArr:
            if (t.name == name):
                tex = t
                if (tex.flipped):
                    tex.flip_dimensions()
                return tex
            index += 1

        return tex

    def get_texture(self, index):
        if (index < 0 or index >= len(self.texArr)):
            return None

        tex = self.texArr[index]
        if (tex.flipped):
            tex.flip_dimensions()
            return True

        return False

    def merge_nodes(self):
        for f in self.freeArr:
            fIdx = 0
            for s in self.freeArr:
                if (f != s):
                    if (f.merge(s)):
                        self.freeArr[fIdx] = f
                        return True
            fIdx += 1

        return False

    def validate(self):
        for f in self.freeArr:
            for c in self.freeArr:
                if (f != c):
                    f.validate(c)

    def pack_textures(self, forcePowerOfTwo, onePixelBorder):
        # 0 = width
        # 1 = height
        # 3 = returnValue
        returnList = []

        if (onePixelBorder):
            i = 0
            for t in self.texArr:
                t.width += 2
                t.height += 2
                self.texArr[i] = t
                i += 1
            self.longestEdge += 2

        if (forcePowerOfTwo):
            self.longestEdge = next_power_of_two(self.longestEdge)

        width = self.longestEdge
        count = self.totalArea / (self.longestEdge * self.longestEdge)
        height = (count + 2) * self.longestEdge

        self.add_node(0, 0, width, height)

        # We must place_texture each texture
        loopI = 0
        while (loopI < len(self.texArr)):
            index = 0
            longestEdge = 0
            mostArea = 0

            # We first search for the texture with the longest edge, placing it first.
            # And the most area...
            j = 0
            for texture in self.texArr:
                #print "Checking texture ", tmpTex.GetName()
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
            #print "Going to try and place_texture ", tex.GetName()

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
            if(bestFitNode.x == 0 and bestFitNode.y == 0 and bestFitNode.get_rect().get_width() == 0 and bestFitNode.get_rect().get_height() == 0):
                print "TexturePacker::pack_textures() BestFit node not found!!"
                exit(1)

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
                        print("TexturePacker::PackTexture() ERROR - Current textures longest edge is less than the BestFitNodes Height!!!")
                        exit(1)

                    if (tex.height < tex.width):
                        tex.flip_dimensions()
                        tex.flipped = True

                    tex.place_texture(bestFitNode.x, bestFitNode.y, tex.flipped)
                    self.add_node(bestFitNode.x, bestFitNode.y + tex.height, bestFitNode.get_rect().width, bestFitNode.get_rect().height - tex.height)
                    bestFitNode.x += tex.width
                    bestFitNode.width -= tex.width
                    bestFitNode.height = tex.height
                    self.validate()
            elif(edgeCount == 1):
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
                    tex.place_texture(bestFitNode.x, bestFitNode.y, True)
                    bestFitNode.x += tex.height
                    bestFitNode.width -= tex.height
                    self.validate()
                elif (tex.height == bestFitNode.get_rect().get_width()):
                    tex.place_texture(bestFitNode.x, bestFitNode.y, True)
                    bestFitNode.y += tex.width
                    bestFitNode.height -= tex.width
                    self.validate()
            elif(edgeCount == 2):
                flipped = tex.width != bestFitNode.get_rect().get_width() or tex.height != bestFitNode.get_rect().get_height()
                tex.place_texture(bestFitNode.x, bestFitNode.y, flipped)
                if (previousBestFitNodeIdx >= 0):
                    previousBestFitNodeIdx = index
                self.validate()

            # Save latest version of texture and Node back into lists since python is pass by value
            self.freeArr[nodeIndex] = bestFitNode
            self.texArr[index] = tex

            loopI += 1

        while (self.merge_nodes()):
            print "Merging nodes"

        index = 0
        height = 0
        for t in self.texArr:
            if (onePixelBorder):
                t.width -= 2
                t.height -= 2
                t.x += 1
                t.y += 1
                self.texArr[index] = t

            y = 0
            if (t.flipped):
                y = t.y + t.width
            else:
                y = t.y + t.height

            if (y > height):
                height = y

            index += 1

        if (forcePowerOfTwo):
            height = next_power_of_two(height)

        returnList.append(width)
        returnList.append(height)
        returnList.append((width * height) - self.totalArea)
        return (returnList)
