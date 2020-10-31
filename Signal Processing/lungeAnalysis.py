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
            self.feedback.append("Straighten your Back")
        if (self.check2): 
            self.feedback.append("Move Front Legs Forward")
        if (self.check3):
            self.feedback.append("Back Knees Should be Lower")

    def getResult(self): 
        self.check1 = False 
        self.check2 = False
        self.check3 = False
        return self.feedback


class LungePostureAnalysis:

    def __init__(self, groundList):
        self.lunge = LungeResult()
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
        line2Slope = self.getSlope(defaultKnee, defaultAnkle)
        line3Slope = self.getSlope(hip, otherKnee)
        line4Slope = self.getSlope(otherKnee, otherAnkle)
        line5Slope = self.getSlope(hip, shoulder)

        angleHip = self.getAngle(shoulder, hip, defaultKnee)
        angleHipOther = self.getAngle(shoulder, hip, otherKnee)
        angleDefaultKnee = self.getAngle(hip, defaultKnee, defaultAnkle)
        angleOtherKnee = self.getAngle(hip, otherKnee, otherAnkle)

        
        # TODO: Make sure that the angle is the y value where ankle touches 
        if not (self.sameSlope(line5Slope, line3Slope) and self.sameAngle(angleHipOther, parallel)):
            self.lunge.check1 = True 
        if not (self.sameAngle(angleDefaultKnee, perpendicular) and self.sameAngle(angleHip, perpendicular) and self.sameSlope(0, line1Slope)):
            self.lunge.check2 = True 
        if not (self.sameSlope(line4Slope, 0) and self.sameAngle(angleOtherKnee, perpendicular)):
            self.lunge.check3 = True 
        
        self.lunge.processResult() 


    def getResult(self): 
        return self.lunge.getResult()
        
    
