import threading
import time

#time between RSL blinks
rslInterval = .5

#RSL status: 1=ON, 0=OFF
rslStatus = 0

#Class used for the timer thread
class timerThread(threading.Thread):
  #Initialization
  def __init__(self, event):
    threading.Thread.__init__(self)

    #event used for pausing the thread
    self.stopped = event

  #Thread function that is run on a timer:
  def run(self):
    #Make the rslStatus variable global so the thread can use it
    global rslStatus
    #Thread loop
    while True:
      #Check for the stopped event, and set the interval
      if not self.stopped.wait(rslInterval):
        #Switch rslStatus between 1 and 0 using MATH
        rslStatus = 1 - rslStatus

#Create the event to stop the thread
stopFlag = threading.Event()

#Create the thread and start it
thread = timerThread(stopFlag)
thread.start()


#To pause:
#stopFlag.set()

#To Resume:
#stopFlag.clear()

#Testing:
runs = 0
while runs <= 10:
  runs += 1 
  print(rslStatus)
  time.sleep(.5)

stopFlag.set()

runs = 0
while runs <= 10:
  runs += 1 
  print(rslStatus)
  time.sleep(.5)

stopFlag.clear()

runs = 0
print("now")
while runs <= 10:
  runs += 1 
  print(rslStatus)
  time.sleep(.5)