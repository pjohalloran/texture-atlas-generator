

class Rect:
    def __init__(self, x1, y1, x2, y2):
        self.mX1 = x1
        self.mY1 = y1
        self.mX2 = x2
        self.mY2 = y2

    def Intersects(self, r):
        if (self.mX2 < r.mX1 or self.mX1 > r.mX2 or self.mY2 < r.mY1 or self.mY1 > r.mY2):
            return (False)
        return (True)

    def GetX1(self):
        return (self.mX1)

    def GetY1(self):
        return (self.mY1)

    def GetX2(self):
        return (self.mX2)

    def GetY2(self):
        return (self.mY2)

    def SetX1(self, x1):
        self.mX1 = x1

    def SetY1(self, y1):
        self.mY1 = y1

    def SetX2(self, x2):
        self.mX2 = x2

    def SetY2(self, y2):
        self.mY2 = y2

    def GetWidth(self):
        return (self.mX2 - self.mX1)

    def GetHeight(self):
        return (self.mY2 - self.mY1)

    def GetArea(self):
        return (self.GetWidth()*self.GetHeight())

    def Print(self):
        print "Rect = (x1=", self.mX1, "y1=", self.mY1, "x2=", self.mX2, "y2=", self.mY2, "width=", self.GetWidth(), "height=", self.GetHeight(), ")"
