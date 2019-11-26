from PCA9685 import PCA9685 #Library for PWM board
# import time
import math
# import smbus
import xbox
import RPi.GPIO as GPIO


'''
Option Variables
'''
#Drag to correct robot drive, -1.0 to 1.0, positive is right
drag = -.3

#Speed multiplier
speedXMultiplier = 0.8
speedYMultiplier = 0.7

#Deadzone (# in both directions)
deadzone = .07

'''
Port Variables
'''
#Motors
frontLeftMotor = 0
backLeftMotor = 1
frontRightMotor = 2
backRightMotor = 3


#Drive functions for 2-joystick control, adapted from wpilibj differentialdrive class
#xSpeed is forward and backward on the left joystick, zRotation is left and right on the right joystick
def arcadeDrive(xSpeed, zRotation, squareInputs):

  if abs(xSpeed) <= deadzone:
      xSpeed = 0
  if abs(zRotation) <= deadzone:
      zRotation = 0

  #Add speed multiplier
  xSpeed = xSpeed * speedXMultiplier
  zRotation = zRotation * speedYMultiplier

  #Add Drag to correct robot drift
  if abs(zRotation) < deadzone:
    if abs(xSpeed) > deadzone:
      zRotation += drag

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
  return leftMotorOutput, rightMotorOutput


#Adjust value -1.0 to 1.0 to match PWM frequency 1000 to 2000
def adjustForPWM(value):
  adjustedValue = ((value+1)*500)+1000
  return adjustedValue


#Apply Deadzone for PWM values
#def applyDeadzone(value):
#  if (value >= (1500 - deadzone) and value <= (1500 + deadzone)):
#    value = 1500
#  return value


'''
Main code starts here
'''

try:

  #Add controller and set joysticks
  joy = xbox.Joystick()

  # Arcade drive, left Y and right X
  leftJoystick = joy.leftY()
  rightJoystick = joy.rightX()

  #Add PWM board and set frequency
  pwm = PCA9685(0x40, debug=False)
  pwm.setPWMFreq(50)

  #Set GPIO to broadcom mode for pin reference
  GPIO.setmode(GPIO.BCM)

  '''
  Initial Variables
  '''
  #If run is false, the program will end. If enable is false, the robot will be disabled, but may be reenabled
  run = True
  enable = True

  '''
  Main loop- setting run to false exits program
  '''

  while run == True:

    #Check if controller is connected
    if not joy.connected():

      enable = False
      print("Joystick not connected...")

    else:

      #Press start + back to exit program (run = false, enable = false)
      if joy.Start() == 1 and joy.Back() == 1:

        run = False
        enable = False
        print("Start + Back detected - exiting normally")

      else:
      
        #Press Y to Enable
        if joy.Y() == 1:
          enable = True
          print("Y button pressed - enabling...")

        #Press X to Disable
        if joy.X() == 1:
          enable = False
          print("X button pressed - disabling...")

        #Adjust Drag
        if joy.A() == 1:
            drag += .001

        if joy.B() == 1:
            drag -= .001

    #Enabled loop
    if enable == True:

      #Constantly poll left and right joystick positions
      # Arcade drive, left Y and right X
      leftJoystick = joy.leftY()
      rightJoystick = joy.rightX()

      #Put joystick values into arcadeDrive function to calculate output for motors
      leftOutput, rightOutput = arcadeDrive(leftJoystick, rightJoystick, True)

      #Adjust values of output to match PWM frequency
      adjustedValueLeft = adjustForPWM(leftOutput)
      adjustedValueRight = adjustForPWM(rightOutput)

      #Apply Deadzones
      #adjustedValueLeft = applyDeadzone(adjustedValueLeft)
      #adjustedValueRight = applyDeadzone(adjustedValueRight)

      #Send PWM Frequencies to motor controllers
      pwm.setServoPulse(frontLeftMotor, adjustedValueLeft)
      pwm.setServoPulse(backLeftMotor, adjustedValueLeft)
      pwm.setServoPulse(frontRightMotor, adjustedValueRight)
      pwm.setServoPulse(backRightMotor, adjustedValueRight)

    else:

      #If disabled,
      #stop motors
      pwm.setServoPulse(frontLeftMotor, 1500)
      pwm.setServoPulse(backLeftMotor, 1500)
      pwm.setServoPulse(frontRightMotor, 1500)
      pwm.setServoPulse(backRightMotor, 1500)

except KeyboardInterrupt:

  # Handle Ctrl-C interrupt here
  print("\nKeyboard Interrupt detected...")

except:

  # Any exception code here
  print("\nError occurred in code!")

finally:

  print("\nDone")

  try:

    #Double check that motors are off before exiting
    pwm.setServoPulse(frontLeftMotor, 1500)
    pwm.setServoPulse(backLeftMotor, 1500)
    pwm.setServoPulse(frontRightMotor, 1500)
    pwm.setServoPulse(backRightMotor, 1500)

    #Close Joystick interface
    joy.close()

  except:

    # Handle final pwm exceptions
    print("\nAnother exception error at end")

  finally:

    #Reset GPIO for pi as last statement
    GPIO.cleanup()

