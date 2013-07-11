from math.rect import Rect


class Node:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def does_rect_fit(self, width, height):
        # 0 = bool, 1 = edgeCount
        resultList = []

        result = False
        edgeCount = 0

        if (width == self.width or height == self.height or width == self.height or height == self.width):
            if (width == self.width):
                edgeCount += 1
            if (height == self.height):
                edgeCount += 1
            elif (width == self.height):
                edgeCount += 1
                if (height == self.width):
                    edgeCount += 1
            elif (height == self.width):
                edgeCount += 1
            elif (height == self.height):
                edgeCount += 1

        if (width <= self.width and height <= self.height):
            result = True
        elif (height <= self.width and width <= self.height):
            result = True

        resultList.append(result)
        resultList.append(edgeCount)

        return (resultList)

    def get_rect(self):
        return Rect(self.x, self.y, self.x + self.width, self.y + self.height)

    def validate(self, node):
        r1 = self.get_rect()
        r2 = node.get_rect()
        return (r1 != r2)

    def merge(self, node):
        ret = False
        r1 = self.get_rect()
        r2 = node.get_rect()

        r1.x2 += 1
        r1.y2 += 1
        r2.x2 += 1
        r2.y2 += 1

        if (r1.x1 == r2.x1 and r1.x2 == r2.x2 and r1.y1 == r2.y2):
            self.y = node.y
            self.height += node.get_rect().height
            ret = True
        elif (r1.x1 == r2.x1 and r1.x2 == r2.x2 and r1.y2 == r2.y1):
            self.height += node.get_rect().height
            ret = True
        elif (r1.y1 == r2.y1 and r1.y2 == r2.y1 and r1.x1 == r2.x2):
            self.x = node.x
            self.width += node.get_rect().width
            ret = True
        elif (r1.y1 == r2.y1 and r1.y2 == r2.y1 and r1.x2 == r2.x1):
            self.width += node.get_rect().width
            ret = True

        return ret
