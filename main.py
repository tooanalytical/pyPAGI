from __future__ import print_function
from pagi_api import *
import time


def main():
    # Create an interface to talk to the agent through.
    # You can also type a port if you're not using the default 42209:
    # If you leave the IP blank it will try to find the IP itself,
    # otherwise, you can type in an IP manually.
    cs = connect_socket()

    # Create an agent and bind it to the port you just opened.
    agent = Agent(cs)

    while True:
        # Check any new messages that were sent
        # responses = receive(cs)
        # print(responses)

        # Adjust this value as needed for your own stability.
        time.sleep(0.01)

        # print(agent.find_object('steak'))
        # agent.jump()
        # agent.left_hand.apply_force(-500, 300)
        # agent.reset_rotation()
        print(agent.left_hand.get_coordinates())
        print(agent.left_hand.get_distance(0, 0))
        # agent.left_hand.grab()
        # agent.left_hand.release()
        # agent.vision.update()
        # print(agent.left_hand.move_to(0,0))
        # print(vision.vision)
        # print(agent.vision.get_object("bacon"))

    # agent.resetRotation()

    close_client(cs)

if __name__ == "__main__":
    main()
