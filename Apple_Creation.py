from __future__ import print_function
from pagi_api import *
import random

# If you leave it blank it will try to find the IP itself.
# Otherwise, you can type in an IP manually:
# cs = connectSocket(ip="128.113.243.43")

# You can also type a port if you're not using the default 42209:
# cs = connectSocket(ip="128.113.243.43", port=230)

# Create an interface to talk to the agent through.
cs = connect_socket("149.164.130.155", 42209)

# Create an agent and bind it to the port you just opened.
agent = Agent(cs)

vision = Vision(cs)

while True:
    # Check any new messages that were sent
    responses = receive(cs)
    for r in responses:
        print("Message received: " + str(r))

    # x = GameObject(agent, apple, 0, 0, 1)
    
    if random.random() < 0.5:
        # agent.find_object('apple')
        # agent.jump()
        # agent.left_hand.send_force(-500, 300)
        # agent.reset_rotation()
        # agent.moveH()
        # print(agent.left_hand.get_coordinates())
        # print(agent.left_hand.get_distance(0, 0))
        # agent.left_hand.grab()
        # agent.left_hand.release()
        # vision.update()
        # # print(vision.vision)
        # print(vision.get_object("bacon"))
        pass
    else:
        print("not")

# agent.resetRotation()

close_client(cs)
