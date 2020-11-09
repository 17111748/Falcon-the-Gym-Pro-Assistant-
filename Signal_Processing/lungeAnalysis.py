import numpy as np

perpendicular = 90 
parallel = 180 

# bodyParts[0] = Shoulder
# bodyParts[1] = Elbow 
# bodyParts[2] = Wrists 
# bodyParts[3] = Hip 
# bodyParts[4] = DefaultKnee
# bodyParts[5] = OtherKnee
# bodyParts[6] = DefaultAnkle
# bodyParts[7] = OtherAnkle

class LungeResult: 

    # Feedback
    def __init__(self):
        self.feedback = [] 
        self.check1 = False
        self.check2 = False
        self.check3 = False 

    def processResult(self): 
        self.feedback = [] 
        if (self.check1): 
            self.feedback.append("Front Knee too Forward")
        if (self.check2): 
            self.feedback.append("Go Lower")
        if (self.check3):
            self.feedback.append("Back Legs too far Back")

    def getResult(self): 
        self.check1 = False 
        self.check2 = False
        self.check3 = False
        return self.feedback


class LungePostureAnalysis:

    def __init__(self):
        self.lunge = LungeResult()

    # Helper Functions 
    def getSlope(self, pos0, pos1): 
        height = 120 
        y1 = height - pos1[0]
        x1 = pos1[1]
        y0 = height - pos0[0]
        x0 = pos0[1]
        return (y1-y0)/(x1-x0)

    def getAngle(self, Point1, MidPoint, Point2):
        a = np.array(Point1)
        b = np.array(MidPoint)
        c = np.array(Point2)

        ba = a - b
        bc = c - b
        
        cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
        angle = np.arccos(cosine_angle)

        return np.degrees(angle)

    def sameSlope(self, slope1, slope2, threshold = 0.1):
        return abs(slope1 - slope2) < threshold 

    def sameAngle(self, angle1, angle2, threshold = 0.1): 
        return abs(angle1 - angle2) < threshold 

    def samePos(self, pos0, pos1, threshold = 0):
        return abs(pos0 - pos1) <= threshold

    def lessThan(self, pos0, pos1, threshold = 0): 
        return (pos0 - threshold) <= pos1  
    
    def greaterThan(self, pos0, pos1, threshold = 0): 
        return pos0 >= (pos1 - threshold)  

    # Line 1: Hip - DefaultKnee 
    # Line 2: DefaultKnee - DefaultAnkle
    # Line 3: Hip - OtherKnee
    # Line 4: OtherKnee - OtherAnkle 
    # Line 5: Shoulder - Hip 
    def feedbackCalculation(self, bodyParts, default=True):

        shoulder = bodyParts[0]
        hip = bodyParts[3]
        defaultKnee = bodyParts[4]
        otherKnee = bodyParts[5]
        defaultAnkle = bodyParts[6]
        otherAnkle = bodyParts[7]

        if (default == False):
            defaultKnee = bodyParts[5]
            otherKnee = bodyParts[4]
            defaultAnkle = bodyParts[7]
            otherAnkle = bodyParts[6]

        line1Slope = self.getSlope(hip, defaultKnee)
        # line2Slope = self.getSlope(defaultKnee, defaultAnkle)
        line3Slope = self.getSlope(hip, otherKnee)
        # line4Slope = self.getSlope(otherKnee, otherAnkle)

        # angleHip = self.getAngle(shoulder, hip, defaultKnee)
        # angleHipOther = self.getAngle(shoulder, hip, otherKnee)
        # angleDefaultKnee = self.getAngle(hip, defaultKnee, defaultAnkle)
        # angleOtherKnee = self.getAngle(hip, otherKnee, otherAnkle)

        frontLegSlope = -0.75
        backLegSlope = 2

        # # Front Leg too forward
        # print(defaultKnee[1])
        # print(defaultAnkle[1])
        # print(self.samePos(defaultKnee[1], defaultAnkle[1], 2))
        # print(defaultKnee[1] > defaultAnkle[1])

        # # Go Lower
        # print(otherAnkle[0])
        # print(otherKnee[0])
        # print(line1Slope)
        # print(frontLegSlope)
        # print(self.lessThan(otherAnkle[0], otherKnee[0], 1))
        # print(self.greaterThan(line1Slope, frontLegSlope, 0.1))
        
        # # Back Legs Too Backward
        # print(line3Slope)
        # print(backLegSlope)
        # print(self.greaterThan(line3Slope, backLegSlope))
        # print(self.sameAngle(angleOtherKnee, perpendicular))

        if not (self.samePos(defaultKnee[1], defaultAnkle[1], 5)):
            if (defaultKnee[1] > defaultAnkle[1]):
                self.lunge.check1 = True

        if not (self.lessThan(otherAnkle[0], otherKnee[0], 1) and self.greaterThan(line1Slope, frontLegSlope, 0.1)):
            self.lunge.check2 = True

        if not (self.greaterThan(line3Slope, backLegSlope)):
            self.lunge.check3 = True 

        
        self.lunge.processResult() 


    def getResult(self): 
        return self.lunge.getResult()



#############################################################


forwardForward = [(0.0, 0.0), (29.5, 80.5), (15.5, 87.5), (49.5, 88.5), (65.0, 127.5), (96.5, 66.5), (84.5, 118.5), (92.0, 48.5)]  
perfectForward = [(0.0, 0.0), (17.5, 72.5), (0.0, 0.0), (38.0, 85.0), (60.5, 122.5), (87.5, 61.0), (82.0, 118.0), (88.0, 42.0)]
backwardForward = [(27.5, 95.5), (32.5, 92.5), (20.5, 108.0), (53.0, 99.0), (64.0, 138.5), (95.0, 67.0), (84.0, 126.5), (90.5, 48.0)]


forwardBackward = [(0.0, 0.0), (31.5, 74.5), (21.5, 82.5), (53.5, 84.5), (94.0, 67.0), (70.5, 115.5), (91.0, 46.5), (88.5, 108.5)]
perfectBackward = [(0.0, 0.0), (23.5, 67.5), (11.5, 81.0), (45.5, 78.0), (86.5, 60.0), (69.0, 110.5), (87.5, 38.0), (88.0, 105.5)]
backwardBackward = [(0.0, 0.0), (0.0, 0.0), (25.5, 95.5), (58.0, 93.5), (95.0, 68.5), (70.5, 125.5), (91.5, 48.0), (86.5, 118.0)]




# lunge = LungePostureAnalysis()

# lunge.feedbackCalculation(forwardForward)
# result = lunge.getResult()
# print("forwardForward: " + str(result))
# print("\n")

# lunge.feedbackCalculation(perfectForward)
# result = lunge.getResult()
# print("perfectForward: " + str(result))
# print("\n")

# lunge.feedbackCalculation(backwardForward)
# result = lunge.getResult()
# print("backwardForward: " + str(result))
# print("\n")



# lunge.feedbackCalculation(forwardBackward, False)
# result = lunge.getResult()
# print("forwardBackward: " + str(result))
# print("\n")

# lunge.feedbackCalculation(perfectBackward, False)
# result = lunge.getResult()
# print("perfectBackward: " + str(result))
# print("\n")

# lunge.feedbackCalculation(backwardBackward, False)
# result = lunge.getResult()
# print("backwardBackward: " + str(result))
# print("\n")