import numpy as np

perpendicular = 90 
parallel = 180 
pushupStartPos = 160

# bodyParts[0] = Shoulder
# bodyParts[1] = Elbow 
# bodyParts[2] = Wrists 
# bodyParts[3] = Hip 
# bodyParts[4] = DefaultKnee
# bodyParts[5] = OtherKnee
# bodyParts[6] = DefaultAnkle
# bodyParts[7] = OtherAnkle
class PushupResult: 

    # Feedback
    def __init__(self):
        self.feedback_before = [] 
        self.feedback_after = [] 
        self.check1 = False
        self.check2 = False
        self.check3 = False 
        self.check4 = False
        self.check5 = False 
    

    def processResult(self): 
        self.feedback_before = [] 
        self.feedback_after = [] 
        if (self.check1): 
            self.feedback_before.append("Butt is too High")
        if (self.check2): 
            self.feedback_before.append("Knees are Bent")
        if (self.check3):
            self.feedback_before.append("Move your hands under your shoulder")
        if (self.check4):
            self.feedback_after.append("Butt is too High")
        if (self.check5):
            self.feedback_after.append("Go Lower")

    def getResult(self): 
        self.check1 = False 
        self.check2 = False
        self.check3 = False
        self.check4 = False
        self.check5 = False
        return (self.feedback_before, self.feedback_after)


class PushupPostureAnalysis:
    

    def __init__(self, groundList):
        self.pushup = PushupResult()
        self.groundList = groundList 

    # Helper Functions 
    def getSlope(self, pos1, pos2): 
        return (pos2[1] - pos1[1])/(pos2[0] - pos1[0])

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
        print("sample: " + str(threshold))
        print(abs(slope1 - slope2))
        return abs(slope1 - slope2) < threshold 

    def sameAngle(self, angle1, angle2, threshold = 0.1): 
        return abs(angle1 - angle2) < threshold 

    
    # Line 1: Shoulder - Hip 
    # Line 2: Hip - Knee 
    # Line 3: Knee - Ankle 
    # Line 4: Shoulder - Elbow 
    # Line 5: Elbow - Wrist 
    def feedbackCalculation(self, bodyParts, default=True):

        shoulder = bodyParts[0]
        elbow = bodyParts[1]
        wrist = bodyParts[2]
        hip = bodyParts[3]
        knee = bodyParts[4]
        ankle = bodyParts[6]

        line1Slope = self.getSlope(shoulder, hip)
        line2Slope = self.getSlope(hip, knee)
        line3Slope = self.getSlope(knee, ankle)
        line4Slope = self.getSlope(shoulder, elbow)
        line5Slope = self.getSlope(elbow, wrist)
        
        angleHip = self.getAngle(shoulder, hip, knee)
        angleKnee = self.getAngle(hip, knee, ankle)
        print(line1Slope)
        print(line2Slope)
        print(line3Slope)
        print(line4Slope)
        print(line5Slope)
        if not (self.sameSlope(line1Slope, line2Slope, 0.5) and self.sameSlope(line2Slope, line3Slope, 2)): # Back is straight and hip not bent 
            self.pushup.check4 = True 
        if not (self.sameSlope(line4Slope, line1Slope, 0.5)):
            self.pushup.check5 = True
        self.pushup.processResult() 
        
       
    def getResult(self): 
        return self.pushup.getResult()
        



groundList = [(0,0), (0,0)]
bodyParts = [(142,98), (131,99), (133,114), (116,105), (65,105), (0,0), (39,107), (0,0)]
upBodyParts = [(134.0, 82.5), (133, 98), (135.5, 112.0), (103.5, 78.5), (59.0, 99.0), (93.0, 50.0), (34.0, 107.0), (59.5, 97.0)]

pushup = PushupPostureAnalysis(groundList)

pushup.pushupMoveAfter(bodyParts)
result = pushup.getResult()
print(result[1])

print("HELLOOOOOO")
pushup.pushupMoveAfter(upBodyParts)
result = pushup.getResult()
print(result[1])