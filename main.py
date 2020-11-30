import matplotlib
matplotlib.use("Agg") # Need this before importing any other matplotlib modules
import matplotlib.pyplot as plt
import matplotlib.backends.backend_agg as agg

import sys, pygame, cv2, time, threading, queue, serial, random, UI.database, pprint, datetime, os

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
    print("sending picture of:", workout)
    resized_col = 160
    resized_row = 120

    #temp random stuff
    sample_image_dir = os.path.join("Signal_Processing", "images", "Nov", "") 
    workoutPhotos = {
        "l_r": [os.path.join("lungeForward", "Backward.png"), os.path.join("lungeForward", "Forward.png"), os.path.join("lungeForward", "Perfect.png")],
        "l_l": [os.path.join("lungeForward", "Backward.png"), os.path.join("lungeForward", "Forward.png"), os.path.join("lungeForward", "Perfect.png")],
        "u": [os.path.join("pushUp", "HandForward.png"), os.path.join("pushUp", "High.png"), os.path.join("pushUp", "Perfect.png"), os.path.join("pushUp", "Perfect2.png")],
        "c": [os.path.join("legRaise", "kneeBent.png"), os.path.join("legRaise", "Over.png"), os.path.join("legRaise", "Perfect.png"), os.path.join("legRaise", "Under.png")]
    }

    randInt = random.randint(0,len(workoutPhotos[workout])-1)

    
    original_image = None
    if(d.useRandomSavedPics):
        print("sent image: "+workoutPhotos[workout][randInt])
        original_image = Image.open(sample_image_dir+workoutPhotos[workout][randInt])
    else:
        original_image = Image.open(d.CAPTURE_IMAGE)
    original_image_pixels = original_image.load()

    new_image = original_image.resize((resized_col, resized_row))
    converted_image = new_image.convert('HSV')
    workout_key = "l" if (workout=="l_l" or workout=="l_r") else workout
    byte_arr = d.UART_WORKOUT_KEY[workout_key]+converted_image.tobytes()

    locationArray = []
    if(d.UART):
        d.ser.write(byte_arr)
        
        total = b''
        data_received = b''
        while ("\n" not in data_received.decode("utf-8")):
            data_received = d.ser.read(d.ser.in_waiting)
            total += data_received

        coord_string = total.decode("utf-8")
        locationArray = convertString(coord_string[:-2]) # getting rid of the \n 
        print(locationArray)
    else:
        time.sleep(1.4)
        locationArray = [(71.5, 129.5), (72.5, 121.5), (92.5, 129.5), (81.0, 99.0), (80.0, 40.0), (0.0, 0.0), (84.5, 17.0), (80.5, 38.5)]    
    feedback = ""
    if(workout=="l_l"):
        d.lungeAnalyzer.feedbackCalculation(locationArray,False)
        feedback =  d.lungeAnalyzer.getResult()
    elif(workout=="l_r"):
        d.lungeAnalyzer.feedbackCalculation(locationArray,True)
        feedback =  d.lungeAnalyzer.getResult()
    elif(workout=="c"):
        d.legRaiseAnalyzer.feedbackCalculation(locationArray)
        feedback = d.legRaiseAnalyzer.getResult()
    elif(workout=="u"):
        d.pushupAnalyzer.feedbackCalculation(locationArray)
        feedback = d.pushupAnalyzer.getResult()
    if(len(feedback)==0):
        d.workoutPerfectCount[workout_key]+=1

    print(feedback)

    d.workoutPerfectCount[workout_key+"_total"]+=1
    d.threadQueue.put(feedback)

def initConstants(d):
    #toggles
    d.UART = False
    d.useRandomSavedPics = False

    #constants
    d.FRAME_FREQUENCY = 100
    d.WINDOW_WIDTH = 1280
    d.WINDOW_HEIGHT = int(d.WINDOW_WIDTH/1.6)
    d.LIVE_VIDEO_DIMS = (int(d.WINDOW_WIDTH*0.5),int(d.WINDOW_HEIGHT*0.5))
    d.CAPTURE_IMAGE = os.path.join("captured.png")
    d.IMAGE_DIR = {
       "c": os.path.join("UI", "images", "leg_raise", ""),
       "l_r": os.path.join("UI", "images", "lunge_right", ""),
       "l_l": os.path.join("UI", "images", "lunge_left", ""),
       "u": os.path.join("UI", "images", "push_up", "")
    }
    d.REPS_PER_SET = 1
    d.SETS_PER_WORKOUT = 4
    d.SET_BREAK_TIME = 1
    d.RESUME_TIME = 3
    #about 2s at 0.04s per rep
    d.END_SET_FRAME_COUNT = 50
    d.UART_WORKOUT_KEY = {
        "l": b'\x00',
        "u": b'\x01',
        "c": b'\x02' 
    }
    d.feedbackAudioVolume = 1.0

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
    
    pygame.mixer.init()
    pygame.mixer.music.set_volume(d.feedbackAudioVolume)

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

    #based on rolling AVG of d.clock.tick() of 40ms
    d.timePerFrame = 0.04
    d.workoutRepTime = {
        #120 frames
        "c": d.timePerFrame*d.workoutTotalFrames['c'],
        "u": d.timePerFrame*d.workoutTotalFrames['u'],
        "l": d.timePerFrame*d.workoutTotalFrames['l'],
    }

def initNewWorkout(d):
    d.currSet = 1
    d.calBurned = 0 
    d.avgHR = 0
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
        "l_r": "Lunge (Right Forward)   ",
        "l_l": "Lunge (Left Forward)   ",
        "u": "Push-Up"
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

    d.newScreen = True

    d.breakTime = d.SET_BREAK_TIME

    d.resumeFromPause = -1
    d.justResumed = False
    d.pause = False

    d.displayFeedback = ""

    d.workoutStopwatch = stopwatch()
    d.feedbackStopwatch = stopwatch()
    initNewWorkout(d)

def initDBProfile(d):
    d.db = UI.database.database("falcon.db")

    #imperial (inches, pounds)
    d.currProfile = d.db.getLastProfile()
    profileData = d.db.getProfile(d.currProfile)
    d.age = profileData[2]
    d.weight = profileData[1]

def initAnalysis(d):
    if(d.UART):
        d.ser = serial.Serial(port = "COM3",
            baudrate=921600,
            bytesize=serial.EIGHTBITS,
            stopbits=serial.STOPBITS_ONE)

    d.legRaiseAnalyzer = legRaiseAnalysis.LegRaisePostureAnalysis()
    d.lungeAnalyzer = lungeAnalysis.LungePostureAnalysis()
    d.pushupAnalyzer = pushupAnalysis.PushupPostureAnalysis()

def initHistory(d):
    d.buttons = []
    d.workout = None
    d.pageNum = 0
    d.screenChangeTime = 0

def initSummary(d):
    x,y = (int(d.WINDOW_WIDTH*0.5),int(d.WINDOW_HEIGHT*0.75))
    w,h =  (int(d.WINDOW_WIDTH*.2),int(d.WINDOW_HEIGHT*0.1))
    d.mainButton = Button(x,y,w,h,color.black,"Main Menu",textSize=32)

def init(d):
    d.currentScreen = screenMode.WORKOUT
    initConstants(d)
    initPyCamera(d)
    initFrames(d)
    initWorkouts(d)
    initDBProfile(d)
    initAnalysis(d)
    initHistory(d)
    initSummary(d)

def metToCal(d,workout):
    lbToKg = 0.45359
    #calories per second burned
    return d.workoutMET[workout]*0.0175*(lbToKg*d.weight)/60

def updateRepText(d):
    repStr = "Rep: "+str(d.currentRep)+"/"+str(d.REPS_PER_SET)
    textLoc = (int(d.WINDOW_WIDTH*0.15), int(d.WINDOW_HEIGHT*0.21))
    repText = Text(repStr,textLoc,35,color.black,topmode=True)
    repText.draw(d)

def updateWorkoutText(d,currentWorkout):
    actualWorkout = currentWorkout 
    if(currentWorkout=="l"):
        actualWorkout = "l_r" if (d.currentRep%2==1) else "l_l"
    workStr = d.workoutNames[actualWorkout]
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
                totalTime+=d.END_SET_FRAME_COUNT*d.timePerFrame
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
    textLoc = (int(d.WINDOW_WIDTH*0.45), int(d.WINDOW_HEIGHT*0.02))
    breakText = Text(breakStr,textLoc,60,color.blue,topmode=True)
    breakText.draw(d)

def updateFeedbackString(d):
    fString = d.displayFeedback
    textLoc = (int(d.WINDOW_WIDTH*0.45), int(d.WINDOW_HEIGHT*0.11))
    breakText = Text(fString,textLoc,45,color.red,topmode=True)
    breakText.draw(d)

def updateResumeTimeText(d):
    resumeStr = "Resuming in "+str(d.resumeFromPause)+" seconds     "
    if(d.resumeFromPause==1):
        resumeStr = "Resuming in "+str(d.resumeFromPause)+" second        "
    elif(d.resumeFromPause<0):
        resumeStr = (len(resumeStr)*2)*" "
    textLoc = (int(d.WINDOW_WIDTH*0.45), int(d.WINDOW_HEIGHT*0.02))
    resumeText = Text(resumeStr,textLoc,60,color.blue,topmode=True)
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
        if(d.feedbackStopwatch.getTime()>2):
            d.feedbackStopwatch.reset()
            d.displayFeedback=(len(d.displayFeedback)*3)*" "
        updateFeedbackString(d)


        if(d.newWorkout):
            initNewWorkout(d)
            d.newWorkout = False
            d.workoutStopwatch.start()
            d.beginWorkoutTime = datetime.datetime.now()
        # test threading
        if(not d.threadQueue.empty()):
            feedbackAudio = os.path.join("audioFiles","perfect.mp3")
            feedback = d.threadQueue.get()
            if(len(feedback)>0):
                #if some feedback is not tuple with audio then just take feedback
                d.displayFeedback = feedback[0]
                if(not isinstance(d.displayFeedback,str)):
                    d.displayFeedback = feedback[0][0]
                    feedbackAudio = feedback[0][1]
            else:
                d.displayFeedback = "Perfect Rep!"
            d.feedbackStopwatch.reset()
            d.feedbackStopwatch.start()

            pygame.mixer.music.load(feedbackAudio)
            pygame.mixer.music.play()

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
            start_line_loc = (int(d.WINDOW_WIDTH*0.45),int(d.WINDOW_HEIGHT*0.28))
            end_line_loc = (int(d.WINDOW_WIDTH*0.45),int(d.WINDOW_HEIGHT*0.92))
            pygame.draw.line(d.screen, color.black, start_line_loc, end_line_loc, 3)

            d.beginTime = pygame.time.get_ticks()
            
            d.newScreen = False

        #take photo and upate live video
        ret, frame = d.camera.read()
        if(ret is False): return False
        frame = cv2.resize(frame, d.LIVE_VIDEO_DIMS, interpolation = cv2.INTER_AREA)
        frame = frame.swapaxes(0,1)
        frame = cv2.flip(frame,0)
        live_loc = (int(d.WINDOW_WIDTH*0.48),int(d.WINDOW_HEIGHT*0.35))
        d.screen.blit(d.live_video, live_loc)
        pygame.surfarray.blit_array(d.live_video, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        #send to FPGA for processing
        if(d.currWorkoutFrame == d.captureFrame[currentWorkout] and d.breakTime<0 and d.resumeFromPause<0):
            #TODO
            toDownsize = frame.swapaxes(0,1)
            flippedFrame = cv2.flip(toDownsize,1)

            cv2.imwrite(d.CAPTURE_IMAGE,flippedFrame)
            print('photo captured')
            imCurrentWorkout = currentWorkout
            if(currentWorkout=="l"):
                imCurrentWorkout = "l_r" if (d.currentRep%2==1) else "l_l"

            serialThread = threading.Thread(target=sendPicture,name="FPGA_SERIAL",args=[d,imCurrentWorkout],daemon=True)
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
                #incrementing rep if needed, if last rep of set use extra frames
                if((d.currWorkoutFrame>=d.workoutTotalFrames[currentWorkout] and d.currentRep<d.REPS_PER_SET)
                    or d.currWorkoutFrame>=d.workoutTotalFrames[currentWorkout]+d.END_SET_FRAME_COUNT):
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
                            d.db.addWorkout(d.workoutFocus,d.workoutStopwatch.getTime(),d.beginWorkoutTime,timeEnd,d.calBurned,d.avgHR,d.currProfile,d.workoutPerfectCount)
                            #return true so that main function proceeds to draw summary
                            return True
                        d.breakTime = d.SET_BREAK_TIME
                        d.newScreen=True
                        return True
                    updateRepText(d)
                    updateWorkoutText(d,currentWorkout)

                #update model image
                modelLocation = (int(d.WINDOW_WIDTH*0.02), int(d.WINDOW_HEIGHT*0.35))
                imCurrentWorkout = currentWorkout
                if(currentWorkout=="l"):
                    imCurrentWorkout = "l_r" if (d.currentRep%2==1) else "l_l"

                d.screen.blit(pygame.image.load(d.IMAGE_DIR[imCurrentWorkout]+"{:03n}".format(d.currWorkoutFrame)+'.gif'),modelLocation)
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
    d.screen.fill(color.white)

    titleStr = "Workout Summary"
    textLoc = (int(d.WINDOW_WIDTH*0.5), int(d.WINDOW_HEIGHT*0.1))
    titleText = Text(titleStr,textLoc,60,color.black,topmode=False)
    titleText.draw(d)

    time = d.workoutStopwatch.getTime()
    m, s = divmod(int(time), 60)
    h, m = divmod(m, 60)
    durationStr = "Workout Duration: "+(f'{m:02d}:{s:02d}')
    textLoc = (int(d.WINDOW_WIDTH*0.5), int(d.WINDOW_HEIGHT*0.18))
    durationText = Text(durationStr,textLoc,35,color.black,topmode=False)
    durationText.draw(d)

    initHeight = d.WINDOW_HEIGHT*0.23
    lineHeight = d.WINDOW_HEIGHT*0.05
    caloriesStr = "Active Calories: "+'{0:.1f}'.format(d.calBurned)
    textLoc = (int(d.WINDOW_WIDTH*0.5), int(int(initHeight+0*lineHeight)))
    caloriesText = Text(caloriesStr,textLoc,30,color.black,topmode=False)
    caloriesText.draw(d)
    HRstr = "Average Heart Rate: "+'{0:.1f}'.format(d.avgHR)
    textLoc = (int(d.WINDOW_WIDTH*0.5), int(int(initHeight+1*lineHeight)))
    hrtext = Text(HRstr,textLoc,30,color.black,topmode=False)
    hrtext.draw(d)

    initHeight = d.WINDOW_HEIGHT*0.4
    pushUpStr = "Perfect Pushups: "+str(d.workoutPerfectCount["u"])+"/"+str(d.workoutPerfectCount["u_total"])
    textLoc = (int(d.WINDOW_WIDTH*0.5), int(initHeight+0*lineHeight))
    pushText = Text(pushUpStr,textLoc,30,color.black,topmode=False)
    pushText.draw(d)
    coreStr = "Perfect Leg Raises: "+str(d.workoutPerfectCount["c"])+"/"+str(d.workoutPerfectCount["c_total"])
    textLoc = (int(d.WINDOW_WIDTH*0.5), int(initHeight+1*lineHeight))
    coreText = Text(coreStr,textLoc,30,color.black,topmode=False)
    coreText.draw(d)
    lungeStr = "Perfect Lunges: "+str(d.workoutPerfectCount["l"])+"/"+str(d.workoutPerfectCount["l_total"])
    textLoc = (int(d.WINDOW_WIDTH*0.5), int(initHeight+2*lineHeight))
    lungeText = Text(lungeStr,textLoc,30,color.black,topmode=False)
    lungeText.draw(d)
    d.newScreen = False

    #handle mouse
    clicked = d.mainButton.handle_mouse()
    d.mainButton.draw(d)
    if(clicked):
        d.newScreen = True
        d.currentScreen = screenMode.MAIN

# Set dataLength to 0 if dont want the navigation buttons to show up
def drawScreenChangeButtons(d, previousScreen, dataLength):
    # Back button
    x = int(d.WINDOW_WIDTH * 0.1)
    y = int(d.WINDOW_HEIGHT * 0.1)
    w = int(d.WINDOW_HEIGHT * 0.13)
    h = int(d.WINDOW_HEIGHT * 0.13)

    normalBack = os.path.join("UI","images","icons","back_og.png")
    highlightedBack = os.path.join("UI","images","icons","back_highlighted.png")
    backButton = ImageButton(x, y, w, h, color.black, "back", normalImg = normalBack, highlightedImg = highlightedBack)
    currTime = pygame.time.get_ticks()
    if(backButton.handle_mouse() and currTime - d.screenChangeTime > 250):
        d.newScreen = True
        d.currentScreen = previousScreen
        d.screenChangeTime = pygame.time.get_ticks()
        d.pageNum = 0
    backButton.draw(d)

    # Trends button
    x = int(d.WINDOW_WIDTH * 0.9)

    normalTrends = os.path.join("UI","images","icons","trends_og.png")
    highlightedTrends = os.path.join("UI","images","icons","trends_highlighted.png")
    trendsButton = ImageButton(x, y, w, h, color.black, "back", normalImg = normalTrends, highlightedImg = highlightedTrends)
    if(trendsButton.handle_mouse()):
        d.newScreen = True
        d.currentScreen = screenMode.HISTORYTRENDS
        d.pageNum = 0
    trendsButton.draw(d)

    # Left button
    x = int(d.WINDOW_WIDTH * 0.1)
    y = int(d.WINDOW_HEIGHT * 0.6)
    w = int(d.WINDOW_HEIGHT * 0.1)
    h = int(d.WINDOW_HEIGHT * 0.1)

    normalLeft = os.path.join("UI","images","icons","left_og.png")
    highlightedLeft = os.path.join("UI","images","icons","left_highlighted.png")
    leftButton = ImageButton(x, y, w, h, color.black, "left", normalImg = normalLeft, highlightedImg = highlightedLeft)
    currTime = pygame.time.get_ticks()
    if(leftButton.handle_mouse() and currTime - d.screenChangeTime > 250):
        if dataLength - (5 * (d.pageNum + 1)) > 0:
            d.pageNum += 1
        d.screenChangeTime = pygame.time.get_ticks()
    if dataLength - (5 * (d.pageNum + 1)) > 0:
        leftButton.draw(d)

    # Right button
    x = int(d.WINDOW_WIDTH * 0.9)
    y = int(d.WINDOW_HEIGHT * 0.6)

    normalRight = os.path.join("UI","images","icons","right_og.png")
    highlightedRight = os.path.join("UI","images","icons","right_highlighted.png")
    rightButton = ImageButton(x, y, w, h, color.black, "left", normalImg = normalRight, highlightedImg = highlightedRight)
    currTime = pygame.time.get_ticks()
    if(rightButton.handle_mouse() and currTime - d.screenChangeTime > 250):
        if d.pageNum > 0:
            d.pageNum -= 1
        d.screenChangeTime = pygame.time.get_ticks()
    if d.pageNum > 0:
        rightButton.draw(d)

def drawHistoryOptions(d):
    if(d.newScreen):
        d.screen.fill(color.white)

        titleStr = "Workout History"
        textLoc = (int(d.WINDOW_WIDTH*0.5), int(d.WINDOW_HEIGHT*0.1))
        titleText = Text(titleStr,textLoc,60,color.black,topmode=False)
        titleText.draw(d)

        chooseStr = "Select a workout to analyze"
        textLoc = (int(d.WINDOW_WIDTH*0.5), int(d.WINDOW_HEIGHT*0.18))
        chooseText = Text(chooseStr,textLoc,30,color.black,topmode=False)
        chooseText.draw(d)

        allData = d.db.getWorkouts(d.currProfile)
        endIndex = len(allData) - (d.pageNum * 5)
        startIndex = max(0, endIndex  - 5)
        data = allData[startIndex:endIndex]

        # Displaying the set of options
        for i in range (len(data)):
            workout = data[len(data)-i-1]
            optionStr = workout[2]
            option = Button(int(d.WINDOW_WIDTH * 0.5), int(d.WINDOW_HEIGHT * 0.35 + 100 * i), int(0.6 * d.WINDOW_WIDTH), 50, color.black, optionStr, info = workout)
            if(option.handle_mouse()):  
                d.currentScreen = screenMode.HISTORYSUMMARY
                d.workout = workout
                d.pageNum = 0
            option.draw(d)
        
        drawScreenChangeButtons(d, screenMode.MAIN, len(allData))

def drawSummaryInfo(d):
    titleStr = "Workout History"
    textLoc = (int(d.WINDOW_WIDTH*0.5), int(d.WINDOW_HEIGHT*0.1))
    titleText = Text(titleStr,textLoc,60,color.black,topmode=False)
    titleText.draw(d)

    workoutStr = "Workout on "+ d.workout[2]
    textLoc = (int(d.WINDOW_WIDTH*0.5), int(d.WINDOW_HEIGHT*0.18))
    workoutText = Text(workoutStr,textLoc,30,color.black,topmode=False)
    workoutText.draw(d)

    focusStr = "Focus: "+ d.workout[0]
    textLoc = (int(d.WINDOW_WIDTH*0.5), int(d.WINDOW_HEIGHT*0.23))
    focusText = Text(focusStr,textLoc,30,color.black,topmode=False)
    focusText.draw(d)

    durationStr = "Duration: "+ str(d.workout[1])
    textLoc = (int(d.WINDOW_WIDTH*0.5), int(d.WINDOW_HEIGHT*0.28))
    durationText = Text(durationStr,textLoc,30,color.black,topmode=False)
    durationText.draw(d)
    
    caloriesStr = "Calories Burned: "+'{0:.1f}'.format(d.workout[4])
    textLoc = (int(d.WINDOW_WIDTH*0.5), int(d.WINDOW_HEIGHT*0.33))
    caloriesText = Text(caloriesStr,textLoc,30,color.black,topmode=False)
    caloriesText.draw(d)

    heartRateStr = "Average Heart Rate: "+'{0:.1f}'.format(d.workout[5])
    textLoc = (int(d.WINDOW_WIDTH*0.5), int(d.WINDOW_HEIGHT*0.38))
    heartRateText = Text(heartRateStr,textLoc,30,color.black,topmode=False)
    heartRateText.draw(d)

def drawSummaryGraphInfo(d):
    # Params
    perfectPushup = d.workout[7]
    imperfectPushup = d.workout[8] - d.workout[7]
    perfectLegRaise = d.workout[9]
    imperfectLegRaise = d.workout[10] - d.workout[9]
    perfectLunge = d.workout[11]
    imperfectLunge = d.workout[12] - d.workout[11]

    pushupStr = "Pushups: "
    textLoc = (int(d.WINDOW_WIDTH*0.07), int(d.WINDOW_HEIGHT*0.50))
    pushupText = Text(pushupStr,textLoc,30,color.black,topmode=True)
    pushupText.draw(d)

    if (perfectPushup + imperfectPushup) != 0:
        pushupValStr = '{0:.1f}'.format(perfectPushup * 100 / (perfectPushup + imperfectPushup)) + "% Perfect"
    else:
        pushupValStr = '{0:.1f}'.format(0) + "% Perfect"
    textLoc = (int(d.WINDOW_WIDTH*0.83), int(d.WINDOW_HEIGHT*0.50))
    pushupValText = Text(pushupValStr,textLoc,30,color.black,topmode=True)
    pushupValText.draw(d)

    legRaiseStr = "Leg Raises: "
    textLoc = (int(d.WINDOW_WIDTH*0.07), int(d.WINDOW_HEIGHT*0.635))
    legRaiseText = Text(legRaiseStr,textLoc,30,color.black,topmode=True)
    legRaiseText.draw(d)

    if (perfectLegRaise + imperfectLegRaise) != 0:
        legRaiseValStr = '{0:.1f}'.format(perfectLegRaise * 100 / (perfectLegRaise + imperfectLegRaise)) + "% Perfect"
    else:
        legRaiseValStr = '{0:.1f}'.format(0) + "% Perfect"
    textLoc = (int(d.WINDOW_WIDTH*0.83), int(d.WINDOW_HEIGHT*0.635))
    legRaiseValText = Text(legRaiseValStr,textLoc,30,color.black,topmode=True)
    legRaiseValText.draw(d)

    lungeStr = "Lunges: "
    textLoc = (int(d.WINDOW_WIDTH*0.07), int(d.WINDOW_HEIGHT*0.77))
    lungeText = Text(lungeStr,textLoc,30,color.black,topmode=True)
    lungeText.draw(d)

    if (perfectLunge + imperfectLunge) != 0:
        lungeValStr = '{0:.1f}'.format(perfectLunge * 100 / (perfectLunge + imperfectLunge)) + "% Perfect"
    else:
        lungeValStr = '{0:.1f}'.format(0) + "% Perfect"
    textLoc = (int(d.WINDOW_WIDTH*0.83), int(d.WINDOW_HEIGHT*0.77))
    lungeValText = Text(lungeValStr,textLoc,30,color.black,topmode=True)
    lungeValText.draw(d)

def drawSummaryGraph(d):
    # Params
    green = "#47ff36"
    red = "#ff3636"
    perfectPushup = d.workout[7]
    imperfectPushup = d.workout[8] - d.workout[7]
    if perfectPushup == 0:
        imperfectPushup = 1

    perfectLegRaise = d.workout[9]
    imperfectLegRaise = d.workout[10] - d.workout[9]
    if perfectLegRaise == 0:
        imperfectLegRaise = 1

    perfectLunge = d.workout[11]
    imperfectLunge = d.workout[12] - d.workout[11]
    if perfectLunge == 0:
        imperfectLunge = 1
    
    my_dpi = 96
    figure_height = (d.WINDOW_HEIGHT * 0.4)/my_dpi
    figure_width = (d.WINDOW_WIDTH * 0.8)/my_dpi

    plt.close("all") # Closing graph before drawing a new one to prevent excess use of memory

    fig = plt.figure(figsize=(figure_width, figure_height))

    # Pushups
    ax = fig.add_subplot(511)
    ax.axis("off")
    ax.barh("Pushup", perfectPushup, color = green)
    ax.barh("Pushup", imperfectPushup, color = red, left = perfectPushup)

    # Leg Raises    
    ax = fig.add_subplot(513)
    ax.axis("off")
    ax.barh("Leg raises", perfectLegRaise, color = green)
    ax.barh("Leg raises", imperfectLegRaise, color = red, left = perfectLegRaise)

    # Lunges
    ax = fig.add_subplot(515)
    ax.axis("off")
    ax.barh("Lunges", perfectLunge, color = green)
    ax.barh("Lunges", imperfectLunge, color = red, left = perfectLunge)
        
    canvas = agg.FigureCanvasAgg(fig)
    canvas.draw()
    renderer = canvas.get_renderer()
    raw_data = renderer.tostring_rgb()
    size = canvas.get_width_height()
    surf = pygame.image.fromstring(raw_data, size, "RGB")
    d.screen.blit(surf, (int(d.WINDOW_WIDTH * 0.1), int(d.WINDOW_HEIGHT*0.45)))
    
    drawSummaryGraphInfo(d)

def drawHistorySummary(d):
    if(d.newScreen):
        d.screen.fill(color.white)
        drawSummaryInfo(d)
        drawSummaryGraph(d)
        drawScreenChangeButtons(d, screenMode.HISTORYOPTIONS, 0)

def filterData(workouts):
    filteredData = dict()
    for workout in workouts:
        date = workout[2].split()[0]
        if date in filteredData:
            filteredData[date]["perfPush"] += workout[7]
            filteredData[date]["totalPush"] += workout[8]
            filteredData[date]["perfRaise"] += workout[9]
            filteredData[date]["totalRaise"] += workout[10]
            filteredData[date]["perfLunge"] += workout[11]
            filteredData[date]["totalLunge"] += workout[12]
        else:
            filteredData[date] = dict()
            filteredData[date]["perfPush"] = workout[7]
            filteredData[date]["totalPush"] = workout[8]
            filteredData[date]["perfRaise"] = workout[9]
            filteredData[date]["totalRaise"] = workout[10]
            filteredData[date]["perfLunge"] = workout[11]
            filteredData[date]["totalLunge"] = workout[12]
    return filteredData
 
def drawHistoryTrends(d):
    if(d.newScreen):
        d.screen.fill(color.white)

        titleStr = "Workout Trends"
        textLoc = (int(d.WINDOW_WIDTH*0.5), int(d.WINDOW_HEIGHT*0.1))
        titleText = Text(titleStr,textLoc,60,color.black,topmode=False)
        titleText.draw(d)

        data = d.db.getWorkouts(d.currProfile)

        my_dpi = 96
        figure_height = (d.WINDOW_HEIGHT * 0.8)/my_dpi
        figure_width = (d.WINDOW_WIDTH * 0.8)/my_dpi
        
        plt.close("all")

        fig = plt.figure(figsize=(figure_width, figure_height))

        ax = fig.add_subplot(111)
        
        # perfectPushup = [3, 4, 5, 6, 8]
        # perfectLunge = [8, 1, 6, 2, 3]
        # perfectLegRaise = [1, 9, 2, 3, 4]

        data = d.db.getWorkouts(d.currProfile)
        data = filterData(data)
        perfectPushup = []
        perfectLunge = []
        perfectLegRaise = []
        sessions = []
        allDates = sorted(data.keys())
        endIndex = len(allDates) - (d.pageNum * 5)
        startIndex = max(0, endIndex  - 5)
        dates = allDates[startIndex:endIndex]

        for date in dates:
            sessions.append(date)
            summary = data[date]
            
            if summary["totalPush"] != 0:
                perfectPushup.append(summary["perfPush"] / summary["totalPush"] * 100)
            else:
                perfectPushup.append(0)
            
            if summary["totalRaise"] != 0:
                perfectLegRaise.append(summary["perfRaise"] / summary["totalRaise"] * 100)
            else:
                perfectLegRaise.append(0)
            
            if summary["totalLunge"] != 0:
                perfectLunge.append(summary["perfLunge"] / summary["totalLunge"] * 100)
            else:
                perfectLunge.append(0)

        push, = ax.plot(sessions, perfectPushup, label="Perfect Pushups", color="blue")
        ax.scatter(sessions, perfectPushup, label="Perfect Pushups", color="blue")
        rais, = ax.plot(sessions, perfectLegRaise, label="Perfect Leg Raises", color="red")
        ax.scatter(sessions, perfectLegRaise, label="Perfect Leg Raises", color="red")
        lunge, = ax.plot(sessions, perfectLunge, label="Perfect Lunges", color="green")
        ax.scatter(sessions, perfectLunge, label="Perfect Lunges", color="green")

        ax.legend([push, rais, lunge], ["Perfect Pushups", "Perfect Leg Raises", "Perfect Lunges"])

        canvas = agg.FigureCanvasAgg(fig)
        canvas.draw()
        renderer = canvas.get_renderer()
        raw_data = renderer.tostring_rgb()
        size = canvas.get_width_height()
        surf = pygame.image.fromstring(raw_data, size, "RGB")
        d.screen.blit(surf, (int(d.WINDOW_WIDTH * 0.1), int(d.WINDOW_HEIGHT*0.18)))

        drawScreenChangeButtons(d, screenMode.HISTORYOPTIONS, len(allDates))

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

def drawMain(d):
    if(d.newScreen):
        d.screen.fill(color.white)

        titleStr = "Falcon: the Pro Gym Assistant"
        textLoc = (int(d.WINDOW_WIDTH*0.5), int(d.WINDOW_HEIGHT*0.18))
        titleText = Text(titleStr,textLoc,70,color.black,topmode=False)
        titleText.draw(d)
        d.newScreen = False
    #rewdraw buttons each time

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
        elif(d.currentScreen == screenMode.HISTORYOPTIONS):
            drawHistoryOptions(d)
        elif(d.currentScreen == screenMode.HISTORYSUMMARY):
            drawHistorySummary(d)
        elif(d.currentScreen == screenMode.HISTORYTRENDS):
            drawHistoryTrends(d)
        pygame.display.update()
        pygameHandleEvent(d)
        # pygameHandleButtons(d)
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
                if(d.currentScreen == screenMode.WORKOUT):
                    if(d.pause):
                        d.feedbackStopwatch.start()
                        d.newScreen = True
                        if(d.breakTime<0):
                            d.resumeFromPause = d.RESUME_TIME
                            d.justResumed = True
                        d.pause = False
                    else:
                        d.feedbackStopwatch.stop()
                        d.workoutStopwatch.stop()
                        drawPause(d)
                        d.pause = True
                        d.workoutStopwatch.stop()

# def pygameHandleButtons(d):
#     if d.currentScreen == screenMode.HISTORYOPTIONS:
#         for button in d.buttons:
#             if button.handle_mouse():
#                 if button.info == "back":
#                     d.currentScreen = screenMode.MAIN
#                 elif button.info == "trends":
#                     d.currentScreen = screenMode.HISTORYTRENDS
#                 else:
#                     d.currentScreen = screenMode.HISTORYSUMMARY
#                     d.workout = button.info
#             # button.draw(d)
#     elif d.currentScreen == screenMode.HISTORYSUMMARY:
#         for button in d.buttons:
#             if button.handle_mouse():
#                 if button.info == "back":
#                     d.currentScreen = screenMode.HISTORYOPTIONS
#                 elif button.info == "trends":
#                     d.currentScreen = screenMode.HISTORYTRENDS
#             # button.draw(d)
#     elif d.currentScreen == screenMode.HISTORYTRENDS:
#         for button in d.buttons:
#             if button.handle_mouse():
#                 if button.info == "back":
#                     d.currentScreen = screenMode.HISTORYOPTIONS
#             # button.draw(d)

data = data()
init(data)
main(data)