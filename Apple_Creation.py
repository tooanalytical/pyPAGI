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
item = Items(cs)

def read_file(filepath, trans_x, trans_y):
    with open(filepath, 'r') as the_file:
        for y,line in enumerate(reversed(list(the_file))):
            for x,character in enumerate(line):
                if character == '1':
                    item.create_item('wall'+str(x)+'_'+str(y), '/Users/brandonyoung/Desktop/brickWall.jpg', x+trans_x, y+trans_y)
                if character ==  '2':
                    item.create_item('roomba','/Users/brandonyoung/Desktop/roomba.jpeg', 3*(x+trans_x), 3*(y+trans_y))

read_file('/Users/brandonyoung/Desktop/TestStream.txt', -30, 3)

try:
    while True:
        # Check any new messages that were sent
        responses = receive(cs)
        for r in responses:
            print("Message received: " + str(r))

        # x = GameObject(agent, apple, 0, 0, 1)

        if random.random() < 0.5:
            # agent.find_object('apple')
            # agent.jump()  # WORKING
            # agent.left_hand.send_force(-50000, 30000) # WORKING
            # agent.right_hand.send_force(50000, -30000)  # WORKING
            # agent.reset_rotation() # WORKING
            # agent.move_agent(-5) # WORKING
            # print(agent.left_hand.get_coordinates()) # WORKING
            # print(agent.left_hand.get_distance(0, 0)) # WORKING
            # agent.left_hand.grab()
            # agent.left_hand.release()
            # vision.update()
            # print(vision.vision)
            # print(vision.get_object("bacon"))
            # agent.left_hand.move_hand(30, 50)
            # agent.bring_hand_close(left_or_right = 'R')
            # item.drop_item('apple', 10, 10) # WORKING
            # item.create_item('wall2', '/Users/brandonyoung/Desktop/brickWall.jpg', '13', '11', '50', '1', '0', '0', '0')
            break
        else:
            print("not")

    # agent.reset_rotation()
    # item.drop_item('apple', 10, 10)
finally:
    close_client(cs)
