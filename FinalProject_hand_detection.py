import cv2
import mediapipe as mp
import time
import traceback
import socket
import sys


# # RPi's IP
SERVER_IP = "192.168.50.64"
SERVER_PORT = 8888

print("Starting socket: TCP...")
server_addr = (SERVER_IP, SERVER_PORT)
socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)



trigger_k = 0.05
aim_k = 0.3
move_k = 20

commandDict = {'right':'10','left':'01','unKnown':'-1','hit the target!':'11','miss':'00'
               ,'Shooting mode':'000', 'Movement mode':'100'}

cap = cv2.VideoCapture(1)

mpHands = mp.solutions.hands
hands = mpHands.Hands(static_image_mode=False,
                      max_num_hands=2,
                      min_detection_confidence=0.5,
                      min_tracking_confidence=0.5)
mpDraw = mp.solutions.drawing_utils

pTime = 0
cTime = 0

# global variables
frameNum = 0
commandLst = []
commandSending = ''

flag = 1

#### connect to raspberry pi
while True:
    try:
        print("Connecting to server @ %s:%d..." % (SERVER_IP, SERVER_PORT))
        socket_tcp.connect(server_addr)
        flag = 1
        break
    except Exception:
        print("Can't connect to server,try it latter!")
        time.sleep(1)
        continue

def get_info():
    # dis_5_17
    dis_5_17 = 0
    # node 0
    node0 = [0, 0, 0]
    # node 5
    node5 = [0, 0, 0]
    # node 3
    node3 = [0,0,0]
    # node 17
    node17 = [0,0,0]
    # intialize 
    distanceDict = {}

    success, img = cap.read()
    imgRGB= cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)
    # print(results.multi_hand_landmarks)

    
    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            for id, lm in enumerate(handLms.landmark):
                d = 0
                ## store node 0, 3, 5
                if id == 0:
                    node0 = [lm.x,lm.y,lm.z]
                h, w, c = img.shape
                cx, cy = int(lm.x *w), int(lm.y*h)
                
                ## store node 5 for aiming and trigger dectection
                if id == 5:
                    node5 = [lm.x,lm.y,lm.z]
                
                if id == 3:
                    node3 = [lm.x,lm.y,lm.z]

                if id ==17:
                    node17 = [lm.x,lm.y,lm.z]

                dis_5_17 = (node17[0]-node5[0])**2 + (node17[1]-node5[1])**2 + (node17[2]-node5[2])**2


                ## draw the nodes
                cv2.circle(img, (cx,cy), 3, (255,0,255), cv2.FILLED)

                ### detect 4 and 8 for left and right 
                if id == 12:
                    d = (node0[0]-lm.x)**2 + (node0[1]-lm.y)**2 + (node0[2]-lm.z)**2
                    distanceDict[id] = d

                if id == 4:
                    distanceSum = 0
                    ## for right detection
                    distanceSum = (node0[0]-lm.x)**2 + (node0[1]-lm.y)**2 + (node0[2]-lm.z)**2
                    distanceDict[id] = distanceSum
                    ## for trigger detection
                    distanceSum = (node3[0]-lm.x)**2 + (node3[1]-lm.y)**2 + (node3[2]-lm.z)**2
                    distanceDict['trigger'] = distanceSum

                if id == 8 :
                    distanceSum = 0
                    distanceSum = (node0[0]-lm.x)**2 + (node0[1]-lm.y)**2 + (node0[2]-lm.z)**2
                    distanceDict[id] = distanceSum


                    distanceSum = (node5[0]-lm.x)**2 + (node5[1]-lm.y)**2 + (node5[2]-lm.z)**2
                    distanceDict['aiming'] = distanceSum
                    
            ## line between nodes in mediapipe
            mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)

    return distanceDict, img, dis_5_17
if flag == 1:
    while True:
        distanceDict,img,dis_5_17 = get_info()

        command = 'Shooting mode'
        if distanceDict == {}:
            command = 'unKnown'
        else:
            MaxId = [key for key,value in distanceDict.items() if value == max(distanceDict.values())][0]

        # if 12 in distanceDict and distanceDict[12] > 0.4:
        if 12 in distanceDict and distanceDict[12] > move_k*dis_5_17:
            ### enter the moving mode
            socket_tcp.send(str.encode('100'))
            time.sleep(2)
            
            while True:
                command = 'Movement mode'
                # get_info()
                print("-----------while loop------------")
                distanceDict,img,dis_5_17 = get_info()
                cv2.putText(img,command,(10,150), cv2.FONT_HERSHEY_PLAIN, 3, (255,0,255), 3)

                ## calculate and print fps
                cTime = time.time()
                fps = 1/(cTime-pTime)
                pTime = cTime

                cv2.putText(img,str(int(fps)), (10,70), cv2.FONT_HERSHEY_PLAIN, 3, (255,0,255), 3)

                cv2.imshow("Image", img)

                frameNum = 1
                commandLst.append(command)
                if frameNum == 1:
                    commandSending = 'movement mode'
                    
                    ## send message to raspberry pi
                    socket_tcp.send(str.encode(commandSending))

                    ## reset data to 0
                    frameNum = 0
                    commandLst = []
                    
                    print(commandSending)

                if distanceDict == {}:
                    command = 'unKnown'
                else:
                    MaxId = [key for key,value in distanceDict.items() if value == max(distanceDict.values())][0]

                if MaxId == 4:
                    for i in range(10):
                        print("----------right------------")
                    socket_tcp.send(str.encode('10')) 
                    command == 'right'
                    break
                if MaxId == 8:
                    for i in range(10):
                        print("----------left------------")
                    socket_tcp.send(str.encode('01'))
                    command == 'left'
                    break

                ## esc
                key = cv2.waitKey(1)
                if key == 27:
                    cv2.destroyAllWindows()
                    break

                

        # if 'aiming' in distanceDict and distanceDict['trigger'] < 0.001:
        if 'aiming' in distanceDict and distanceDict['trigger'] < trigger_k*dis_5_17:
            # print("-------trigger dis--------",distanceDict['trigger'])
            print("trigger!!!")
            # if distanceDict['aiming'] < 0.014:
            if distanceDict['aiming'] < aim_k*dis_5_17:
                # print("--------hit distance------", distanceDict['aiming'])
                # print("--------hit distance------", dis_5_17)
                command = 'hit the target!'
            else:
                # print("--------miss distance------", distanceDict['aiming'])
                # print("--------miss distance------", dis_5_17)
                command = 'miss'

        cv2.putText(img,command,(10,150), cv2.FONT_HERSHEY_PLAIN, 3, (255,0,255), 3)

        ## calculate and print fps
        cTime = time.time()
        fps = 1/(cTime-pTime)
        pTime = cTime

        cv2.putText(img,str(int(fps)), (10,70), cv2.FONT_HERSHEY_PLAIN, 3, (255,0,255), 3)

        cv2.imshow("Image", img)

        ## judge the command by the number of frames
        frameNum += 1
        commandLst.append(command)
        if frameNum == 3:
            if max(commandLst) == min(commandLst):
                commandSending = commandDict[command]
            else:
                commandSending = commandDict['unKnown']
            
            ## send message to raspberry pi
            socket_tcp.send(str.encode(commandSending))

            ## reset data to 0
            frameNum = 0
            commandLst = []
            
            print(commandSending)

        else:
            continue

        ## esc
        key = cv2.waitKey(1)
        if key == 27:
            cv2.destroyAllWindows()
            break
