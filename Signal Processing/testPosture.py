from pushupAnalysis import *
from legRaiseAnalysis import *
from lungeAnalysis import *



groundList = [(0,0), (0,0)]
bodyParts = [(142,98), (131,99), (133,114), (116,105), (65,105), (0,0), (39,107), (0,0)]
upBodyParts = [(134.0, 82.5), (133, 98), (135.5, 112.0), (103.5, 78.5), (59.0, 99.0), (93.0, 50.0), (34.0, 107.0), (59.5, 97.0)]

pushup = PushupPostureAnalysis(groundList)

pushup.pushupMoveAfter(bodyParts)
result = pushup.getResult()
print(result[1])

pushup.pushupMoveAfter(upBodyParts)
result = pushup.getResult()
print(result[1])