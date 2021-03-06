import cv2
import numpy as np
import time
import autopy
from VirtualMouse import HandTrackingModule

##############
wCam,hCam = 640 , 480
pTime = 0
detector = HandTrackingModule.HandDetector(maxHands=1)
wScr, hScr = autopy.screen.size()
frameR = 100
smoothening = 8
plocX, plocY = 0, 0
clocX,clocY = 0, 0
###############


cap = cv2.VideoCapture(0)
cap.set(3,wCam) #width
cap.set(4,hCam) #height

while True:
    # 1. Find hand landmarks
    success , img = cap.read()
    img = detector.findHands(img)
    lmList, bbox = detector.findPosition(img)
    # 2. get tip of the index and middle fingers
    if len(lmList) != 0 :
        x1, y1 = lmList[8][1:]
        x2, y2 = lmList[12][1:]

        # 3. check which fingers are up
        fingers = detector.fingersUp()
        print(fingers)

        # 4. only index finger : Moving mode
        cv2.rectangle(img, (frameR, frameR), (wCam - frameR, hCam - frameR), (255, 0, 255), 2)
        if fingers[1] == 1 and fingers[2] == 0 :

            # 5. Convert Coordinates

            x3 = np.interp(x1,(frameR,wCam-frameR),(0,wScr))
            y3 = np.interp(y1, (frameR, hCam-frameR), (0, hScr))

            clocX = plocX + (x3 - plocX) / smoothening
            clocY = plocY + (y3 - plocY) / smoothening
            # 7. Move mouse
            autopy.mouse.move(wScr - clocX, clocY)
            cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
            plocX, plocY = clocX,clocY
            # 8. Both index and middle fingers are up : clicking mode
            # 9. Find distance between finger and click mouse
        if fingers[1] == 1 and fingers[2] == 1 :
            length, img, lineInfo = detector.findDistance(8,12,img)
            print(length)
            if(length < 15):
                cv2.circle(img, (lineInfo[4], lineInfo[5]), 15, (0, 255, 0), cv2.FILLED)
                autopy.mouse.click()
                time.sleep(0.3)

    # 11. Frame rate and display
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img,str(int(fps)),(20,20),cv2.FONT_ITALIC,0.5,(0,0,255),1)

    cv2.imshow("Image",img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break