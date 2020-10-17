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

class PuhsupPostureAnalysis:

    def __init__(self, groundList):
        self.pushup = PushUpResult()
        self.groundList = groundList 

    # Helper Functions 
    def getSlope(pos1, pos2): 
        return (pos2[1] - pos1[1])/(pos2[0] - pos1[0])

    def getAngle(Point1, MidPoint, Point2):
        a = np.array(Point1)
        b = np.array(MidPoint)
        c = np.array(Point2)

        ba = a - b
        bc = c - b
        
        cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
        angle = np.arccos(cosine_angle)

        return np.degrees(angle)

    def sameSlope(slope1, slope2, threshold = 0.1):
        return abs(slope1 - slope2) < threshold 

    def sameAngle(angle1, angle2, threshold = 0.1): 
        return abs(angle1 - angle2) < threshold 

    # Line 1: Shoulder - Hip 
    # Line 2: Hip - Knee 
    # Line 3: Knee - Ankle 
    # Line 4: Shoulder - Elbow 
    # Line 5: Elbow - Wrist 
    def pushupMoveBefore(self, bodyParts):

        shoulder = bodyParts[0]
        elbow = bodyParts[1]
        wrist = bodyParts[2]
        hip = bodyParts[3]
        knee = bodyParts[4]
        ankle = bodyParts[6]

        line1Slope = getSlope(shoulder, hip)
        line2Slope = getSlope(hip, knee)
        line3Slope = getSlope(knee, ankle)
        line4Slope = getSlope(shoulder, elbow)
        line5Slope = getSlope(elbow, wrist)

        angleShoulder = getAngle(hip, shoulder, elbow)
        angleWrist = getAngle(elbow, wrist, groundList[0])
      

        groundSlope = getSlope(self.groundList[0], self.groundList[1])
        
        if (!(sameSlope(line1Slope, line2Slope))): # Hip is too high 
            self.pushup.check1 = True 
        if (!(sameSlope(line2Slope, line3Slope))): # Knees are Bent 
            self.pushup.check2 = True 
        if (angleShoulder > perpendicular and !(sameAngle(angleWrist, perpendicular))):
            self.pushup.check3 = True 

        self.pushup.processResult()
    
    # Line 1: Shoulder - Hip 
    # Line 2: Hip - Knee 
    # Line 3: Knee - Ankle 
    # Line 4: Shoulder - Elbow 
    # Line 5: Elbow - Wrist 
    def pushupMoveAfter(self, bodyParts):

        shoulder = bodyParts[0]
        elbow = bodyParts[1]
        wrist = bodyParts[2]
        hip = bodyParts[3]
        knee = bodyParts[4]
        ankle = bodyParts[6]

        line1Slope = getSlope(shoulder, hip)
        line2Slope = getSlope(hip, knee)
        line3Slope = getSlope(knee, ankle)
        line4Slope = getSlope(shoulder, elbow)
        line5Slope = getSlope(elbow, wrist)

        groundSlope = getSlope(self.groundList[0], self.groundList[1])
        
        angleHip = getAngle(shoulder, hip, knee)
        angleKnee = getAngle(hip, knee, ankle)

        if (!(sameSlope(line1Slope, groundSlope) and sameSlope(line2Slope, groundSlope) and sameSlope(line3Slope, groundSlope))): # Back is straight and hip not bent 
            self.pushup.check4 = True 
        if (!(sameSlope(line4Slope, line1Slope))):
            self.pushup.check5 = True

        self.pushup.processResult() 

    def pushupPostureAnalysis(self): 
        return self.pushup.getResult 
        
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
