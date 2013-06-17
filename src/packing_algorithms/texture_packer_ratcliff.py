from util.node import Node
from util.texture import Texture


class TexturePacker:
    def __init__(self):
        self.Reset()

    def Print(self):
        print "List of textures:"
        for tex in self.mTextureArr:
            tex.Print()
        for node in self.mFreeArr:
            node.Print()
        print "Area = ", self.mTotalArea, "longest edge = ", self.mLongestEdge

    def Reset(self):
        self.mTextureArr = []
        self.mFreeArr = []
        self.mLongestEdge = 0
        self.mTotalArea = 0

    def GetNumberTextures(self):
        return (len(self.mTextureArr))

    def AddTexture(self, width, height, name=""):
        self.mTextureArr.append(Texture(width, height, name))
        self.mLongestEdge = width if (width > self.mLongestEdge) else self.mLongestEdge
        self.mLongestEdge = height if (height > self.mLongestEdge) else self.mLongestEdge
        self.mTotalArea += width * height

    def AddNode(self, x, y, width, height):
        self.mFreeArr.append(Node(x, y, width, height))

    def GetNextPowerOfTwo(self, num):
        p = 1
        while (p < num):
            p *= 2
        return (p)

    def GetTextureByName(self, name=""):
        if (len(name) == 0):
            return (None)

        index = 0
        tex = None
        for t in self.mTextureArr:
            if (t.GetName() == name):
                tex = t
                if(tex.IsFlipped()):
                    tex.FlipDimensions()
                return (tex)
            index += 1

        return (tex)

    def GetTexture(self, index):
        if(index < 0 or index >= len(self.mTextureArr)):
            return None

        tex = self.mTextureArr[index]
        if(tex.IsFlipped()):
            tex.FlipDimensions()
            return (True)

        return (False)

    def MergeNodes(self):
        for f in self.mFreeArr:
            fIdx = 0
            for s in self.mFreeArr:
                if (f != s):
                    if (f.Merge(s)):
                        self.mFreeArr[fIdx] = f
                        return (True)
            fIdx += 1

        return (False)

    def Validate(self):
        for f in self.mFreeArr:
            for c in self.mFreeArr:
                if (f != c):
                    f.Validate(c)

    def PackTextures(self, forcePowerOfTwo, onePixelBorder):
        # 0 = width
        # 1 = height
        # 3 = returnValue
        returnList = []

        if (onePixelBorder):
            i = 0
            for t in self.mTextureArr:
                t.SetWidth(t.GetWidth() + 2)
                t.SetHeight(t.GetHeight() + 2)
                self.mTextureArr[i] = t
                i += 1
            self.mLongestEdge += 2

        if (forcePowerOfTwo):
            self.mLongestEdge = self.GetNextPowerOfTwo(self.mLongestEdge)

        width = self.mLongestEdge
        count = self.mTotalArea / (self.mLongestEdge * self.mLongestEdge)
        height = (count + 2) * self.mLongestEdge

        self.AddNode(0, 0, width, height)

        # We must place each texture
        loopI = 0
        while (loopI < len(self.mTextureArr)):
            index = 0
            longestEdge = 0
            mostArea = 0

            # We first search for the texture with the longest edge, placing it first.
            # And the most area...
            j = 0
            for tmpTex in self.mTextureArr:
                #print "Checking texture ", tmpTex.GetName()
                if (not tmpTex.IsPlaced()):
                    if (tmpTex.GetLongestEdge() > longestEdge):
                        mostArea = tmpTex.GetArea()
                        longestEdge = tmpTex.GetLongestEdge()
                        index = j
                    elif (tmpTex.GetLongestEdge() == longestEdge):
                        if (tmpTex.GetArea() > mostArea):
                            mostArea = tmpTex.GetArea()
                            index = j
                j += 1

            # For the texture with the longest edge we place it according to this criteria.
            #   (1) If it is a perfect match, we always accept it as it causes the least amount of fragmentation.
            #   (2) A match of one edge with the minimum area left over after the split.
            #   (3) No edges match, so look for the node which leaves the least amount of area left over after the split.
            tex = self.mTextureArr[index]
            #print "Going to try and place ", tex.GetName()

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
            for currNode in self.mFreeArr:
                resultFitsArr = currNode.Fits(tex.GetRect().GetWidth(), tex.GetRect().GetHeight())
                ec = resultFitsArr[1]

                # see if the texture will fit into this slot, and if so how many edges does it share.
                if (resultFitsArr[0] is True):
                    if (ec == 2):
                        previousBestFitNodeIdx = previousNodeIdx
                        bestFitNode = currNode
                        nodeIndex = idx
                        edgeCount = ec
                        break

                    if (currNode.GetY() < leastY):
                        leastY = currNode.GetY()
                        leastX = currNode.GetX()
                        previousBestFitNodeIdx = previousNodeIdx
                        bestFitNode = currNode
                        nodeIndex = idx
                        edgeCount = ec
                    elif (currNode.GetY() == leastY and currNode.GetX() < leastX):
                        leastX = currNode.GetX()
                        previousBestFitNodeIdx = previousNodeIdx
                        bestFitNode = currNode
                        nodeIndex = idx
                        edgeCount = ec

                previousNodeIdx = idx
                idx += 1

            # we should always find a fit location!
            if(bestFitNode.GetX() == 0 and bestFitNode.GetY() == 0 and bestFitNode.GetRect().GetWidth() == 0 and bestFitNode.GetRect().GetHeight() == 0):
                print "TexturePacker::PackTextures() BestFit node not found!!"
                exit(1)

            self.Validate()

            if (edgeCount == 0):
                if (tex.GetLongestEdge() <= bestFitNode.GetRect().GetWidth()):
                    if (tex.GetHeight() > tex.GetWidth()):
                        tex.FlipDimensions()
                        tex.SetFlipped(True)

                    tex.Place(bestFitNode.GetX(), bestFitNode.GetY(), tex.IsFlipped())

                    self.AddNode(bestFitNode.GetX(), bestFitNode.GetY() + tex.GetHeight(), bestFitNode.GetRect().GetWidth(), bestFitNode.GetRect().GetHeight() - tex.GetHeight())

                    bestFitNode.SetX(bestFitNode.GetX() + tex.GetWidth())
                    bestFitNode.SetWidth(bestFitNode.GetRect().GetWidth() - tex.GetWidth())
                    bestFitNode.SetHeight(tex.GetHeight())
                    self.Validate()
                else:
                    if (tex.GetLongestEdge() <= bestFitNode.GetHeight()):
                        print("TexturePacker::PackTexture() ERROR - Current textures longest edge is less than the BestFitNodes Height!!!")
                        exit(1)

                    if (tex.GetHeight() < tex.GetWidth()):
                        tex.FlipDimensions()
                        tex.SetFlipped(True)

                    tex.Place(bestFitNode.GetX(), bestFitNode.GetY(), tex.IsFlipped())
                    self.AddNode(bestFitNode.GetX(), bestFitNode.GetY() + tex.GetHeight(), bestFitNode.GetRect().GetWidth(), bestFitNode.GetRect().GetHeight() - tex.GetHeight())
                    bestFitNode.SetX(bestFitNode.GetX() + tex.GetWidth())
                    bestFitNode.SetWidth(bestFitNode.GetWidth() - tex.GetWidth())
                    bestFitNode.SetHeight(tex.GetHeight())
                    self.Validate()

            elif(edgeCount == 1):
                if (tex.GetWidth() == bestFitNode.GetRect().GetWidth()):
                    tex.Place(bestFitNode.GetX(), bestFitNode.GetY(), False)
                    bestFitNode.SetY(bestFitNode.GetY() + tex.GetHeight())
                    bestFitNode.SetHeight(bestFitNode.GetRect().GetHeight() - tex.GetHeight())
                    self.Validate()
                elif (tex.mHeight == bestFitNode.GetRect().GetHeight()):
                    tex.Place(bestFitNode.GetX(), bestFitNode.GetY(), False)
                    bestFitNode.SetX(bestFitNode.GetX() + tex.GetWidth())
                    bestFitNode.SetWidth(bestFitNode.GetRect().GetWidth() - tex.GetWidth())
                    self.Validate()
                elif (tex.mWidth == bestFitNode.GetRect().GetHeight()):
                    tex.Place(bestFitNode.GetX(), bestFitNode.GetY(), True)
                    bestFitNode.SetX(bestFitNode.GetX() + tex.GetHeight())
                    bestFitNode.SetWidth(bestFitNode.GetRect().GetWidth() - tex.GetHeight())
                    self.Validate()
                elif (tex.mHeight == bestFitNode.GetRect().GetWidth()):
                    tex.Place(bestFitNode.GetX(), bestFitNode.GetY(), True)
                    bestFitNode.SetY(bestFitNode.GetY() + tex.GetWidth())
                    bestFitNode.SetHeight(bestFitNode.GetHeight() - tex.GetWidth())
                    self.Validate()

            elif(edgeCount == 2):
                flipped = tex.GetWidth() != bestFitNode.GetRect().GetWidth() or tex.GetHeight() != bestFitNode.GetRect().GetHeight()
                tex.Place(bestFitNode.GetX(), bestFitNode.GetY(), flipped)
                if (previousBestFitNodeIdx >= 0):
                    previousBestFitNodeIdx = index
                self.Validate()

            # Save latest version of texture and Node back into lists since python is pass by value
            self.mFreeArr[nodeIndex] = bestFitNode
            self.mTextureArr[index] = tex

            loopI += 1

        while (self.MergeNodes()):
            print "Merging nodes"

        index = 0
        height = 0
        for t in self.mTextureArr:
            if (onePixelBorder):
                t.SetWidth(t.GetWidth() - 2)
                t.SetHeight(t.GetHeight() - 2)
                t.SetX(t.GetX() + 1)
                t.SetY(t.GetY() + 1)
                self.mTextureArr[index] = t

            y = 0
            if (t.IsFlipped()):
                y = t.GetY() + t.GetWidth()
            else:
                y = t.GetY() + t.GetHeight()

            if (y > height):
                height = y

            index += 1

        if (forcePowerOfTwo):
            height = self.GetNextPowerOfTwo(height)

        returnList.append(width)
        returnList.append(height)
        returnList.append((width * height) - self.mTotalArea)
        return (returnList)
