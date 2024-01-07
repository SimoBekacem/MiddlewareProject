import cv2
import subprocess
from time import sleep


classNames = []
classFile = r"C:\Users\Reda\OneDrive\Bureau\New folder\INE2\P2\Middleware et architecture distribue\Object_Detection_Files\Object_Detection_Files\coco.names"
with open(classFile,"rt") as f:
    classNames = f.read().rstrip("\n").split("\n")

configPath = r"C:\Users\Reda\OneDrive\Bureau\New folder\INE2\P2\Middleware et architecture distribue\Object_Detection_Files\Object_Detection_Files\ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt"
weightsPath = r"C:\Users\Reda\OneDrive\Bureau\New folder\INE2\P2\Middleware et architecture distribue\Object_Detection_Files\Object_Detection_Files\frozen_inference_graph.pb"
command_file_path = r"C:\Users\Reda\OneDrive\Bureau\cd.txt"
file_path = r"C:\Users\Reda\OneDrive\Bureau\command.txt"


net = cv2.dnn_DetectionModel(weightsPath,configPath)
net.setInputSize(320,320)
net.setInputScale(1.0/ 127.5)
net.setInputMean((127.5, 127.5, 127.5))
net.setInputSwapRB(True)


def getObjects(img, thres, nms, draw=True, objects=[]):
    classIds, confs, bbox = net.detect(img,confThreshold=thres,nmsThreshold=nms)
    #print(classIds,bbox)
    if len(objects) == 0: objects = classNames
    objectInfo =[]
    X,Y=0,0
    if len(classIds) != 0:
        
        for classId, confidence,box in zip(classIds.flatten(),confs.flatten(),bbox):
            className = classNames[classId - 1]
            if className in objects:
                objectInfo.append([box,className])
                if (draw):
                    cv2.rectangle(img,box,color=(0,255,0),thickness=2)
                    cv2.putText(img,classNames[classId-1].upper(),(box[0]+10,box[1]+30),
                    cv2.FONT_HERSHEY_COMPLEX,1,(0,255,0),2)
                    cv2.putText(img,str(round(confidence*100,2)),(box[0]+200,box[1]+30),
                    cv2.FONT_HERSHEY_COMPLEX,1,(0,255,0),2)
                    X = int((box[0] + box[2]) / 2)  # X-coordinate at the center
                    Y = int((box[1] + box[3]) / 2)  # Y-coordinate at the center      
                    
                    # Display the x and y coordinates
                    cv2.putText(img, f"X: {X}, Y: {Y}", (box[0] + 10, box[1] + 60),
                                cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)  

    return img,objectInfo,X,Y

def rescale_frame(frame, percent):
    width = int(frame.shape[1] * percent/ 100)
    height = int(frame.shape[0] * percent/ 100)
    dim = (width, height)
    return cv2.resize(frame, dim, interpolation =cv2.INTER_AREA)

def getAdjustment(windowMax, x):
    normalised_adjustment = x/windowMax - 0.5
    adjustment_magnitude = abs(round(normalised_adjustment,1))

    if normalised_adjustment>0:
        adjustment_direction = -1
    else:
        adjustment_direction = 1
        
    return adjustment_magnitude, adjustment_direction


if __name__ == "__main__":

    cap = cv2.VideoCapture(0)
    cap.set(3,640)
    cap.set(4,480)
    
     

    # Constants
    cx = 1 # Have to change sign because this servo rotates in the wrong direction
    cy = 1

    Kp = 80
    Kd = 10
    servo1_now=0
    servo2_now=0
    while True:
        success, img = cap.read()
        x=0
        y=0
        result, objectInfo,x,y = getObjects(img,0.5,0.2,objects=['bird'])
        #print(objectInfo)
        img = rescale_frame(img,50)
        window = img.shape
        cv2.imshow("Output",img)
        cv2.waitKey(1)
        
        # Get adjustment
        xmag, xdir = getAdjustment(window[0], x)
        ymag, ydir = getAdjustment(window[1], y)

        if xmag is not None:
            # Proportional
            adj_Kpx = cx * Kp * xdir * xmag
            adj_Kpy = cy * Kp * ydir * ymag
            
            # Derivative
            xmag_old = xmag
            ymag_old = ymag
            
            adj_Kdx = cx * Kd * xdir * (xmag - xmag_old)
            adj_Kdy = cy * Kd * ydir * (ymag - ymag_old)
                        
            # Adjustment
            adjustment_x = adj_Kpx + adj_Kdx
            adjustment_y = adj_Kpy + adj_Kdy
            
            # Servo
            servo1_now = servo1_now + adjustment_x
            servo2_now = servo2_now + adjustment_y
            
            # Reset line of sight if instructed to look out of bounds            
            if servo1_now > 90 or servo1_now < -90:
                servo1_now = 0
            if servo2_now > 90 or servo2_now < -90:
                servo2_now = 0

            

            with open(file_path, 'r') as file:
                content = file.read()
                

            # Replace 'X' with the updated variable value
            
            updated_content = content.replace(content, f'echo {servo1_now} > /home/reda/Desktop/coordinates')

            # Write the updated content back to the file
            with open(file_path, 'w') as file:
                file.write(updated_content)
            # Read command from file
            with open(command_file_path, "r") as file:
                command = file.read().strip()

            # Execute the command in the terminal and send an Enter key press
            process = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE)
            process.communicate(input=b"\n")
            
            sleep(0.00001)

         
        xmag = 0
        xdir = 0
        ymag = 0
        ydir = 0

        