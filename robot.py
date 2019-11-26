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

#Deadzone (# in both directions)
deadzone = 200

#Connection timeout
timeout = 5.0

#Cleanup GPIO
GPIO.cleanup()


'''
Port Variables
'''
#Motors
frontLeftMotor = 0    
backLeftMotor = 1
frontRightMotor = 2
backRightMotor = 3

#RSL
# rslPin = 26         
# rslBlinkInterval = 1.0
# rslStatus = 1

'''
Initial Variables
'''
#If run is false, the program will end. If enable is false, the robot will be disabled, but may be reenabled
run = True
enable = True

#RSL thread

#Function for rsl blink thread
# def rslBlink():
#   while True:
#     #if enable == True:
#     #If RSL is off, turn it on. Otherwise, turn it off
#     rslStatus = -rslStatus + 1
#     print("working")
#     print(rslStatus)
#     time.sleep(1)

#def timeoutDetection():
#  currentTimeout -= 1
#  if currentTimeout <= 0:
#    enable == False


# currentTimeout = timeout
# rslTimer = threading.Timer(1.0, rslBlink)
# rslTimer.start()

#Disconnect Detection Thread 
#timeoutThread = threading.Timer(1.0, timeoutDetection)
#timeoutThread.start()


'''
Code
'''

#Add controller and set joysticks
joy = xbox.Joystick()
leftJoystick = joy.leftY()
rightJoystick = joy.rightX()

#Add PWM board and set frequency
pwm = PCA9685(0x40, debug=False)
pwm.setPWMFreq(50)

#Set GPIO to broadcom mode for pin reference 
GPIO.setmode(GPIO.BCM)

#Set RSL pin as an output
# GPIO.setup(rslPin, GPIO.OUT)

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

'''
Main loop- setting run to false exits program
'''
while run == True:

  #Enabled loop
  if enable == True:

    #Check if controller is connected
    if not joy.connected():
      enable = False

    #Check whether RSL should be on or off
    #     if rslStatus == 1:
    #       #Turn RSL on
    #       GPIO.output(rslPin, True)
    #     else:
    #       #Turn RSL off
    #       GPIO.output(rslPin, False)

    #Constantly poll left and right joystick positions
    leftJoystick = joy.leftY()
    rightJoystick = joy.rightX()

    #Put joystick values into arcadeDrive function to calculate output for motors
    leftOutput, rightOutput = arcadeDrive(leftJoystick, rightJoystick, True)

    #Adjust values of output to match PWM frequency
    adjustedValueLeft = (leftOutput+1)*500+1000
    adjustedValueRight = (rightOutput+1)*500+1000

    #Apply Deadzones
    if (adjustedValueLeft >= (1500 - deadzone) and adjustedValueLeft <= (1500 + deadzone)):
      adjustedValueLeft = 1500
    else: 
      if (adjustedValueRight >= (1500 - deadzone) and adjustedValueRight <= (1500 + deadzone)):
        adjustedValueRight = 1500
      #If not in the deadzone, reset timeout countdown
      else:
        currentTimeout = timeout

    #Send PWM Frequencies to motor controllers
    pwm.setServoPulse(frontLeftMotor, adjustedValueLeft)
    pwm.setServoPulse(backLeftMotor, adjustedValueLeft)
    pwm.setServoPulse(frontRightMotor, adjustedValueRight)
    pwm.setServoPulse(backRightMotor, adjustedValueRight)

    #Press X to Disable
    if joy.X() == 1:
      enable = False
  else:
    #If disabled, 
    #stop motors
    pwm.setServoPulse(frontLeftMotor, 1500)
    pwm.setServoPulse(backLeftMotor, 1500)
    pwm.setServoPulse(frontRightMotor, 1500)
    pwm.setServoPulse(backRightMotor, 1500)
  #Press Y to Enable
  if joy.Y() == 1:
    enable = True
    currentTimeout = timeout
 

  #Press start + back to exit program (run = false)
  if joy.Start() == 1 and joy.Back() == 1:
    run = False

#Double check that motors are off before exiting 
pwm.setServoPulse(frontLeftMotor, 1500)
pwm.setServoPulse(backLeftMotor, 1500)
pwm.setServoPulse(frontRightMotor, 1500)
pwm.setServoPulse(backRightMotor, 1500)

#Reset GPIO for pi
GPIO.cleanup()

#Close Joystick interface
joy.close()
