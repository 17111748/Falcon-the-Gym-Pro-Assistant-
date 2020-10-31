import sys, pygame, cv2, time
from structs import *
from colors import *

def init(d):
    #constants
    d.FRAME_FREQUENCY = 100
    d.WINDOW_WIDTH = 1280
    d.WINDOW_HEIGHT = int(d.WINDOW_WIDTH/1.6)
    d.LIVE_VIDEO_DIMS = (int(d.WINDOW_WIDTH*0.5),int(d.WINDOW_HEIGHT*0.5))
    d.IMAGE_DIR = '/Users/vishalbaskar/OneDrive/Documents/School/College/2020-2021/18-500/Falcon-the-Gym-Pro-Assistant-/UI/images/leg_raise/'
    d.REPS_PER_SET = 3
    d.SETS_PER_WORKOUT = 10
    d.SET_BREAK_TIME = 5
    d.RESUME_TIME = 3
    #setup pygame/camera
    # d.camera  = cv2.VideoCapture(0)
    d.camera = cv2.VideoCapture(1)
    if not d.camera.isOpened():
        print("Could not open video device")
    pygame.init()
    pygame.display.set_caption("OpenCV camera stream on Pygame")
    d.screen = pygame.display.set_mode([d.WINDOW_WIDTH, d.WINDOW_HEIGHT])
    d.live_video = pygame.Surface(d.LIVE_VIDEO_DIMS)
    d.clock = pygame.time.Clock()

    #based on rolling AVG of d.clock.tick() of 40ms
    d.timePerFrame = 0.041
    d.workoutRepTime = {
        #120 frames
        "c": d.timePerFrame*120,
        "u": d.timePerFrame*120,
        "l": d.timePerFrame*120,
    }

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
    d.currSet = 6

    d.currWorkoutFrame = 0
    d.currentRep = 1

    d.timeRemaining = -1
    d.beginTime = pygame.time.get_ticks()

    d.workoutTotalFrames = {
        "c": 120, 
        "l": 120,
        "u": 120
    }

    d.captureFrame = {
        "c": 50, 
        "l": 10,
        "u": 10
    }

    d.currentScreen = screenMode.WORKOUT
    d.newScreen = True

    d.breakTime = d.SET_BREAK_TIME

    d.resumeFromPause = -1
    d.justResumed = False
    d.pause = False

def drawMain(d):
    if(d.newScreen):
        #draw start and settings
        #draw 
        d.screen.fill(color.white)
        d.newScreen = False

def updateRepText(d):
    repStr = "Rep: "+str(d.currentRep)+"/"+str(d.REPS_PER_SET)
    textLoc = (int(d.WINDOW_WIDTH*0.15), int(d.WINDOW_HEIGHT*0.17))
    repText = Text(repStr,textLoc,35,color.black,topmode=True)
    repText.draw(d)

def updateWorkoutText(d,currentWorkout):
    workStr = d.workoutNames[currentWorkout]
    textLoc = (int(d.WINDOW_WIDTH*0.025), int(d.WINDOW_HEIGHT*0.025))
    workText = Text(workStr,textLoc,50,color.black,topmode=True)
    workText.draw(d)

def updateSetText(d):
    setStr = "Set: "+str(d.currSet)+"/"+str(d.SETS_PER_WORKOUT)
    textLoc = (int(d.WINDOW_WIDTH*0.025), int(d.WINDOW_HEIGHT*0.17))
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

def updateBreakString(d):
    breakStr = "Next set in "+str(d.breakTime)+" seconds     "
    if(d.breakTime==1):
        breakStr = "Next set in "+str(d.breakTime)+" second      "
    textLoc = (int(d.WINDOW_WIDTH*0.5), int(d.WINDOW_HEIGHT*0.06))
    breakText = Text(breakStr,textLoc,60,color.red,topmode=True)
    breakText.draw(d)

def updateResumeTimeText(d):
    resumeStr = "Resuming in "+str(d.resumeFromPause)+" seconds     "
    if(d.resumeFromPause==1):
        resumeStr = "Resuming in "+str(d.resumeFromPause)+" second      "
    elif(d.resumeFromPause<0):
        resumeStr = (len(resumeStr)*2)*" "
    textLoc = (int(d.WINDOW_WIDTH*0.5), int(d.WINDOW_HEIGHT*0.06))
    resumeText = Text(resumeStr,textLoc,60,color.red,topmode=True)
    resumeText.draw(d)


def drawWorkout(d):
    if(not d.pause):
        currentWorkout = d.workoutSets[d.workoutFocus][d.currSet-1]
        timeTextResumePause = True
        if(d.newScreen):
            #only reset workoutframe and current rep and recalculate time if new set
            if(d.resumeFromPause<0):
                d.currWorkoutFrame = 0
                d.currentRep = 1 
                timeTextResumePause = False
            
            if(d.breakTime>=0):
                d.currWorkoutFrame = 0 

            d.screen.fill(color.white)

            #initialize text
            updateRepText(d)
            updateWorkoutText(d,currentWorkout)
            updateSetText(d)
            updateTimeText(d,True,timeTextResumePause)
            if(d.breakTime>0):
                updateBreakString(d)

            #draw divider line
            start_line_loc = (d.WINDOW_WIDTH*0.45,d.WINDOW_HEIGHT*0.225)
            end_line_loc = (d.WINDOW_WIDTH*0.45,d.WINDOW_HEIGHT*0.85)
            pygame.draw.line(d.screen, color.black, start_line_loc, end_line_loc, 3)

            d.beginTime = pygame.time.get_ticks()
            
            d.newScreen = False

        #take photo and upate live video
        ret, frame = d.camera.read()
        if(ret is False): 
            return False
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
            #need to downsize to 160x120
            #send to UART in a seperate thread?

        #incrementing rep and updating model
        if(d.breakTime < 0 or d.currWorkoutFrame==0):
            if(d.resumeFromPause>=0):
                updateResumeTimeText(d)
            if(d.resumeFromPause<0 or d.justResumed):
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
                            #TODO: code to go to workout summary screen
                            return True
                        d.breakTime = d.SET_BREAK_TIME
                        d.newScreen=True
                        return True
                    updateRepText(d)

                #update model image
                modelLocation = (d.WINDOW_WIDTH*0.02, d.WINDOW_HEIGHT*0.3)
                d.screen.blit(pygame.image.load(d.IMAGE_DIR+"{:03n}".format(d.currWorkoutFrame)+'.gif'),modelLocation)
                d.currWorkoutFrame+=1

        #change timer if second has passed
        currTime = pygame.time.get_ticks()
        if(currTime-d.beginTime>1000):
            if(d.resumeFromPause<0):
                updateTimeText(d,False,False)
                if(d.breakTime>0):
                    d.breakTime-=1
                    if(d.breakTime==0):
                        d.newScreen = True
                        d.breakTime = -1
                    else:
                        updateBreakString(d)
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
            sys.exit(0)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
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

data = data()
init(data)
main(data)