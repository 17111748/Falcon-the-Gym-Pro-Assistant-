
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

class LegRaiseResult: 

    # Feedback
    def __init__(self):
        self.feedback = [] 
        self.check1 = False
        self.check2 = False
        self.check3 = False 
        self.check4 = False
    
    def processResult(self): 
        self.feedback = [] 
        if (self.check1): 
            self.feedback.append("Raise You Legs Higher")
        if (self.check2):
            self.feedback.append("Legs are too High")
        if (self.check3):
            self.feedback.append("Knees are Bent")

    def getResult(self): 
        self.check1 = False
        self.check2 = False
        self.check3 = False 
        return self.feedback

class LegRaisePostureAnalysis:

    def __init__(self, groundList):
        self.legRaise = LegRaiseResult()
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
        return abs(slope1 - slope2) < threshold 

    def sameAngle(self, angle1, angle2, threshold = 0.1): 
        return abs(angle1 - angle2) < threshold 
    
    # Line 1: Shoulder - Hip 
    # Line 2: Hip - Knee 
    # Line 3: Knee - Ankle 
    def feedbackCalculation(self, bodyParts, default=True):

        shoulder = bodyParts[0]
        hip = bodyParts[3]
        knee = bodyParts[4]
        ankle = bodyParts[6]

        line1Slope = self.getSlope(shoulder, hip)
        line2Slope = self.getSlope(hip, knee)
        line3Slope = self.getSlope(knee, ankle)

        # groundSlope = self.getSlope(self.groundList[0], self.groundList[1])
        
        angleHip = self.getAngle(shoulder, hip, knee)
        angleKnee = self.getAngle(hip, knee, ankle)

        if not (self.sameAngle(angleHip, perpendicular)):
            if(angleHip > perpendicular):
                self.legRaise.check1 = True 
            else: 
                self.legRaise.check2 = True 
        
        if not (self.sameAngle(angleKnee, parallel)):
            self.legRaise.check3 = True 

        self.legRaise.processResult()

    def getResult(self): 
        return self.legRaise.getResult() 
        
    


#############################################################

