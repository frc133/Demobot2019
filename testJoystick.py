import time
import math
import smbus
import xbox


def deadzone(value):
  if value >= 1400.0 and value <= 1600.0:
    value = 1500.0
  return value


joy = xbox.Joystick()
leftJoystick = joy.leftY()
rightJoystick = joy.rightX()

run = True

while run == True:
  leftJoystick = deadzone(joy.leftY())
  rightJoystick = deadzone(joy.rightX())
  adjustedValueLeft = (leftJoystick+1)*500+1000
  
  adjustedValueRight = (rightJoystick+1)*500+1000
  print(str(adjustedValueLeft) + " - " + str(adjustedValueRight))
  if joy.Start() == 1 and joy.Back() == 1:
    run = False

joy.close()

print("Exit normally")
