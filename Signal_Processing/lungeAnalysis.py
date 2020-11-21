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
        self.invalid = [] 
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

        if (self.invalid): 
            self.feedback = []
            str = "Invalid Joints Detected:"
            if (0 in self.invalid):
                str += " Shoulder,"
            if (1 in self.invalid):
                str += " Elbow,"
            if (2 in self.invalid):
                str += " Wrist,"
            if (3 in self.invalid):
                str += " Hip,"
            if (4 in self.invalid):
                str += " Knee,"
            if (5 in self.invalid):
                str += " Other Knee,"
            if (6 in self.invalid):
                str += " Ankle,"
            if (7 in self.invalid):
                str += " Other Ankle,"
            str = str[:-1] + "!"
            self.feedback.append(str)

    def getResult(self): 
        self.check1 = False 
        self.check2 = False
        self.check3 = False
        self.invalid = [] 
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

        if ((x1 - x0) == 0):
            if (y1 != y0): 
                return float("inf") 
            else: 
                return 0 

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

        hip = (int(bodyParts[3][0]), int(bodyParts[3][1])) 
        defaultKnee = (int(bodyParts[4][0]), int(bodyParts[4][1])) 
        otherKnee = (int(bodyParts[5][0]), int(bodyParts[5][1])) 
        defaultAnkle = (int(bodyParts[6][0]), int(bodyParts[6][1])) 
        otherAnkle = (int(bodyParts[7][0]), int(bodyParts[7][1])) 

        if (hip[0] == 0 and hip[1] == 0):
            self.lunge.invalid.append(3)
            
        if (defaultKnee[0] == 0 and defaultKnee[1] == 0):
            self.lunge.invalid.append(4)
        
        if (otherKnee[0] == 0 and otherKnee[1] == 0):
            self.lunge.invalid.append(5)

        if (defaultAnkle[0] == 0 and defaultAnkle[1] == 0):
            self.lunge.invalid.append(6) 
        
        if (otherAnkle[0] == 0 and otherAnkle[1] == 0):
            self.lunge.invalid.append(7)

        if (default == False):
            defaultKnee = (int(bodyParts[5][0]), int(bodyParts[5][1])) 
            otherKnee = (int(bodyParts[4][0]), int(bodyParts[4][1])) 
            defaultAnkle = (int(bodyParts[7][0]), int(bodyParts[7][1])) 
            otherAnkle = (int(bodyParts[6][0]), int(bodyParts[6][1])) 

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

        # Front Leg too forward
        # print(defaultKnee[1])
        # print(defaultAnkle[1])
        

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

        if not (self.lessThan(defaultKnee[1], defaultAnkle[1], 6)):
            self.lunge.check1 = True

        if not (self.lessThan(otherAnkle[0], otherKnee[0], 1) and self.greaterThan(line1Slope, frontLegSlope, 0.1)):
            self.lunge.check2 = True

        if not (self.greaterThan(line3Slope, backLegSlope)):
            self.lunge.check3 = True 

        
        self.lunge.processResult() 


    def getResult(self): 
        return self.lunge.getResult()



#############################################################


# forwardForward = [(0.0, 0.0), (29.5, 80.5), (15.5, 87.5), (49.5, 88.5), (65.0, 127.5), (96.5, 66.5), (84.5, 118.5), (92.0, 48.5)]  
# perfectForward = [(0.0, 0.0), (17.5, 72.5), (0.0, 0.0), (38.0, 85.0), (60.5, 122.5), (87.5, 61.0), (82.0, 118.0), (88.0, 42.0)]
# backwardForward = [(27.5, 95.5), (32.5, 92.5), (20.5, 108.0), (53.0, 99.0), (64.0, 138.5), (95.0, 67.0), (84.0, 126.5), (90.5, 48.0)]


# forwardBackward = [(0.0, 0.0), (31.5, 74.5), (21.5, 82.5), (53.5, 84.5), (94.0, 67.0), (70.5, 115.5), (91.0, 46.5), (88.5, 108.5)]
# perfectBackward = [(0.0, 0.0), (23.5, 67.5), (11.5, 81.0), (45.5, 78.0), (86.5, 60.0), (69.0, 110.5), (87.5, 38.0), (88.0, 105.5)]
# backwardBackward = [(0.0, 0.0), (0.0, 0.0), (25.5, 95.5), (58.0, 93.5), (95.0, 68.5), (70.5, 125.5), (91.5, 48.0), (86.5, 118.0)]




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