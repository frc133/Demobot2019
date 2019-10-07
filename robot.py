from PCA9685 import PCA9685
import time
import math
import smbus
import xbox

'''
Option Variables
'''
#Drag to correct robot drive, -1.0 to 1.0
drag = 0.0
#Speed multiplier 
speedMultiplier = 0.8 



#Add controller and set joysticks
joy = xbox.Joystick()
leftJoystick = joy.leftY()
rightJoystick = joy.rightX()

#Add PWM board and set frequency
pwm = PCA9685(0x40, debug=True)
pwm.setPWMFreq(50)

#If run is false, the program will end. If enable is false, the robot will be disabled, but may be reenabled
run = True
enable = True

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



#Main loop- setting run to false exits program
while run == True:
  #Enabled loop
  if enable == True:
    #Constantly poll left and right joystick positions
    leftJoystick = joy.leftY()
    rightJoystick = joy.rightX()
    #Put joystick values into arcadeDrive function to calculate output for motors
    leftOutput, rightOutput = arcadeDrive(leftJoystick, rightJoystick, True)
    #Adjust values of output to match PWM frequency
    adjustedValueLeft = (leftOutput+1)*500+1000
    adjustedValueRight = (rightOutput+1)*500+1000
    #Send PWM Frequencies to motor controllers
    pwm.setServoPulse(0, adjustedValueLeft)
    pwm.setServoPulse(1, adjustedValueLeft)
    pwm.setServoPulse(2, adjustedValueRight)
    pwm.setServoPulse(3, adjustedValueRight)
    #Press X to Disable
    if joy.X() == 1:
      enable = False
    #Press Y to Enable
    if joy.Y() == 1:
      enable = True
  #Press start + back to exit program (run = false)
  if joy.Start() == 1 and joy.Back() == 1:
    run = False

#Close Joystick interface
joy.close()
