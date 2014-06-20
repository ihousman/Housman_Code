#!/usr/bin/python

##import threading
##import time
##
##exitFlag = 0
##
##class myThread (threading.Thread):
##    def __init__(self, threadID, name, counter):
##        threading.Thread.__init__(self)
##        self.threadID = threadID
##        self.name = name
##        self.counter = counter
##    def run(self):
##        print "Starting " + self.name
##        print_time(self.name, self.counter, 5)
##        print "Exiting " + self.name
##
##def print_time(threadName, delay, counter):
##    while counter:
##        if exitFlag:
##            thread.exit()
##        time.sleep(delay)
##        print "%s: %s" % (threadName, time.ctime(time.time()))
##        counter -= 1
##
### Create new threads
##thread1 = myThread(1, "Thread-1", 1)
##thread2 = myThread(2, "Thread-2", 2)
##
### Start new Threads
##thread1.start()
##thread2.start()
##
##print "Exiting Main Thread"
import time
from threading import Thread

def myfunc(i):
    print "sleeping 5 sec from thread %d" % i
    time.sleep(5)
    print "finished sleeping from thread %d" % i

for i in range(10):
    t = Thread(target=myfunc, args=(i,))
    t.start()
