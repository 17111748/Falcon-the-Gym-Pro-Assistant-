import numpy as np

perpendicular = 90 
parallel = 180 
lungeStartPos = 160

# bodyParts[0] = Shoulder
# bodyParts[1] = Elbow 
# bodyParts[2] = Wrists 
# bodyParts[3] = Hip 
# bodyParts[4] = DefaultKnee
# bodyParts[5] = OtherKnee
# bodyParts[6] = DefaultAnkle
# bodyParts[7] = OtherAnkle

class LungePostureAnalysis:

    def __init__(self, groundList):
        self.lunge = LungeResult()
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
    
    def findPerpendicular(num1, num2, threshold = 0.1):
        return abs(num1 - num2) < threshold

    # Line 1: Hip - DefaultKnee 
    # Line 2: DefaultKnee - DefaultAnkle
    # Line 3: Hip - OtherKnee
    # Line 4: OtherKnee - OtherAnkle 
    # Line 5: Shoulder - Hip 
    def lungeMoveDefault(self, bodyParts):

        shoulder = bodyParts[0]
        hip = bodyParts[3]
        defaultKnee = bodyParts[4]
        otherKnee = bodyParts[5]
        defaultAnkle = bodyParts[6]
        otherAnkle = bodyParts[7]

        line1Slope = getSlope(hip, defaultKnee)
        line2Slope = getSlope(knee, defaultAnkle)
        line3Slope = getSlope(hip, otherKnee)
        line4Slope = getSlope(otherKnee, otherAnkle)
        line5Slope = getSlope(hip, shoulder)

        angleHip = getAngle(shoulder, hip, defaultKnee)
        angleDefaultKnee = getAngle(hip, defaultKnee, defaultAnkle)
        angleOtherKnee = getAngle(hip, otherKnee, otherAnkle)

        groundSlope = getSlope(self.groundList[0], self.groundList[1])
        
        # TODO: Make sure that the angle is the y value where ankle touches 
        if (!(findPerpendicular(line5Slope * groundSlope, -1))):
            self.lunge.check1 = True 
        if (!(sameAngle(angleDefaultKnee, perpendicular) and sameSlope(groundSlope, line1Slope))):
            self.lunge.check2 = True 
        if (!(sameSlope(line4Slope, groundSlope) and sameAngle(angleOtherKnee, perpendicular))):
            self.lunge.check3 = True 
        
        self.lunge.processResult() 
    
    # Line 1: Hip - DefaultKnee 
    # Line 2: DefaultKnee - DefaultAnkle
    # Line 3: Hip - OtherKnee
    # Line 4: OtherKnee - OtherAnkle 
    # Line 5: Shoulder - Hip 
    def lungeMoveOther(self, bodyParts):

        shoulder = bodyParts[0]
        hip = bodyParts[3]
        defaultKnee = bodyParts[4]
        otherKnee = bodyParts[5]
        defaultAnkle = bodyParts[6]
        otherAnkle = bodyParts[7]

        line1Slope = getSlope(hip, defaultKnee)
        line2Slope = getSlope(knee, defaultAnkle)
        line3Slope = getSlope(hip, otherKnee)
        line4Slope = getSlope(otherKnee, otherAnkle)
        line5Slope = getSlope(hip, shoulder)

        angleHip = getAngle(shoulder, hip, defaultKnee)
        angleDefaultKnee = getAngle(hip, defaultKnee, defaultAnkle)
        angleOtherKnee = getAngle(hip, otherKnee, otherAnkle)

        groundSlope = getSlope(self.groundList[0], self.groundList[1])
        
        # TODO: Make sure that the angle is the y value where ankle touches 
        if (!(findPerpendicular(line5Slope * groundSlope, -1))):
            self.lunge.check1 = True 
        if (!(sameAngle(angleDefaultKnee, perpendicular) and sameSlope(groundSlope, line2Slope))):
            self.lunge.check2 = True 
        if (!(sameSlope(line3Slope, groundSlope) and sameAngle(angleOtherKnee, perpendicular))):
            self.lunge.check3 = True 
        
        self.lunge.processResult() 


    def lungePostureAnalysis(self): 
        return self.pushup.getResult 
        
    class LungeResult: 

        # Feedback
        def __init__(self):
            self.feedback_before = [] 
            self.feedback_after = [] 
            self.check1 = False
            self.check2 = False
            self.check3 = False 
            self.check4 = False
            self.check5 = False 
            self.check6 = False

        def processResult(self): 
            self.feedback_before = [] 
            self.feedback_after = [] 
            if (self.check1): 
                self.feedback_before.append("Straighten your Back")
            if (self.check2): 
                self.feedback_before.append("Move Front Legs Forward")
            if (self.check3):
                self.feedback_before.append("Go Lower on your Back Legs")
            if (self.check4):
                self.feedback_after.append("Straighten your Back ")
            if (self.check5):
                self.feedback_after.append("Go Lower on your Back Leg")
            if (self.check6):
                self.feedback_after.append("Move Front Leg Forward")

        def getResult(self): 
            self.check1 = False 
            self.check2 = False
            self.check3 = False
            self.check4 = False
            self.check5 = False
            self.check6 = False 
            return (self.feedback_before, self.feedback_after)
