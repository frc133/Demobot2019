import threading 
import time


start = True

def threadA(): 
    rslStatus = 1
    while True:
        print("it works")
        rslStatus = -rslStatus + 1
        time.sleep(1)
        


thread = threading.Timer(1.0, threadA)
thread.start()

i = 1
while True:
    print("a")
    time.sleep(2)
    print(thread.rslStatus)
