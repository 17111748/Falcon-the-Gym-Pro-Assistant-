import sys, pygame, cv2, time, threading, queue, serial, random, UI.database, pprint, datetime
from PIL import Image
from UI.structs import *
from UI.colors import *
from UI.stopwatch import stopwatch

import Signal_Processing.legRaiseAnalysis as legRaiseAnalysis
import Signal_Processing.lungeAnalysis as lungeAnalysis
import Signal_Processing.pushupAnalysis as pushupAnalysis

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

def sendPicture(d,workout):
    resized_col = 160
    resized_row = 120

    #temp random stuff
    sample_image_dir = "Signal_Processing\\images\\Nov\\" 
    workoutPhotos = {
        "l": ["lungeForward\\Backward.png","lungeForward\\Forward.png","lungeForward\\Perfect.png"],
        "u": ["pushUp\\HandForward.png","pushUp\\High.png","pushUp\\Perfect.png","pushUp\\Perfect2.png"],
        "c": ["legRaise\\kneeBent.png","legRaise\\Over.png","legRaise\\Perfect.png","legRaise\\Under.png"]
    }

    randInt = random.randint(0,len(workoutPhotos[workout])-1)
   
    original_image = Image.open(sample_image_dir+workoutPhotos[workout][randInt])
    original_image_pixels = original_image.load()

    new_image = original_image.resize((resized_col, resized_row))
    converted_image = new_image.convert('HSV')
    # converted_pixel = converted_image.load()
    byte_arr = converted_image.tobytes()

    locationArray = []
    if(not d.sendPicTest):
        d.ser.write(byte_arr)
        print("sent image: "+workoutPhotos[workout][randInt])
        
        total = b''
        data_received = b''
        while ("\n" not in data_received.decode("utf-8")):
            data_received = d.ser.read(d.ser.in_waiting)
            total += data_received
            # if(len(data_received) != 0):
            #     print(data_received.decode("utf-8"))
        coord_string = total.decode("utf-8")
        locationArray = convertString(coord_string[:-2]) # getting rid of the \n 
        print(locationArray)
    else:
        time.sleep(1.4)
        locationArray = [(71.5, 129.5), (72.5, 121.5), (92.5, 129.5), (81.0, 99.0), (80.0, 40.0), (0.0, 0.0), (84.5, 17.0), (80.5, 38.5)]    
    feedback = ""
    if(workout=="l"):
        d.lungeAnalyzer.feedbackCalculation(locationArray)
        feedback =  d.lungeAnalyzer.getResult()
    elif(workout=="c"):
        d.legRaiseAnalyzer.feedbackCalculation(locationArray)
        feedback = d.legRaiseAnalyzer.getResult()
    elif(workout=="u"):
        d.pushupAnalyzer.feedbackCalculation(locationArray)
        feedback = d.pushupAnalyzer.getResult()
    if(len(feedback)==0):
        d.workoutPerfectCount[workout]+=1
    d.workoutPerfectCount[workout+"_total"]+=1
    d.threadQueue.put(feedback)

def initConstants(d):
    #toggles
    d.UART = False
    d.sendPicTest = True

    #constants
    d.FRAME_FREQUENCY = 100
    d.WINDOW_WIDTH = 1280
    d.WINDOW_HEIGHT = int(d.WINDOW_WIDTH/1.6)
    d.LIVE_VIDEO_DIMS = (int(d.WINDOW_WIDTH*0.5),int(d.WINDOW_HEIGHT*0.5))
    d.IMAGE_DIR = {
       "c": 'UI\\images\\leg_raise\\',
       "l": 'UI\\images\\lunge\\',
       "u": 'UI\\images\\push_up\\'
    }
    d.REPS_PER_SET = 3
    d.SETS_PER_WORKOUT = 3
    d.SET_BREAK_TIME = 5
    d.RESUME_TIME = 3

def initPyCamera(d):
    #setup pygame/camera
    d.camera  = cv2.VideoCapture(0)
    # d.camera = cv2.VideoCapture(1)
    if not d.camera.isOpened():
        print("Could not open video device")
    pygame.init()
    pygame.display.set_caption("OpenCV camera stream on Pygame")
    d.screen = pygame.display.set_mode([d.WINDOW_WIDTH, d.WINDOW_HEIGHT])
    d.live_video = pygame.Surface(d.LIVE_VIDEO_DIMS)
    d.clock = pygame.time.Clock()

def initFrames(d):
    d.workoutTotalFrames = {
        "c": 136, 
        "l": 173,
        "u": 100
    }

    d.captureFrame = {
        "c": 60, 
        "l": 88,
        "u": 55
    }
    
    d.endFeedbackFrame = {
        "c": 16,
        
    }

    #based on rolling AVG of d.clock.tick() of 40ms
    d.timePerFrame = 0.04
    d.workoutRepTime = {
        #120 frames
        "c": d.timePerFrame*d.workoutTotalFrames['c'],
        "u": d.timePerFrame*d.workoutTotalFrames['u'],
        "l": d.timePerFrame*d.workoutTotalFrames['l'],
    }

def initNewWorkout(d):
    d.currSet = 2
    d.calBurned = 0 
    d.currWorkoutFrame = 0
    d.currentRep = 1
    d.timeRemaining = -1
    d.beginTime = pygame.time.get_ticks()
    d.workoutPerfectCount = {
        "l": 0,
        "l_total": 0,
        "c": 0,
        "c_total": 0, 
        "u": 0,
        "u_total": 0  
    }
    d.newWorkout = True
    d.HRTotalLow = 0 
    d.HRTotalHigh = 0
    d.workoutStopwatch.reset()
    d.threadQueue = queue.Queue()

def initWorkouts(d):
    #if focused on core then that is 4 sets rest is 3
    d.workoutSets = {
        "core": ["c","u","l","c","u","l","c","u","l","c"],
        "upper": ["u","c","l","u","c","l","u","c","l","u"],
        "leg": ["l","c","u","l","c","u","l","c","u","l"],
    }
    d.workoutNames = {
        "c": "Leg Raise",
        "l": "Lunges",
        "u": "Push-Ups"
    }
    d.workoutFocus = "core"

    d.workoutHRR = {
        "rest": 0.1,
        "c": 0.4,
        "l": 0.45,
        "u": 0.7
    }
    d.workoutMET = {
        "rest": 1.5,
        "c": 2.23,
        "l": 2.23,
        "u": 7.55
    }

    d.currentScreen = screenMode.WORKOUT
    d.newScreen = True

    d.breakTime = d.SET_BREAK_TIME

    d.resumeFromPause = -1
    d.justResumed = False
    d.pause = False

    d.workoutStopwatch = stopwatch()
    initNewWorkout(d)

def initDBProfile(d):
    d.db = UI.database.database("falcon.db")

    #imperial (inches, pounds)
    d.currProfile = d.db.getLastProfile()
    profileData = d.db.getProfile(d.currProfile)
    d.age = profileData[1]
    d.weight = profileData[2]

def initAnalysis(d):
    if(d.UART):
        d.ser = serial.Serial(port = "COM3",
            baudrate=921600, # Could change to go upto 921600? <- max rate supported by the UARTLite IP block
            bytesize=serial.EIGHTBITS,
            stopbits=serial.STOPBITS_ONE)

    d.legRaiseAnalyzer = legRaiseAnalysis.LegRaisePostureAnalysis()
    d.lungeAnalyzer = lungeAnalysis.LungePostureAnalysis()
    d.pushupAnalyzer = pushupAnalysis.PushupPostureAnalysis()

def init(d):
    initConstants(d)
    initPyCamera(d)
    initFrames(d)
    initWorkouts(d)
    initDBProfile(d)
    initAnalysis(d)

def metToCal(d,workout):
    lbToKg = 0.45359
    #calories per second burned
    return d.workoutMET[workout]*0.0175*(lbToKg*d.weight)/60

def drawMain(d):
    if(d.newScreen):
        #draw start and settings
        #draw 
        d.screen.fill(color.white)
        d.newScreen = False

def updateRepText(d):
    repStr = "Rep: "+str(d.currentRep)+"/"+str(d.REPS_PER_SET)
    textLoc = (int(d.WINDOW_WIDTH*0.15), int(d.WINDOW_HEIGHT*0.21))
    repText = Text(repStr,textLoc,35,color.black,topmode=True)
    repText.draw(d)

def updateWorkoutText(d,currentWorkout):
    workStr = d.workoutNames[currentWorkout]
    textLoc = (int(d.WINDOW_WIDTH*0.025), int(d.WINDOW_HEIGHT*0.025))
    workText = Text(workStr,textLoc,50,color.black,topmode=True)
    workText.draw(d)

def updateSetText(d):
    setStr = "Set: "+str(d.currSet)+"/"+str(d.SETS_PER_WORKOUT)
    textLoc = (int(d.WINDOW_WIDTH*0.025), int(d.WINDOW_HEIGHT*0.21))
    setText = Text(setStr,textLoc,35,color.black,topmode=True)
    setText.draw(d)

def updateTimeText(d,newSet,timeTextResumePause):
    if(not timeTextResumePause):
        if(d.timeRemaining<0 or newSet):
            totalTime = (d.SETS_PER_WORKOUT-(d.currSet-1))*d.SET_BREAK_TIME
            if(d.breakTime<=0):
                totalTime-=d.SET_BREAK_TIME
            for i in range(d.currSet-1,d.SETS_PER_WORKOUT):
                totalTime+= d.workoutRepTime[d.workoutSets[d.workoutFocus][i]]*d.REPS_PER_SET
            d.timeRemaining = totalTime
        else:
            d.timeRemaining-=1
    remainingTime = time.strftime("%M:%S", time.gmtime(d.timeRemaining))
    timeStr = "Time Remaining: "+remainingTime+" "
    textLoc = (int(d.WINDOW_WIDTH*0.025), int(d.WINDOW_HEIGHT*0.11))
    timeText = Text(timeStr,textLoc,35,color.black,topmode=True)
    timeText.draw(d)

    elapsedTime = time.strftime("%M:%S", time.gmtime(d.workoutStopwatch.getTime()))
    timeStr = "Time Elapsed: "+elapsedTime+" "
    textLoc = (int(d.WINDOW_WIDTH*0.025), int(d.WINDOW_HEIGHT*0.16))
    timeText = Text(timeStr,textLoc,35,color.black,topmode=True)
    timeText.draw(d)

def updateBreakString(d):
    breakStr = "Next set in "+str(d.breakTime)+" seconds     "
    if(d.breakTime==1):
        breakStr = "Next set in "+str(d.breakTime)+" second        "
    textLoc = (int(d.WINDOW_WIDTH*0.52), int(d.WINDOW_HEIGHT*0.02))
    breakText = Text(breakStr,textLoc,60,color.red,topmode=True)
    breakText.draw(d)

def updateResumeTimeText(d):
    resumeStr = "Resuming in "+str(d.resumeFromPause)+" seconds     "
    if(d.resumeFromPause==1):
        resumeStr = "Resuming in "+str(d.resumeFromPause)+" second        "
    elif(d.resumeFromPause<0):
        resumeStr = (len(resumeStr)*2)*" "
    textLoc = (int(d.WINDOW_WIDTH*0.52), int(d.WINDOW_HEIGHT*0.02))
    resumeText = Text(resumeStr,textLoc,60,color.red,topmode=True)
    resumeText.draw(d)

def updateCalText(d,workout,reset):
    if(not reset):
        d.calBurned += metToCal(d,workout)
    calStr = '{0:.1f}'.format(d.calBurned)+" Cal  "
    textLoc = (int(d.WINDOW_WIDTH*0.025), int(d.WINDOW_HEIGHT*0.26))
    calText = Text(calStr,textLoc,35,color.black,topmode=True)
    calText.draw(d)

def calcHR(d,workout):
    #220 is max heart rate for new born
    heartRateReserve = 220-d.age
    #64 is assumed heart rate rest on average
    heartRate = heartRateReserve*d.workoutHRR[workout]+64
    lowHeart = str(int(0.95*heartRate))
    highHeart = str(int(1.05*heartRate))
    return (lowHeart,highHeart)

def updateHRText(d,workout):
    lowHeart,highHeart = calcHR(d,workout)
    hrStr = lowHeart+"-"+highHeart+" BPM   " 
    textLoc = (int(d.WINDOW_WIDTH*0.15), int(d.WINDOW_HEIGHT*0.26))
    hrText = Text(hrStr,textLoc,35,color.black,topmode=True)
    hrText.draw(d)    

def drawWorkout(d):
    if(not d.pause):
        if(d.newWorkout):
            initNewWorkout(d)
            d.newWorkout = False
            d.workoutStopwatch.start()
            d.beginWorkoutTime = datetime.datetime.now()
        # test threading
        if(not data.threadQueue.empty()):
            print(data.threadQueue.get())

        currentWorkout = d.workoutSets[d.workoutFocus][d.currSet-1]
        timeTextResumePause = True
        if(d.newScreen):
            #only reset workoutframe and current rep and recalculate time if new set
            if(d.resumeFromPause<0):
                d.currWorkoutFrame = 0
                d.currentRep = 1 
                timeTextResumePause = False

            d.screen.fill(color.white)

            if(d.breakTime>=0):
                updateHRText(d,"rest")
                d.currWorkoutFrame = 0 
            else:
                updateHRText(d,currentWorkout)

            #initialize text
            updateRepText(d)
            updateWorkoutText(d,currentWorkout)
            updateSetText(d)
            updateTimeText(d,True,timeTextResumePause)
            updateCalText(d,currentWorkout,True)
            if(d.breakTime>0):
                updateBreakString(d)

            #draw divider line
            start_line_loc = (int(d.WINDOW_WIDTH*0.45),int(d.WINDOW_HEIGHT*0.225))
            end_line_loc = (int(d.WINDOW_WIDTH*0.45),int(d.WINDOW_HEIGHT*0.85))
            pygame.draw.line(d.screen, color.black, start_line_loc, end_line_loc, 3)

            d.beginTime = pygame.time.get_ticks()
            
            d.newScreen = False

        #take photo and upate live video
        ret, frame = d.camera.read()
        if(ret is False): return False
        frame = cv2.resize(frame, d.LIVE_VIDEO_DIMS, interpolation = cv2.INTER_AREA)
        frame = frame.swapaxes(0,1)
        frame = cv2.flip(frame,0)
        live_loc = (int(d.WINDOW_WIDTH*0.48),int(d.WINDOW_HEIGHT*0.275))
        d.screen.blit(d.live_video, live_loc)
        pygame.surfarray.blit_array(d.live_video, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        #send to FPGA for processing
        if(d.currWorkoutFrame == d.captureFrame[currentWorkout] and d.breakTime<0 and d.resumeFromPause<0):
            #TODO
            toDownsize = frame.swapaxes(0,1)
            # print('photo captured')
            # Depending on exercise add a d.ser.write before you write the byte_arr.
            # Write \x00 for lunges, \x01 for push ups, x\02 for leg raise
            # d.ser.write(b'\x01')
            # d.ser.write(byte_arr)
            if(d.UART or d.sendPicTest):
                serialThread = threading.Thread(target=sendPicture,name="FPGA_SERIAL",args=[d,currentWorkout],daemon=True)
                serialThread.start()

        #incrementing rep and updating model
        if(d.breakTime < 0 or d.currWorkoutFrame==0):
            if(d.resumeFromPause>=0):
                updateResumeTimeText(d)
            if(d.resumeFromPause<0 or d.justResumed):
                if(d.resumeFromPause<0):
                    d.workoutStopwatch.start()
                if(d.justResumed and d.currWorkoutFrame>0):
                    d.currWorkoutFrame-=1
                d.justResumed = False
                #incrementing rep if needed
                if(d.currWorkoutFrame>=d.workoutTotalFrames[currentWorkout]):
                    d.currentRep+=1   
                    d.currWorkoutFrame=0
                    #next set
                    if(d.currentRep>d.REPS_PER_SET):
                        d.currentRep = 1 
                        d.currSet+=1
                        #workout done
                        if(d.currSet>d.SETS_PER_WORKOUT):
                            d.workoutStopwatch.stop()
                            #save finishing data
                            timeEnd = datetime.datetime.now()
                            avgHRLow = d.HRTotalLow/d.workoutStopwatch.getTime()
                            avgHRHigh = d.HRTotalHigh/d.workoutStopwatch.getTime()
                            d.avgHR = (avgHRHigh+avgHRLow)/2
                            d.db.addWorkout(d.workoutFocus,d.workoutStopwatch.getTime(),d.beginWorkoutTime,timeEnd,d.calBurned,d.avgHR,d.currProfile)
                            #return true so that main function proceeds to draw summary
                            return True
                        d.breakTime = d.SET_BREAK_TIME
                        d.newScreen=True
                        return True
                    updateRepText(d)

                #update model image
                modelLocation = (int(d.WINDOW_WIDTH*0.02), int(d.WINDOW_HEIGHT*0.31))
                d.screen.blit(pygame.image.load(d.IMAGE_DIR[currentWorkout]+"{:03n}".format(d.currWorkoutFrame)+'.gif'),modelLocation)
                d.currWorkoutFrame+=1

        #timer based (time left, next set break, resume, calories burned)
        currTime = pygame.time.get_ticks()
        if(currTime-d.beginTime>1000):
            #not resuming from pause
            if(d.resumeFromPause<0):
                #decrement time remaining
                updateTimeText(d,False,False)
                #if on a break
                if(d.breakTime>0):
                    d.breakTime-=1
                    #break over
                    if(d.breakTime==0):
                        d.newScreen = True
                        d.breakTime = -1
                    else:
                        updateBreakString(d)
                    updateCalText(d,"rest",False)
                    low,high = calcHR(d,"rest")
                    d.HRTotalLow+=int(low)
                    d.HRTotalHigh+=int(high)
                else:
                    updateCalText(d,currentWorkout,False)
                    low,high = calcHR(d,currentWorkout)
                    d.HRTotalLow+=int(low)
                    d.HRTotalHigh+=int(high)
            #resuming from pause
            else:
                d.resumeFromPause-=1
                if(d.resumeFromPause==0):
                    d.resumeFromPause = -1
                    updateResumeTimeText(d)
            d.beginTime = currTime
        
def drawSummary(d):
    if(d.newScreen):
        d.screen.fill(color.white)

        titleStr = "Workout Summary"
        textLoc = (int(d.WINDOW_WIDTH*0.5), int(d.WINDOW_HEIGHT*0.1))
        titleText = Text(titleStr,textLoc,60,color.black,topmode=False)
        titleText.draw(d)

        caloriesStr = "Active Calories: "+'{0:.1f}'.format(d.calBurned)
        textLoc = (int(d.WINDOW_WIDTH*0.5), int(d.WINDOW_HEIGHT*0.18))
        caloriesText = Text(caloriesStr,textLoc,30,color.black,topmode=False)
        caloriesText.draw(d)

        #temp summary
        pushUpStr = "Perfect Pushups: "+str(d.workoutPerfectCount["u"])+"/"+str(d.workoutPerfectCount["u_total"])
        textLoc = (int(d.WINDOW_WIDTH*0.5), int(d.WINDOW_HEIGHT*0.23))
        pushText = Text(pushUpStr,textLoc,30,color.black,topmode=False)
        pushText.draw(d)
        coreStr = "Perfect Leg Raises: "+str(d.workoutPerfectCount["c"])+"/"+str(d.workoutPerfectCount["c_total"])
        textLoc = (int(d.WINDOW_WIDTH*0.5), int(d.WINDOW_HEIGHT*0.28))
        coreText = Text(coreStr,textLoc,30,color.black,topmode=False)
        coreText.draw(d)
        lungeStr = "Perfect Lunges: "+str(d.workoutPerfectCount["l"])+"/"+str(d.workoutPerfectCount["l_total"])
        textLoc = (int(d.WINDOW_WIDTH*0.5), int(d.WINDOW_HEIGHT*0.33))
        lungeText = Text(lungeStr,textLoc,30,color.black,topmode=False)
        lungeText.draw(d)

        d.newScreen = False

def drawPause(d):
        #create transparent layer when pausing
    s = pygame.Surface((d.WINDOW_WIDTH,d.WINDOW_HEIGHT)) 
    s.set_alpha(200)      
    s.fill((255,255,255)) 
    d.screen.blit(s, (0,0))

    textLoc = (int(d.WINDOW_WIDTH*0.5), int(d.WINDOW_HEIGHT*0.4))
    pauseText = Text("PAUSED",textLoc,100,color.black,topmode=False,transparent=True)
    pauseText.draw(d)

    resumeMsg = "Press the Escape Key to Resume Your Workout"
    textLoc = (int(d.WINDOW_WIDTH*0.5), int(d.WINDOW_HEIGHT*0.55))
    pauseTextRes = Text(resumeMsg,textLoc,50,color.black,topmode=False,transparent=True)
    pauseTextRes.draw(d)

def main(d):
    frames = 0 
    rollingAvg = 0
    while True:
        if(d.currentScreen == screenMode.MAIN):
            drawMain(d) 
        elif(d.currentScreen == screenMode.WORKOUT):
            setOrWorkoutFinished = drawWorkout(d)
            #draw workout returns true if finished set or workout
            if(setOrWorkoutFinished):
                if(d.currSet>d.SETS_PER_WORKOUT):
                    d.currentScreen=screenMode.SUMMARY
                    d.newScreen = True
        elif(d.currentScreen == screenMode.SUMMARY):
            drawSummary(d)
        pygame.display.update()
        pygameHandleEvent(d)
        # rollingAvg = (rollingAvg*frames+d.clock.tick(25))/(frames+1)
        # frames+=1
        # print(rollingAvg)
        d.clock.tick(30)

def pygameHandleEvent(d):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            d.db.cursor.close()
            sys.exit(0)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                print(d.workoutStopwatch.getTime())
                if(d.currentScreen == screenMode.WORKOUT):
                    if(d.pause):
                        d.newScreen = True
                        if(d.breakTime<0):
                            d.resumeFromPause = d.RESUME_TIME
                            d.justResumed = True
                        d.pause = False
                    else:
                        drawPause(d)
                        d.pause = True
                        d.workoutStopwatch.stop()

data = data()
init(data)
main(data)