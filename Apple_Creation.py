import time
import math
import random
from pagi_api import *

cs = connectSocket("149.164.130.155", 42209)

#if you leave it blank, it will try to find the IP itself. Otherwise, you can
#type in an IP manually:
#cs = connectSocket(ip="128.113.243.43") 

#you can also type a port if you're not using the default 42209:
#cs = connectSocket(ip="128.113.243.43", port=230)

#create an agent and bind it to the port you just opened
agent = Agent(cs)

vision = Vision(cs)

while True:
    #MAIN LOOP.
    
    #check any new messages that were sent
    responses = receive(cs)
    for r in responses:
        print ("Message received: " + str(r))
            
    #Do whatever you want: send messages, etc.
    #here we make him jump with probability 10%, otherwise we print "not".
    
    #x = GameObject(agent, apple, 0, 0, 1)
    
    #agent.sendForce(10, 10)
    
    
    if random.random() < 0.5:
        #agent.findObject('apple')
        #agent.jump()
        #agent.lhand.sendForce(-500, 300)
        #agent.resetRotation()
        #agent.moveH()
        #print(agent.lhand.getCoordinates())
        #print(agent.lhand.getDist(0,0))
        #agent.lhand.grab()
        #agent.lhand.release()
        #vision.update()
        print(vision.vision)
        print(vision.getObject("bacon"))
        pass

    else:
        print ("not")

#agent.resetRotation()

closeClient(cs)

exit()