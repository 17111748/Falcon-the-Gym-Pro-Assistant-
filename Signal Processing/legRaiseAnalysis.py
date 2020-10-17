
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

class LegRaisePostureAnalysis:

    def __init__(self, groundList):
        self.legRaise = LegRaiseResult()
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
    def legRaiseMoveBefore(self, bodyParts):

        shoulder = bodyParts[0]
        hip = bodyParts[3]
        knee = bodyParts[4]
        ankle = bodyParts[6]

        line1Slope = getSlope(shoulder, hip)
        line2Slope = getSlope(hip, knee)
        line3Slope = getSlope(knee, ankle)

        groundSlope = getSlope(self.groundList[0], self.groundList[1])
        
        if (!(sameSlope(line1Slope, groundSlope) and sameSlope(line2Slope, groundSlope) and sameSlope(line3Slope, groundSlope))):
            self.legRaise.check1 = True 

        self.legRaise.processResult()
    
    # Line 1: Shoulder - Hip 
    # Line 2: Hip - Knee 
    # Line 3: Knee - Ankle 
    def legRaiseMoveAfter(self, bodyParts):

        shoulder = bodyParts[0]
        hip = bodyParts[3]
        knee = bodyParts[4]
        ankle = bodyParts[6]

        line1Slope = getSlope(shoulder, hip)
        line2Slope = getSlope(hip, knee)
        line3Slope = getSlope(knee, ankle)

        groundSlope = getSlope(self.groundList[0], self.groundList[1])
        
        angleHip = getAngle(shoulder, hip, knee)
        angleKnee = getAngle(hip, knee, ankle)

        if (!(sameAngle(angleHip, perpendicular))):
            if(angleHip > perpendicular):
                self.legRaise.check2 = True 
            else: 
                self.legRaise.check3 = True 
        
        if (!(samgeAngle(angleKnee, parallel))):
            self.legRaise.check4 = True 

        self.legRaise.processResult()

    def legRaisePostureAnalysis(self): 
        return self.legRaise.getResult 
        
    class LegRaiseResult: 

        # Feedback
        def __init__(self):
            self.feedback_before = [] 
            self.feedback_after = [] 
            self.check1 = False
            self.check2 = False
            self.check3 = False 
            self.check4 = False
        

        def processResult(self): 
            self.feedback_before = [] 
            self.feedback_after = [] 
            if (self.check1): 
                self.feedback_before.append("Lie Flat on the Ground")
            if (self.check2): 
                self.feedback_after.append("Raise You Legs Higher")
            if (self.check3):
                self.feedback_after.append("Legs are too High")
            if (self.check4):
                self.feedback_after.append("Knees are Bent")

        def getResult(self): 
            self.check1 = False
            self.check2 = False
            self.check3 = False 
            self.check4 = False
            return (self.feedback_before, self.feedback_after)


#############################################################








    








# if __name__ == '__main__': 
#     pass 

