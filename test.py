import xbox

joy = xbox.Joystick()

yaxis = joy.leftY()

run = True

while run == True:
  yaxis = joy.leftY()
  adjustedValue = (yaxis+1)*500+1000
  print(adjustedValue)
  
joy.close()
