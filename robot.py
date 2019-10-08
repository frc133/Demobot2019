from PCA9685 import PCA9685 #Library for PWM board
import time
import math
import smbus 
import xbox
import RPi.GPIO as GPIO
import threading 

'''
Option Variables
'''
#Drag to correct robot drive, -1.0 to 1.0, positive is right
drag = -0.1

#Speed multiplier 
speedMultiplier = 0.8 


'''
Port Variables
'''
#Motors
frontLeftMotor = 0     #I may have front and back switched currently
backLeftMotor = 1
frontRightMotor = 2
backRightMotor = 3

#RSL
rslPin = 26             #CHECK THIS!!!!
rslBlinkInterval = 1.0


'''
Initial Variables
'''
#If run is false, the program will end. If enable is false, the robot will be disabled, but may be reenabled
run = True
enable = True

#RSL status
rslStatus = 0

#RSL thread
rslTimer = threading.timer(rslBlinkInterval, rslBlink)
rslTimer.start()

'''
Code
'''

#Add controller and set joysticks
joy = xbox.Joystick()
leftJoystick = joy.leftY()
rightJoystick = joy.rightX()

#Add PWM board and set frequency
pwm = PCA9685(0x40, debug=True)
pwm.setPWMFreq(50)

#Set GPIO to broadcom mode for pin reference 
GPIO.setmode(GPIO.BCM)

#Set RSL pin as an output
GPIO.setup(rslPin, GPIO.OUT)

#Drive functions for 2-joystick control, adapted from wpilibj differentialdrive class
#xSpeed is forward and backward on the left joystick, zRotation is left and right on the right joystick
def arcadeDrive(xSpeed, zRotation, squareInputs):

    #Add speed multiplier 
    xSpeed = xSpeed * speedMultiplier

    #Add Drag to correct robot drift
    xSpeed += drag

    #Clamp xSpeed and zRotation to -1.0 to 1.0
    xSpeed = max(min(xSpeed, 1.0), -1.0)
    zRotation = max(min(zRotation, 1.0), -1.0)

    #Square inputs to control speed at a curve
    if squareInputs:
      xSpeed = math.copysign(xSpeed * xSpeed, xSpeed)
      zRotation = math.copysign(zRotation * zRotation, zRotation)

    #maxInput math for setting speeds
    maxInput = math.copysign(max(abs(xSpeed), abs(zRotation)), xSpeed)

    #If statements seperating turning and direction into quadrants
    if xSpeed >= 0.0:
        if zRotation >= 0.0:
          #First Quadrant
          leftMotorOutput = maxInput
          rightMotorOutput = xSpeed - zRotation
        else:
          #Second Quadrant
          leftMotorOutput = xSpeed + zRotation
          rightMotorOutput = maxInput
    else:
      if zRotation >= 0.0:
        #Third Quadrant
        leftMotorOutput = xSpeed + zRotation
        rightMotorOutput = maxInput
      else:
        #Fourth Quadrant
        leftMotorOutput = maxInput
        rightMotorOutput = xSpeed - zRotation
    #Returns left and right motor output values between -1.0 and 1.0 as a tuple
    return leftMotorOutput, rightMotorOutput;

#Function for rsl blink thread
def rslBlink():
  if enable == true:
    #If RSL is off, turn it on. Otherwise, turn it off
    if rslStatus == 0:
      rslStatus = 1
    else 
      rslStatus = 0
  else:
    rslStatus = 1

'''
Main loop- setting run to false exits program
'''
while run == True:
  #Enabled loop
  if enable == True:

    #Check whether RSL should be on or off
    if rslStatus == 1:
      #Turn RSL on
      GPIO.output(rslPin, GPIO.HIGH)
    else:
      #Turn RSL off
      GPIO.output(rslPin, GPIO.LOW)

    #Constantly poll left and right joystick positions
    leftJoystick = joy.leftY()
    rightJoystick = joy.rightX()

    #Put joystick values into arcadeDrive function to calculate output for motors
    leftOutput, rightOutput = arcadeDrive(leftJoystick, rightJoystick, True)

    #Adjust values of output to match PWM frequency
    adjustedValueLeft = (leftOutput+1)*500+1000
    adjustedValueRight = (rightOutput+1)*500+1000

    #Send PWM Frequencies to motor controllers
    pwm.setServoPulse(frontLeftMotor, adjustedValueLeft)
    pwm.setServoPulse(backLeftMotor, adjustedValueLeft)
    pwm.setServoPulse(frontRightMotor, adjustedValueRight)
    pwm.setServoPulse(backRightMotor, adjustedValueRight)

    #Press X to Disable
    if joy.X() == 1:
      enable = False
    #Press Y to Enable
    if joy.Y() == 1:
      enable = True
      
  #Press start + back to exit program (run = false)
  if joy.Start() == 1 and joy.Back() == 1:
    run = False


#Reset GPIO for pi
GPIO.cleanup()

#Close Joystick interface
joy.close()
