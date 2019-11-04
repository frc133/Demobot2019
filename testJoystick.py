import time
import math
import smbus
import xbox


def deadzone(value):
  if value >= 1400.0 and value <= 1600.0:
    value = 1500.0
  return value


def squareInput(value):
  if value < 0:
    return value * value * -1
  return value * value


def adj2pwm(value):
  return (value+1)*500+1000


joy = xbox.Joystick()
leftJoystick = joy.leftY()
rightJoystick = joy.rightX()

run = True

while run == True:
  leftJoystick = joy.leftY()
  rightJoystick = joy.rightY()
  adjustedValueLeft = deadzone(adj2pwm(squareInput(leftJoystick)))
  adjustedValueRight = deadzone(adj2pwm(squareInput(rightJoystick)))
  print(str(adjustedValueLeft) + " - " + str(adjustedValueRight))
  if joy.Start() == 1 and joy.Back() == 1:
    run = False

joy.close()

print("Exit normally")
