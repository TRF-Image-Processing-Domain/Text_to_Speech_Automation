import cv2
import time 
import pytesseract
import os
import numpy as np
from gtts import gTTS   

pytesseract.pytesseract.tesseract_cmd = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

currentFile = ""
currentTime = ""

clickStatus = False
def mouse_click(event, x, y,  
                flags, param): 
    global clickStatus
    global currentFile
    global currentTime
    # to check if left mouse  
    # button was clicked 
    if event == cv2.EVENT_LBUTTONDOWN: 
        currentTime = str(int(time.time()))
        currentFile = "Text_Images/" + currentTime + ".jpg"
        cv2.imwrite(currentFile, img)
        print("Image saved")
        clickStatus = True


cap = cv2.VideoCapture(0) 
  
while(True): 
    ret, img = cap.read() 

    font = cv2.FONT_HERSHEY_TRIPLEX 
    # cv2.putText(img, "Left click to capture image", (40, 20), font, 1, (255, 255, 0), 2)  

    cv2.imshow("Left click to capture image", img)

    cv2.setMouseCallback('Left click to capture image', mouse_click)   
    # print(clickStatus)
    if cv2.waitKey(1) & 0xFF == ord('q') or clickStatus == True: 
        break

cap.release() 
cv2.destroyAllWindows() 


img = cv2.imread(currentFile)

gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) 

# Performing OTSU threshold 
ret, thresh1 = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV) 
#cv2.imshow("thresh", cv2.resize(thresh1, (1000, 700)))
# Appplying dilation on the threshold image 
dilation = cv2.dilate(thresh1, (3, 3), iterations = 1)
#cv2.imshow("dilation", cv2.resize(dilation, (1000, 700))) 

coords = np.column_stack(np.where(thresh1 > 0))
angle = cv2.minAreaRect(coords)[-1]

if angle < -45:
    angle = -(90 + angle)
else:
    angle = -angle

(h, w) = img.shape[:2]
center = (w // 2, h // 2)
M = cv2.getRotationMatrix2D(center, angle, 1.0)
rotated = cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

# cv2.putText(rotated, "Angle: {:.2f} degrees".format(angle), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
# show the output img
# print("[INFO] angle: {:.3f}".format(angle))

# # Finding contours 
contours, hierarchy = cv2.findContours(dilation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE) 
for cnt in contours: 
    x, y, w, h = cv2.boundingRect(cnt) 
    
    # Drawing a rectangle on copied image 
    cv2.rectangle(img, (x, y), (x + w, y + h), (255, 255, 0), 2) 

cv2.imshow("Input", img)
cv2.imshow("Rotated", rotated)
cv2.waitKey(0)

text = pytesseract.image_to_string(rotated)
#print(type(text))

file = open("Text_Recognized/" + currentTime + ".txt", "w+") 
file.write(text) 
file.close() 
print("\nText file saved")

# Language in which you want to convert 
language = 'en'

myobj = gTTS(text=text, lang=language, slow=False) 

try:
    myobj.save("Text_Audio/" + currentTime + ".mp3")  
    print("Audio file saved\n")
except:
    print("Unexpected error, audio unsaved :(\n")