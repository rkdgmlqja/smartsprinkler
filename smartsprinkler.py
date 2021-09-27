#-*- coding:utf-8 -*-
import math
import numpy as np
import cv2
import sys
from picamera import PiCamera
from time import sleep
import RPi.GPIO as GPIO #RPi.GPIO 라이브러리를 GPIO로 사용
from time import sleep  #time 라이브러리의 sleep함수 사용

servoPin1          = 11
servoPin2          = 12
servoPin3          = 13  # 서보 핀
SERVO_MAX_DUTY    = 12   # 서보의 최대(180도) 위치의 주기
SERVO_MIN_DUTY    = 3    # 서보의 최소(0도) 위치의 주기

GPIO.setmode(GPIO.BOARD)        # GPIO 설정
GPIO.setup(servoPin1, GPIO.OUT)  # 서보핀 출력으로 설정
GPIO.setup(servoPin2, GPIO.OUT)
GPIO.setup(servoPin3, GPIO.OUT)
servo1 = GPIO.PWM(servoPin1, 50)  # 서보핀을 PWM 모드 50Hz로 사용하기 (50Hz > 20ms)
servo2 = GPIO.PWM(servoPin2, 50)
servo3 = GPIO.PWM(servoPin3, 50)
servo1.start(0)  # 서보 PWM 시작 duty = 0, duty가 0이면 서보는 동작하지 않는다.
servo2.start(0)
servo3.start(0)

'''
서보 위치 제어 함수
degree에 각도를 입력하면 duty로 변환후 서보 제어(ChangeDutyCycle)
'''
def setServoPos1(degree):
  # 각도는 180도를 넘을 수 없다.
  if degree > 180:
    degree = 190
  # 각도(degree)를 duty로 변경한다.
  duty = SERVO_MIN_DUTY+(degree*(SERVO_MAX_DUTY-SERVO_MIN_DUTY)/180.0)
  # duty 값 출력
  print("Degree: {} to {}(Duty)".format(degree, duty))

  # 변경된 duty값을 서보 pwm에 적용
  servo1.ChangeDutyCycle(duty)

def setServoPos2(degree):
  # 각도는 180도를 넘을 수 없다.
  if degree > 180:
    degree = 190
  # 각도(degree)를 duty로 변경한다.
  duty = SERVO_MIN_DUTY+(degree*(SERVO_MAX_DUTY-SERVO_MIN_DUTY)/180.0)
  # duty 값 출력
  print("Degree: {} to {}(Duty)".format(degree, duty))

  # 변경된 duty값을 서보 pwm에 적용
  servo2.ChangeDutyCycle(duty)

def setServoPos3(degree):
  # 각도는 180도를 넘을 수 없다.
  if degree > 180:
    degree = 190
  # 각도(degree)를 duty로 변경한다.
  duty = SERVO_MIN_DUTY+(degree*(SERVO_MAX_DUTY-SERVO_MIN_DUTY)/180.0)
  # duty 값 출력
  print("Degree: {} to {}(Duty)".format(degree, duty))

  # 변경된 duty값을 서보 pwm에 적용
  servo3.ChangeDutyCycle(duty)

def Area(section) :
 if(section ==5 ):
  setServoPos1(10)
  setServoPos2(90)
  setServoPos3(190)
  sleep(1)

 else:
  print("error")
 
 if(section ==6):
  setServoPos1(190)
  setServoPos2(70)
  setServoPos3(150)
  sleep(1)
 
 if(section ==1 ):
  setServoPos1(190)
  setServoPos2(10)
  setServoPos3(90)
  sleep(1)

 if(section ==2 ):
  setServoPos1(150)
  setServoPos2(190)
  setServoPos3(70)
  sleep(1)
 
 if(section ==3):
  setServoPos1(90)
  setServoPos2(190)
  setServoPos3(10)
  sleep(1)
 

 if(section ==4 ):
  setServoPos1(70)
  setServoPos2(150)
  setServoPos3(190)
  sleep(1)
 

 if(section ==0):
  setServoPos1(-30)
  setServoPos2(-30)
  setServoPos3(-30)
  sleep(1)





#극좌표변환함수
def cart2pol(x, y):
    rho = np.sqrt(x**2 + y**2)
    
    d= 180/math.pi*np.arctan2(y, x)
    return(rho, d)




#카메라 초기설정
camera = PiCamera()
camera.rotation = 180
camera.resolution = (640,480)

#카메라좌표
camx=320
camy=240

while (1):
    sleep(1)
    
    #사진촬영
    camera.capture('/home/pi/Desktop/image.jpg')
    
    #촬영한 사진 불러옴
    src = cv2.imread('/home/pi/Desktop/image.jpg') 
    
    #mask이미지 불러옴
    mask = cv2.imread('/home/pi/Desktop/mask.png')
    
    #meanshift알고리즘 적용
    src1	=	cv2.pyrMeanShiftFiltering(src, sp = 13, sr = 13, maxLevel = 4) 
    mask1	=	cv2.pyrMeanShiftFiltering(mask, sp = 13, sr = 13, maxLevel = 4)



    #히스토그램 생성을위해 타입변환
    src_ycrcb = cv2.cvtColor(src1, cv2.COLOR_BGR2YCrCb)        

    crop = cv2.cvtColor(mask1, cv2.COLOR_BGR2YCrCb)


    
    channels = [1, 2]  # 0인덱스인 y 성분은 쓰지 않음. y 성분은 밝기 정보.
    cr_bins = 128      # cr을 표현하는 범위. 256을 128로 단순화.
    cb_bins = 128
    histSize = [cr_bins, cb_bins]
    cr_range = [0,256]
    cb_range = [0,256]
    ranges = cr_range + cb_range
    
    # 히스토그램 생성
    hist = cv2.calcHist([crop], channels, None, histSize, ranges) # 리스트 입력
    
    # 히스토그램 스트레칭
    
    hist_norm = cv2.normalize(cv2.log(hist + 1), None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
    
    # 히스토그램 역투영으로 마스크 생성
    backproj = cv2.calcBackProject([src_ycrcb], channels, hist, ranges, 1)
    
    kernel = np.ones((3,3),np.uint8)
    
    
    # 오프닝과 클로징으로 노이즈 제거
    #opening = cv2.morphologyEx(backproj, cv2.MORPH_CLOSE, kernel)
    gt1 = cv2.morphologyEx(backproj, cv2.MORPH_OPEN, kernel)
    gt2= erode=cv2.erode(gt1, kernel)
    gt3= erode=cv2.erode(gt2, kernel)
    #erode=cv2.erode(opening, kernel)
    closing = cv2.morphologyEx(gt3, cv2.MORPH_OPEN, kernel)
    gt4 = erode=cv2.erode(closing,kernel)


    # 마스크 연산
    dst = cv2.copyTo(src, backproj)
    dstg= cv2.cvtColor(dst, cv2.COLOR_BGR2GRAY)
    cnt, labels, stats, centroids = cv2.connectedComponentsWithStats(dstg)
    
    X=0
    Y=0
    centermassxsum=0
    centermassysum=0
    areasum=0
    centermassx=0
    centermassy=0
    #for i in range(1, cnt):
       # (x, y, w, h, area) = stats[i]
        #centermassxsum+= x*area
        #centermassysum+= y*area
        #areasum+=area    
        
        #centermassx= centermassxsum/areasum
        #centermassy= centermassysum/areasum
    #if cnt==1:
    (cordx, cordy, W, H, area) =stats[cnt//2]
    #cordx=centermassx
    #cordy=centermassy
        
    X=cordx-camx +15
    Y=cordy-camy +15
    r,ceta=cart2pol(X,Y)
    input=0
    if (X==-305 and Y==215):
        input=7
    elif(ceta<120 and ceta>=60):
        input=1
    elif(ceta<60 and ceta>=0):
        input=2
    elif(ceta<0 and ceta>=-60):
        input=3
    elif(ceta<-60 and ceta>=-120):
        input=4
    elif(ceta<-120 and ceta>=-180):
        input=5
    elif(ceta<180 and ceta>=120):
        input=6
    print(X,Y)
    print(ceta)
    print(input)
    Area(input)
        
        
        
        
    #if (cnt!=1):
        #break
        
    
        
        
        
        
        
        
        
        
        
        
        
        
            
