from pushupAnalysis import *
from legRaiseAnalysis import *
from lungeAnalysis import *
from imageDownscale import *

# Images from 'images/Nov/<workout>' 

# Convert String to List of Body Parts 
def convertString(bodyParts):
    result = [] 
    bodyList = bodyParts.split("_")

    for coordinate in bodyList:
        vals = coordinate.split(",")
        # print(vals)
        row = float(vals[0])
        col = float(vals[1])
        result.append((row, col))

    return result 



def albert():
    legRaisePic = []
    # legRaisePic.append('images/21/legRaise/kneeBent.png')
    # legRaisePic.append('images/21/legRaise/over.png')
    # legRaisePic.append('images/21/legRaise/low.png')
    # legRaisePic.append('images/21/legRaise/1.png')
    # legRaisePic.append('images/21/legRaise/2.png')
    # legRaisePic.append('images/21/legRaise/3.png')
    # legRaisePic.append('images/21/legRaise/perfect.png')

    pushupPic = []
    # pushupPic.append('images/21/pushup/handForward.png')
    # pushupPic.append('images/21/pushup/high.png')
    # pushupPic.append('images/21/pushup/buttHigh.png')
    # pushupPic.append('images/21/pushup/1.png')
    # pushupPic.append('images/21/pushup/2.png')
    # pushupPic.append('images/21/pushup/3.png')
    # pushupPic.append('images/21/pushup/perfect.png')

    defaultLungePic = []
    defaultLungePic.append('images/21/lunge/forward.png')
    defaultLungePic.append('images/21/lunge/high.png')
    defaultLungePic.append('images/21/lunge/1.png')
    defaultLungePic.append('images/21/lunge/3.png')
    defaultLungePic.append('images/21/lunge/perfect.png')

    otherLungePic = []
    otherLungePic.append('images/21/lunge/backward.png')
    otherLungePic.append('images/21/lunge/2.png')

    legRaise = LegRaisePostureAnalysis()
    for picture in legRaisePic: 
        joints = getJoints(picture)
        legRaise.feedbackCalculation(joints)
        result = legRaise.getResult()
        feedback = picture.split("/")[-1] + ": " + str(result)
        print(feedback)
        print("\n")


    pushup = PushupPostureAnalysis()
    for picture in pushupPic: 
        joints = getJoints(picture)
        pushup.feedbackCalculation(joints)
        result = pushup.getResult()
        feedback = picture.split("/")[-1] + ": " + str(result)
        print(feedback)
        print("\n")
    


    lunge = LungePostureAnalysis()
    for picture in defaultLungePic: 
        joints = getJoints(picture)
        lunge.feedbackCalculation(joints)
        result = lunge.getResult()
        feedback = picture.split("/")[-1] + ": " + str(result)
        print(feedback)
        print("\n")
    for picture in otherLungePic: 
        joints = getJoints(picture)
        lunge.feedbackCalculation(joints, False)
        result = lunge.getResult()
        feedback = picture.split("/")[-1] + ": " + str(result)
        print(feedback)
        print("\n")
    return 0


albert()

