from PCA9685 import PCA9685
import time
import math
import smbus
import xbox

joy = xbox.Joystick()
leftJoystick = joy.leftY()
rightJoystick = joy.rightX()

pwm = PCA9685(0x40, debug=True)
pwm.setPWMFreq(50)

run = True
enable = True

def arcadeDrive(xSpeed, zRotation, squareInputs):
    xSpeed = max(min(xSpeed, 1.0), -1.0)
    zRotation = max(min(zRotation, 1.0), -1.0)

    if squareInputs:
      xSpeed = math.copysign(xSpeed * xSpeed, xSpeed)
      zRotation = math.copysign(zRotation * zRotation, zRotation)

    maxInput = math.copysign(max(abs(xSpeed), abs(zRotation)), xSpeed)

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
    return leftMotorOutput, rightMotorOutput;




while run == True:
  if enable == True:
    leftJoystick = joy.leftY()
    rightJoystick = joy.rightX()
    leftOutput, rightOutput = arcadeDrive(leftJoystick, rightJoystick, True)
    adjustedValueLeft = (leftOutput+1)*500+1000
    adjustedValueRight = (rightOutput+1)*500+1000
    pwm.setServoPulse(0, adjustedValueLeft)
    pwm.setServoPulse(1, adjustedValueLeft)
    pwm.setServoPulse(2, adjustedValueRight)
    pwm.setServoPulse(3, adjustedValueRight)
    if joy.X() == 1:
      enable = False
    if joy.Y() == 1:
      enable = True
  if joy.Start() == 1 and joy.Back() == 1:
    run = False


joy.close()
