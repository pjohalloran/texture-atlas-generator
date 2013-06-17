from math.rect import Rect


class Texture:
    def __init__(self, width, height, name=""):
        self.mWidth = width
        self.mHeight = height
        self.mX = 0
        self.mY = 0
        self.mArea = width * height
        self.mFlipped = False
        self.mPlaced = False
        self.mLongestEdge = width if width > height else height
        self.mName = name

    def Place(self, x, y, flipped=False):
        self.mX = x
        self.mY = y
        self.mFlipped = flipped
        self.mPlaced = True
        print "Placing ", self.mName, "at ", self.mX, self.mY

    def GetX(self):
        return (self.mX)

    def SetX(self, x):
        self.mX = x

    def GetY(self):
        return (self.mY)

    def SetY(self, y):
        self.mY = y

    def GetArea(self):
        return (self.mArea)

    def GetWidth(self):
        return (self.mWidth)

    def GetHeight(self):
        return (self.mHeight)

    def SetWidth(self, width):
        self.mWidth = width

    def SetHeight(self, height):
        self.mHeight = height

    def IsPlaced(self):
        return (self.mPlaced)

    def IsFlipped(self):
        return (self.mFlipped)

    def SetFlipped(self, flipped):
        self.mFlipped = flipped

    def FlipDimensions(self):
        if(self.mFlipped):
            tmp = self.mWidth
            self.mWidth = self.mHeight
            self.mHeight = tmp

    def GetRect(self):
        return (Rect(self.mX, self.mY, self.mX + self.mWidth, self.mY + self.mHeight))

    def GetLongestEdge(self):
        return (self.mLongestEdge)

    def GetName(self):
        return (self.mName)

    def SetName(self, name):
        self.mName = name

    def Print(self):
        print "Texture = (", self.GetRect().Print(), "area=", self.mArea, "flipped=", self.mFlipped, "placed=", self.mPlaced, "longestEdge=", self.mLongestEdge, "name=", self.mName, ")"
