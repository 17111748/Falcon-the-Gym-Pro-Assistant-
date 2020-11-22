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
        self.feedback = [] 
        self.check1 = False
        self.check2 = False
        self.check3 = False
        self.check4 = False
        self.invalid = [] 
    

    def processResult(self): 
        self.feedback = []
        if (self.check1):
            self.feedback.append("Position your Hands Slightly Backward")
        if (self.check2):
            self.feedback.append("Go Lower")
        if (self.check3):
            self.feedback.append("Butt is Too High")
        if (self.check4):
            self.feedback.append("Lower Body too Low to the Ground")

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
        self.check4 = False 
        self.invalid = []
        return self.feedback


class PushupPostureAnalysis:
    
    def __init__(self):
        self.pushup = PushupResult()

    # Helper Functions 
    def getSlope(self, pos0, pos1): 
        height = 120 
        y1 = height - pos1[0]
        x1 = pos1[1]
        y0 = height - pos0[0]
        x0 = pos0[1]
        print(x0)
        print(x1)
        print(y0)
        print(y1)

        print(y1 - y0)
        print(x1 - x0)
        print("Run once")
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
        return (pos0 - threshold) < pos1  
    
    def greaterThan(self, pos0, pos1, threshold = 0): 
        return pos0 >= (pos1 - threshold)  

    
    # Line 1: Shoulder - Hip 
    # Line 2: Hip - Knee 
    # Line 3: Knee - Ankle 
    # Line 4: Shoulder - Elbow 
    # Line 5: Elbow - Wrist 
    def feedbackCalculation(self, bodyParts, default=True):

        shoulder = (int(bodyParts[0][0]), int(bodyParts[0][1])) 
        elbow = (int(bodyParts[1][0]), int(bodyParts[1][1])) 
        wrist = (int(bodyParts[2][0]), int(bodyParts[2][1])) 
        hip = (int(bodyParts[3][0]), int(bodyParts[3][1])) 
        knee = (int(bodyParts[4][0]), int(bodyParts[4][1]))
        # ankle = (int(bodyParts[6][0]), int(bodyParts[6][1])) 
        
        if (shoulder[0] == 0 and shoulder[1] == 0):
            self.pushup.invalid.append(0)  

        if (elbow[0] == 0 and elbow[1] == 0):
            self.pushup.invalid.append(1)

        if (wrist[0] == 0 and wrist[1] == 0):
            self.pushup.invalid.append(2)

        if (hip[0] == 0 and hip[1] == 0):
            self.pushup.invalid.append(3)
            
        if (knee[0] == 0 and knee[1] == 0):
            self.pushup.invalid.append(4)

        # if (ankle[0] == 0 and ankle[1] == 0):
        #     self.pushup.invalid.append(6) 
    

        line1Slope = self.getSlope(shoulder, hip)
        # line2Slope = self.getSlope(hip, ankle)
        # line3Slope = self.getSlope(knee, ankle)
        # line4Slope = self.getSlope(shoulder, elbow)
        # line5Slope = self.getSlope(elbow, wrist)
        
        # angleHip = self.getAngle(shoulder, hip, knee)
        # angleKnee = self.getAngle(hip, knee, ankle)

        # # If the Hands are Too Forward
        # print(wrist[1])
        # print(elbow[1])
        # print(self.lessThan(wrist[1], shoulder[1]))
        # print(self.lessThan(wrist[1], elbow[1], 2))

        if not (self.lessThan(wrist[1], shoulder[1]) and self.lessThan(wrist[1], elbow[1], 2)):
            self.pushup.check1 = True
        
        # # Go Lower
        # print(shoulder[0])
        # print(elbow[0])
        # print(self.greaterThan(shoulder[0], elbow[0], 4))

        if not (self.greaterThan(shoulder[0], elbow[0], 4)):
            self.pushup.check2 = True 


        # TODO: 
        # Get Better Pictures to Classify 

        # Check if the slope of shoulder to hip  
        slopeOfShoulder = 0

        # print(line1Slope)
        # print(slopeOfShoulder)
        
        if not (self.greaterThan(line1Slope, slopeOfShoulder, 0)):
            self.pushup.check3 = True 


        # if not (self.greaterThan(wrist[0], knee[0], -1)):
        #     self.pushup.check4 = True 

        self.pushup.processResult() 
        
       
    def getResult(self): 
        return self.pushup.getResult()
        

        
#################################################################

# perfect = [(69.0, 128.5), (73.0, 123.0), (90.5, 120.0), (76.5, 102.5), (79.0, 43.0), (87.5, 81.0), (83.5, 20.0), (0.0, 0.0)]
# handForward = [(71.5, 129.5), (72.5, 121.5), (92.5, 129.5), (81.0, 99.0), (80.0, 40.0), (0.0, 0.0), (84.5, 17.0), (80.5, 38.5)]
# low = [(77.0, 141.5), (72.5, 131.0), (92.0, 129.5), (85.5, 106.5), (84.0, 55.0), (83.0, 103.5), (85.0, 33.0), (0.0, 0.0)]
# high = [(57.5, 127.0), (68.5, 125.5), (88.5, 126.5), (64.0, 100.5), (75.5, 45.0), (82.0, 46.0), (81.5, 21.5), (85.5, 27.0)]
# buttHigh = [(76.0, 138.0), (74.5, 133.5), (92.5, 132.0), (80.0, 108.0), (79.0, 52.0), (75.5, 106.5), (83.0, 29.5), (0.0, 0.0)]
 
test = [(90.5, 133.5), (83.0, 122.5), (89.0, 123.5), (93.5, 96.5), (95.0, 42.5), (0.0, 0.0), (95.0, 14.5), (90.5, 133.5)]

pushup = PushupPostureAnalysis()


pushup.feedbackCalculation(test)
result = pushup.getResult()
print("Perfect: " + str(result))
print("\n")

# pushup.feedbackCalculation(handForward)
# result = pushup.getResult()
# print("handForward: " + str(result))
# print("\n")

# pushup.feedbackCalculation(low)
# result = pushup.getResult()
# print("Low: " + str(result))
# print("\n")

# pushup.feedbackCalculation(high)
# result = pushup.getResult()
# print("High: " + str(result))
# print("\n")

# # TODO: Fix this 
# pushup.feedbackCalculation(buttHigh)
# result = pushup.getResult()
# print("Butt High: " + str(result))