from math.rect import Rect


class Node:
    def __init__(self, x, y, width, height):
        self.mX = x
        self.mY = y
        self.mWidth = width
        self.mHeight = height

    def Fits(self, width, height):
        # 0 = bool, 1 = edgeCount
        resultList = []

        result = False
        edgeCount = 0

        if (width == self.mWidth or height == self.mHeight or width == self.mHeight or height == self.mWidth):
            if (width == self.mWidth):
                edgeCount += 1
            if (height == self.mHeight):
                edgeCount += 1
            elif (width == self.mHeight):
                edgeCount += 1
                if (height == self.mWidth):
                    edgeCount += 1
            elif (height == self.mWidth):
                edgeCount += 1
            elif (height == self.mHeight):
                edgeCount += 1

        if (width <= self.mWidth and height <= self.mHeight):
            result = True
        elif (height <= self.mWidth and width <= self.mHeight):
            result = True

        resultList.append(result)
        resultList.append(edgeCount)

        return (resultList)

    def GetRect(self):
        return (Rect(self.mX, self.mY, self.mX + self.mWidth, self.mY + self.mHeight))

    def GetX(self):
        return (self.mX)

    def GetY(self):
        return (self.mY)

    def SetX(self, x):
        self.mX = x

    def SetY(self, y):
        self.mY = y

    def SetWidth(self, width):
        self.mWidth = width

    def SetHeight(self, height):
        self.mHeight = height

    def Validate(self, node):
        r1 = self.GetRect()
        r2 = node.GetRect()
        return (r1 != r2)

    def Merge(self, node):
        ret = False
        r1 = self.GetRect()
        r2 = node.GetRect()

        r1.SetX2(r1.GetX2() + 1)
        r1.SetY2(r1.GetY2() + 1)
        r2.SetX2(r2.GetX2() + 1)
        r2.SetY2(r2.GetY2() + 1)

        if (r1.GetX1() == r2.GetX1() and r1.GetX2() == r2.GetX2() and r1.GetY1() == r2.GetY2()):
            self.mY = node.GetY()
            self.mHeight += node.GetRect().GetHeight()
            ret = True
        elif (r1.GetX1() == r2.GetX1() and r1.GetX2() == r2.GetX2() and r1.GetY2() == r2.GetY1()):
            self.mHeight += node.GetRect().GetHeight()
            ret = True
        elif (r1.GetY1() == r2.GetY1() and r1.GetY2() == r2.GetY1() and r1.GetX1() == r2.GetX2()):
            self.mX = node.GetX()
            self.mWidth += node.GetRect().GetWidth()
            ret = True
        elif (r1.GetY1() == r2.GetY1() and r1.GetY2() == r2.GetY1() and r1.GetX2() == r2.GetX1()):
            self.mWidth += node.GetRect().GetWidth()
            ret = True

        return ret

    def Print(self):
        print "Node = (x=", self.mX, "y=", self.mY, "width=", self.mWidth, "height=", self.mHeight, ")"
