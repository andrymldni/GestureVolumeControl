import cv2
from handDetection import HandDetection
from cv2 import waitKey
import time
import numpy as np
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# Define camera we are going to read
webcam = cv2.VideoCapture()
webcam.open(0, cv2.CAP_DSHOW)
pTime = 0

# Initialize detector
handDetection = HandDetection(max_num_hands=2, min_detection_confidence =0.7, 
                        min_tracking_confidence=0.7)

# Initialize Audio devices
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
#volume.GetMute()
#volume.GetMasterVolumeLevel()
volRange = volume.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]
vol = 0
volBar = 400
volPer = 0

while True:
    # Setting webcam
    status , frame = webcam.read()
    frame = cv2.flip(frame,1)  # Webcam no mirror
    
    handLandMarks = handDetection.findHandLanMarks(image=frame, draw=True)
    if len(handLandMarks) != 0:  
        #print(handLandMarks[4], handLandMarks[8])
        x1, y1 = handLandMarks[4][1], handLandMarks[4][2]
        x2, y2 = handLandMarks[8][1], handLandMarks[8][2]
        
        # Middle point of the line connecting the thumb and index fingers
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        cv2.circle(frame, (x1,y1), 15, (255, 0, 255), cv2.FILLED)
        cv2.circle(frame, (x2,y2), 15, (255, 0, 255), cv2.FILLED)
        cv2.line(frame,(x1, y1), (x2, y2), (255, 0, 255),3)
        cv2.circle(frame, (cx,cy), 15, (255, 0, 255), cv2.FILLED)
        
        # Check the legnth of the line to define the UPPER and LOWER bounds
        # Then when we are in the UPPER bound = 100% Volumne
        length = math.hypot(x2 - x1, y2 - y1)

        # Map range [50, 300] to [minVol, maxVol]
        vol = np.interp(length, [50, 300],[minVol, maxVol])
        volume.SetMasterVolumeLevel(vol, None)
        
        volBar = np.interp(length, [50, 300],[400, 150])
        volPer = np.interp(length, [50, 300],[0, 100])
        print(int(length), vol)

        if length < 50:
            cv2.circle(frame, (cx,cy), 15, (0, 255, 0), cv2.FILLED)
    
    cv2.rectangle(frame, (50, 150), (85, 400), (255, 0, 0), 3)
    cv2.rectangle(frame, (50, int(volBar)), (85, 400), (0, 255, 0), cv2.FILLED)
    cv2.putText(frame,f'{int(volPer)}%',(40,450), cv2.FONT_HERSHEY_COMPLEX,
                 1, (255, 0, 0), 3)

    # To make FPS count
    cTime = time.time()
    fps = 1/(cTime-pTime)
    pTime = cTime
    cv2.putText(frame,f'FPS: {int(fps)}',(40,50), cv2.FONT_HERSHEY_COMPLEX,
                 1, (255, 0, 0), 3)

    # Start webcam, End webcam press 's'
    cv2.imshow("Test",frame)
    if cv2.waitKey(1) == ord('s'):
        break
    
# Since we exit the loop, its time to clean 
cv2.destroyAllWindows()
webcam.release()