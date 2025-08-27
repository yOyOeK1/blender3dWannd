import cv2
import numpy as np
import os
import time
import wsHelper
import json
import base64
import time

wsHostUrl = "wss://192.168.43.220:8080/fooWSS"
wsClientID = 'ocvCam'
wsObj = -1
mediaChunks = []
fName = f"/tmp/opcv.tmp"
streamCurrentFrame = 0
lastP = []
avgP = []
acuLevel = 10.00



eStack = []

def rebuildAvgP():
    global lastP
    global acuLevel
    global avgP
    mm = [True,True]
    xyz = [False,False,False]
    lastPlen = len( lastP )

    if lastPlen > 26:
        lastP.pop(0)
        lastPlen-=1


    for p in range( lastPlen ):
        if p == 0:
            xyz = [ lastP[p][0], lastP[p][1], lastP[p][2] ]
            mm = [ lastP[p][0], lastP[p][0] ]
        else:
            xyz[0]+= lastP[p][0]
            xyz[1]+= lastP[p][1]
            xyz[2]+= lastP[p][2]

            if mm[0] > lastP[p][0] : mm[0] = lastP[p][0]
            if mm[1] < lastP[p][0] : mm[1] = lastP[p][0] 

    avgP = [
        xyz[0]/lastPlen, xyz[1]/lastPlen, xyz[2]/lastPlen
    ]
    
    acuLevel = mm[1] - mm[0] 



def onDone( event ):
    print("onDone ")

    msg = event['msg']
    msg['status'] = 'done'
    #print(msg)
    msgStr = json.dumps(msg)
    senderBackTo = msg['sender']
    strToSend = f"wsSendToWSID:{senderBackTo}:{msgStr}"
    print(strToSend)
    event['ws'].send( strToSend )


def on_message(ws, message):
    global wsObj
    global mediaChunks
    global fName
    global streamCurrentFrame
    global eStack
    global lastP
    global avgP

    wsObj = ws
    #print(["ws on_message   ", message])
    j = json.loads( message)
#def abc():
    if j['topic'] == 'dziHarv/mediaStream':
        mediaChunks.append( j['totalFrames'] )
        streamCurrentFrame = j['totalFrames']
        #print(['totalFrames',j['totalFrames']])

        with open(fName, 'ab') as f:
            f.write( base64.b64decode( j['chunk'] ) )
            
    elif j['topic'] == 'bt/SetPOI':
        print(["got ",j])
        eStack.append({
            "ws": ws, "msg": j
        })
        keyPress3.keyPress3(lastP[0],lastP[1],lastP[2], onDone, eStack[-1])

                

        

#wsHelper.wsStart(on_message, wsClientID,host=wsHostUrl )

#print("ws is connected...?")
#time.sleep(2)

# Load the image
image = cv2.imread('./marker_42.png')

# C

aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)
parameters = cv2.aruco.DetectorParameters()
parameters.cornerRefinementMethod = cv2.aruco.CORNER_REFINE_SUBPIX
detector = cv2.aruco.ArucoDetector( aruco_dict, parameters )
parameters = cv2.aruco.DetectorParameters()


def DoProcess( frame ):
    global lastP


    # For a camera stream (inside a loop):
    frameNo = 0
    marker_length = 0.03
    cameraMatrix = np.array([[1200.0,    0.0,  960.0],
                          [   0.0, 1200.0,  540.0],
                          [   0.0,    0.0,    1.0]])
    distCoeffs = np.zeros((4,1),np.float64)




#  ,y     , x  ,z      opencv is 0,0 in top right of screen
#top right
#['tvecs', -0.2721733907529358, -0.005067015469792001, 0.5854158840667054]
# top left
#['tvecs', -0.24607548171962706, -0.17980969424632956, 0.5264022979446922]
#bottom right 
#['tvecs', -0.48845245038418533, -0.015459396070424309, 0.6747175063712179]
#bottom left 
#['tvecs', -0.4992812286788609, -0.2384740299383612, 0.6808032145086779]
#center
#['tvecs', -0.3916441304165394, -0.14357023442866698, 0.6653835155854524]

    
    #ret, frame = cap.read()
    #print(["frame",frameNo])
    frameNo+=1
    #time.sleep(1.00/30.00)
        
    try:
        frame = cv2.resize( frame, (480,640) )
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    except:
        return 9
    
    (corners, ids, rejected) = detector.detectMarkers(frame)
    
    if ids is not None:
        frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
        cv2.aruco.drawDetectedMarkers(frame, corners, ids)

        rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers( corners, marker_length, cameraMatrix, distCoeffs )
        for i in range(len(ids)):
            cv2.drawFrameAxes( frame, cameraMatrix, distCoeffs, rvecs[i], tvecs[i], marker_length *0.5 )
            #print(["id", i," ","rvecs",rvecs[i],"tvecs",tvecs[i]])
            #print(["tvecs",tvecs[i][0][0], tvecs[i][0][1], tvecs[i][0][2]])
            dataTo = {
                "topic":"ocvWeb/point/1",
                "rv": {"a":rvecs[i][0][0],"b":rvecs[i][0][1],"c":rvecs[i][0][2]},
                "tv": {"a":tvecs[i][0][0],"b":tvecs[i][0][1],"c":tvecs[i][0][2]}
            }
            lastP.append( tvecs[i][0] )
            rebuildAvgP()
            #print(dataTo['tv'])
            #jToStr = json.dumps( dataTo )
            #wsHelper.stackSend( jToStr )
        #print( ["id",ids,"\n\n\n",corners ])
        
    #cv2.imshow("Hand Tracking", frame)
    #if cv2.waitKey(1) & 0xFF == ord("q"):
    #    return 0   


    #cap.release()
    #cv2.destroyAllWindows()
    #time.sleep(2.5)
    #print("DoProcess Done")
    #try:
    #    os.remove( vidPath )
    #except:
    #    print("remove not ok")
    return 1

        

fNo = 0
currentFrame = 0

caps = []
tStart = -1
tLast = -1
tNow = -1
tDelta = -1
tFlame = int(1000.00/12.00)
skipFrame = False









def getMsNow():
    return int(time.time()*1000.00)

def sTick( frame ):
    global sTOffset
    global sFpsMs

    targetT = float( frame ) * sFpsMs
    offsetNow = (sTOffset+getMsNow())%1000
    sleepFor = (targetT-offsetNow)%1000
    if sleepFor > sFpsMs:
        print(f"overload 2 - sTick f{frame}")
    elif sleepFor > 0.00:
        #print(['sleepFor',sleepFor])
        time.sleep( float( sleepFor)/1000.00 )
    else:
        print("overload - sTick")

sTStart = 0
sTOffset = 0
sFps = 30
sFpsMs = 1000.00/float(sFps)




while False:


    #exit(1)
    

    fNo+=1
    #vidPath = '/tmp/vid_huAruco9_2.webm'
    vidPath = '/home/yoyo/Apps/videoAruco9.webm'
    vidPath = '/home/yoyo/Apps/videoAruco8.webm'

    if len( mediaChunks ) > 15:
        tStart = int(time.time()*1000.00)
        #try:
        #    os.remove( fName )
        #except:
        #    print("remove not ok")

                

        cap = cv2.VideoCapture( fName ) 
        thisFrameNo = 0
        sTStart = getMsNow()
        sTOffset = sTStart%1000
        while True:
            try:
                ret, frame = cap.read()
            except:
                print("oiysh - 3 cap.empty?")
            #fps = cap.get(cv2.CAP_PROP_FPS)
            #frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)

            #print(['ret',ret, 'fps',fps,'frame_count',frame_count])
            
            if skipFrame == False:
                if thisFrameNo%3 == 0:
                    res = DoProcess( frame )
            
            thisFrameNo+=1

            if streamCurrentFrame - thisFrameNo < 45:
                time.sleep( (sFpsMs/1000.00)*1.2   ) 



        cap = 0
        print("end file")

        
        
        

    else:
        print("no media in stack")
        time.sleep(1)



# Create the ArUco detector
#detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)
# Detect the markers
#corners, ids, rejected = detector.detectMarkers(gray)
# Print the detected markers
#print("Detected markers:", ids)
#if ids is not None:
#    cv2.aruco.drawDetectedMarkers(image, corners, ids)
#    cv2.imshow('Detected Markers', image)
#    cv2.waitKey(0)
#    cv2.destroyAllWindows()

#exit()
