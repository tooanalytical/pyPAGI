import time
import math
import random
from pagi_api import *

cs = connectSocket("25.10.181.48", 42209)

#if you leave it blank, it will try to find the IP itself. Otherwise, you can
#type in an IP manually:
#cs = connectSocket(ip="128.113.243.43") 

#you can also type a port if you're not using the default 42209:
#cs = connectSocket(ip="128.113.243.43", port=230)

#create an agent and bind it to the port you just opened
agent = Agent(cs)


while True:
    #MAIN LOOP.
    
    #check any new messages that were sent
    responses = getMessages(cs)
    for r in responses:
        if r != "":
            print ("Message received: " + str(r))
            #Do anything you want with the message here...
            
    #Do whatever you want: send messages, etc.
    #here we make him jump with probability 10%, otherwise we print "not".
    
    #x = GameObject(agent, apple, 0, 0, 1)
    
    #agent.sendForce(10, 10)
    
    
    if random.random() < 0.5:
        #agent.findObject('apple')
        #agent.jump()
        #agent.sendForce(-5000, 3000)
        #agent.resetRotation()
        #agent.moveH()
        print(agent.lhand.getCoordinates())

    else:
        print ("not")

#agent.resetRotation()

closeClient(cs)

exit()