from pushupAnalysis import *
from legRaiseAnalysis import *
from lungeAnalysis import *


# Images from 'images/Nov/<workout>' 

# Convert String to List of Body Parts 
def convertString(bodyParts):
    result = [] 
    bodyParts = bodyParts[1:-1]
    bodyList = bodyParts.split(", ")

    for index in range(0, len(bodyList), 2):
        row = float(bodyList[index][1:])
        col = float(bodyList[index + 1][:-1])
        result.append((row, col))

    return result 


# Leg Raise 

perfect = [(91.5, 33.5), (96.0, 49.0), (96.0, 65.5), (88.0, 55.5), (41.5, 66.5), (46.0, 72.0), (22.0, 70.0), (27.0, 75.0)]
over = [(93.0, 32.0), (96.5, 47.5), (97.0, 66.0), (83.5, 49.0), (40.5, 36.5), (42.5, 42.5), (21.5, 35.0), (24.5, 37.5)]
under = [(92.5, 32.5), (96.5, 48.5), (97.0, 66.0), (89.5, 56.0), (49.5, 81.5), (90.0, 59.0), (33.5, 90.5), (0.0, 0.0)]
kneeBent = [(92.0, 33.0), (96.5, 48.5), (97.0, 65.0), (89.5, 56.5), (45.5, 63.5), (51.0, 70.0), (31.0, 77.0), (35.5, 80.5)]

legRaise = LegRaisePostureAnalysis()


legRaise.feedbackCalculation(perfect)
result = legRaise.getResult()
print("Perfect: " + str(result))
print("\n")

legRaise.feedbackCalculation(over)
result = legRaise.getResult()
print("Over: " + str(result))
print("\n")

legRaise.feedbackCalculation(under)
result = legRaise.getResult()
print("Under: " + str(result))
print("\n")

legRaise.feedbackCalculation(kneeBent)
result = legRaise.getResult()
print("Knee Bent: " + str(result))
print("\n")



################################################################

# Pushup 

perfect = [(69.0, 128.5), (73.0, 123.0), (90.5, 120.0), (76.5, 102.5), (79.0, 43.0), (87.5, 81.0), (83.5, 20.0), (0.0, 0.0)]
handForward = [(71.5, 129.5), (72.5, 121.5), (92.5, 129.5), (81.0, 99.0), (80.0, 40.0), (0.0, 0.0), (84.5, 17.0), (80.5, 38.5)]
low = [(77.0, 141.5), (72.5, 131.0), (92.0, 129.5), (85.5, 106.5), (84.0, 55.0), (83.0, 103.5), (85.0, 33.0), (0.0, 0.0)]
high = [(57.5, 127.0), (68.5, 125.5), (88.5, 126.5), (64.0, 100.5), (75.5, 45.0), (82.0, 46.0), (81.5, 21.5), (85.5, 27.0)]
buttHigh = [(76.0, 138.0), (74.5, 133.5), (92.5, 132.0), (80.0, 108.0), (79.0, 52.0), (75.5, 106.5), (83.0, 29.5), (0.0, 0.0)]
 


pushup = PushupPostureAnalysis()


pushup.feedbackCalculation(perfect)
result = pushup.getResult()
print("Perfect: " + str(result))
print("\n")

pushup.feedbackCalculation(handForward)
result = pushup.getResult()
print("handForward: " + str(result))
print("\n")

pushup.feedbackCalculation(low)
result = pushup.getResult()
print("Low: " + str(result))
print("\n")

pushup.feedbackCalculation(high)
result = pushup.getResult()
print("High: " + str(result))
print("\n")

# # TODO: Fix this 
# pushup.feedbackCalculation(buttHigh)
# result = pushup.getResult()
# print("Butt High: " + str(result))


################################################################

# Lunges 

forwardForward = [(0.0, 0.0), (29.5, 80.5), (15.5, 87.5), (49.5, 88.5), (65.0, 127.5), (96.5, 66.5), (84.5, 118.5), (92.0, 48.5)]  
perfectForward = [(0.0, 0.0), (17.5, 72.5), (0.0, 0.0), (38.0, 85.0), (60.5, 122.5), (87.5, 61.0), (82.0, 118.0), (88.0, 42.0)]
backwardForward = [(27.5, 95.5), (32.5, 92.5), (20.5, 108.0), (53.0, 99.0), (64.0, 138.5), (95.0, 67.0), (84.0, 126.5), (90.5, 48.0)]


forwardBackward = [(0.0, 0.0), (31.5, 74.5), (21.5, 82.5), (53.5, 84.5), (94.0, 67.0), (70.5, 115.5), (91.0, 46.5), (88.5, 108.5)]
perfectBackward = [(0.0, 0.0), (23.5, 67.5), (11.5, 81.0), (45.5, 78.0), (86.5, 60.0), (69.0, 110.5), (87.5, 38.0), (88.0, 105.5)]
backwardBackward = [(0.0, 0.0), (0.0, 0.0), (25.5, 95.5), (58.0, 93.5), (95.0, 68.5), (70.5, 125.5), (91.5, 48.0), (86.5, 118.0)]


lunge = LungePostureAnalysis()

lunge.feedbackCalculation(forwardForward)
result = lunge.getResult()
print("forwardForward: " + str(result))
print("\n")

lunge.feedbackCalculation(perfectForward)
result = lunge.getResult()
print("perfectForward: " + str(result))
print("\n")

lunge.feedbackCalculation(backwardForward)
result = lunge.getResult()
print("backwardForward: " + str(result))
print("\n")



lunge.feedbackCalculation(forwardBackward, False)
result = lunge.getResult()
print("forwardBackward: " + str(result))
print("\n")

lunge.feedbackCalculation(perfectBackward, False)
result = lunge.getResult()
print("perfectBackward: " + str(result))
print("\n")

lunge.feedbackCalculation(backwardBackward, False)
result = lunge.getResult()
print("backwardBackward: " + str(result))
print("\n")