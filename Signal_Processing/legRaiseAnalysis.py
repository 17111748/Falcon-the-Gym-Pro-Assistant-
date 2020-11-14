import numpy as np

expectedHipAngle = 110 
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
        self.invalid = False 
        self.check1 = False
        self.check2 = False
        self.check3 = False 
        self.check4 = False
    
    def processResult(self): 
        self.feedback = [] 
        if (self.check1): 
            self.feedback.append("Raise Your Legs Higher")
        if (self.check2):
            self.feedback.append("Over-Extending")
        if (self.check3):
            self.feedback.append("Knees are Bent")
        
        if (self.invalid): 
            self.feedback = []
            self.feedback.append("Invalid Joint Detection")

    def getResult(self): 
        self.check1 = False
        self.check2 = False
        self.check3 = False 
        self.invalid = False 
        return self.feedback

class LegRaisePostureAnalysis:

    def __init__(self):
        self.legRaise = LegRaiseResult()

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
                self.invalid = True 
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
    
    # Line 1: Shoulder - Hip 
    # Line 2: Hip - Knee 
    # Line 3: Knee - Ankle 
    def feedbackCalculation(self, bodyParts, default=True):

        shoulder = bodyParts[0]
        hip = bodyParts[3]
        knee = bodyParts[4]
        ankle = bodyParts[6]

        if ((int(shoulder[0]) == 0 and int(shoulder[1]) == 0) or 
            (int(hip[0]) == 0 and int(hip[1]) == 0) or 
            (int(knee[0]) == 0 and int(knee[1]) == 0) or 
            (int(ankle[0]) == 0 and int(ankle[1]) == 0)):
            self.invalid = True 

        # line1Slope = self.getSlope(shoulder, hip)
        # line2Slope = self.getSlope(hip, knee)
        # line3Slope = self.getSlope(knee, ankle)

        angleHip = self.getAngle(shoulder, hip, knee)
        angleKnee = self.getAngle(hip, knee, ankle)

        if not (self.sameAngle(angleHip, expectedHipAngle, 5)):
            if(angleHip > expectedHipAngle):
                self.legRaise.check1 = True 
            else: 
                self.legRaise.check2 = True 
        
        if not (self.sameAngle(angleKnee, parallel, 10)):
            self.legRaise.check3 = True 

        self.legRaise.processResult()

    def getResult(self): 
        return self.legRaise.getResult() 



# NOTE:
# Raise your Legs Higher. Since we are tracking the hip and not the butt. Therefore, a pefect would be slanted. 110 degrees with +/- 5 degrees


#############################################################


# perfect = [(91.5, 33.5), (96.0, 49.0), (96.0, 65.5), (88.0, 55.5), (41.5, 66.5), (46.0, 72.0), (22.0, 70.0), (27.0, 75.0)]
# over = [(93.0, 32.0), (96.5, 47.5), (97.0, 66.0), (83.5, 49.0), (40.5, 36.5), (42.5, 42.5), (21.5, 35.0), (24.5, 37.5)]
# under = [(92.5, 32.5), (96.5, 48.5), (97.0, 66.0), (89.5, 56.0), (49.5, 81.5), (90.0, 59.0), (33.5, 90.5), (0.0, 0.0)]
# kneeBent = [(92.0, 33.0), (96.5, 48.5), (97.0, 65.0), (89.5, 56.5), (45.5, 63.5), (51.0, 70.0), (31.0, 77.0), (35.5, 80.5)]

# legRaise = LegRaisePostureAnalysis()


# legRaise.feedbackCalculation(perfect)
# result = legRaise.getResult()
# print("Perfect: " + str(result))
# print("\n")

# legRaise.feedbackCalculation(over)
# result = legRaise.getResult()
# print("Over: " + str(result))
# print("\n")

# legRaise.feedbackCalculation(under)
# result = legRaise.getResult()
# print("Under: " + str(result))
# print("\n")

# legRaise.feedbackCalculation(kneeBent)
# result = legRaise.getResult()
# print("Knee Bent: " + str(result))
