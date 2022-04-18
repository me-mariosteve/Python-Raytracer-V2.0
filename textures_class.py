from vector_class import Vector


class TextureValue:
    
    def __init__(self, value):
        """An unique color/value for all the object"""
        self.value = value

    def getValue(self, position):
        return self.value


class SquareTexture:
    
    def __init__(self, squareSize, val1, val2):
        self.squareSize = squareSize
        self.val1, self.val2 = val1, val2

    def getColor(self, position):
        tempVector = position / self.squareSize
        temp = round(position.x) + round(position.y) + round(position.z)
        return self.val1 if (abs(temp)%2==1) else self.val2
