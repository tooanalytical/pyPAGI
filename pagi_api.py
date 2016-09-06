from __future__ import print_function
import socket
import time
import math
import select
import sys

unread = []  # stores all unread messages from socket


def connect_socket(ip_address=None, port=42209):
    """
    Sets up the socket for communication.
    :param ip_address: The IP address to connect to.
    :param port: The port to communicate through
    :return: The socket that you will need.
    """
    if ip_address is None:
        # Connect to local address.
        ip_address = socket.gethostbyname(socket.gethostname())
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((ip_address, port))
        client_socket.setblocking(0)
        return client_socket
    except ConnectionRefusedError:
        print("The provided address and port refused the connection.")
        print("Check the address and port to make sure they're valid.")
        print("If all else fails, restart PAGI World, especially if you've "
              "switched networks since you last started it.")
        sys.exit(1)


def close_client(client_socket):
    """
    Closes connection to PAGI World; must be called to interact with pagi_api outside of pagi_api.py
    """
    client_socket.close()


def send(message, client_socket, encode_message=True, return_response=False):
    """
    WARNING: seems to randomly ignore responses from the socket, causing an infinite loop
    (possibly) PREVENTS client_socket.recv FROM WORKING OUTSIDE THIS FUNCTION
    calls socket.send(out) and returns corresponding value of socket.recv()
    waits for socket to respond before exiting
    :param message: A string that is to be sent to PAGI world over the network.
    :param client_socket:
    :param encode_message:
    :param return_response: Whether the response for this command is to be automatically received and returned.
    :return: The response from the server is return_response is True, otherwise None.
    """
    if encode_message:
        message = encode(message)
    try:
        client_socket.send(message)
    except BrokenPipeError:
        print("The socket connection was reset. Please rerun the program.")
        sys.exit(1)
    if return_response:
        return receive(client_socket)


def receive(client_socket, split_on_comma=False,
            return_first_response=False, max_receive_size=16384):
    try:
        readable = select.select([client_socket], [], [], 0.25)  # timeout/1000
        if readable[0]:
            # Read message and add to messages.
            responses = decode(client_socket.recv(max_receive_size)).split('\n')
            responses = [c for c in responses if c != ""]
            if split_on_comma:
                responses = [response.split(',') for response in responses]
            return responses[0] if return_first_response else responses
        return []
    except KeyboardInterrupt:
        close_client(client_socket)
        sys.exit(0)


def encode(command):
    return str.encode(command)


def decode(bytes_object):
    return bytes_object.decode("utf-8")

    # messageType = msg.split('\n')[0].split(',')[1]
    # global unread
    # while True:
    #     # update unread with responses from socket
    #     readable = select.select([client_socket], [], [], 1)
    #     if readable[0]:
    #         # read message and add to messages
    #         responses = decode(client_socket.recv(8192)).split('\n')    # limit of 8192 characters
    #         for response in responses:
    #             if response != "":
    #                 unread.append(response)
    #     # search unread messages for match with current call; remove and return if found
    #     for message in unread:
    #         responseType = message.split(',')[0]
    #         if responseType == messageType:
    #             unread.remove(message)
    #             return message


class Body:
    """
    Holds body sensors.
    """

    def __init__(self, client_socket):
        self.client_socket = client_socket
        self.sensors = [None] * 8

    def apply_force(self, x, y):
        send('addForce,BHvec,{x},{y}\n'.format(x=x, y=y), self.client_socket, return_response=True)

    def get_sensor(self, index=None):
        """
        :param index: The index of the sensor reading to retrieve.

            If num is unspecified, returns a list of all body sensor readings.
            0 is top, increases counterclockwise.
                0
              1   7
            2   A   6
              3   5
                4
        :return: A string of the form s,p,tmp,tx1,tx2,tx3,tx4,e, where:

            • s - the sensor’s code
            • p - 0 if the sensor detects nothing (in which case all following values will be 0),
                1 if something was detected
            • tmp - The temperature value detected, as a float
            • tx1-tx4 - The texture detected. This is four floats meant to describe the
                quality of the texture.
            • e - Body sensors only. This is the amount of ”direct pleasure” the agent is
                currently feeling from that sensor. e.g., if the B0 sensor is touching a reward
                object, then this sensor will return a positive value for e. If it is touching a
                pain object, then it will return a negative value
        """
        if index is not None:
            send('sensorRequest,B{n}\n'.format(n=index), self.client_socket)
            response = receive(self.client_socket, split_on_comma=True)
            self.sensors[index] = response
        else:
            for index in range(8):
                self.sensors[index] = send('sensorRequest,B{n}\n'.format(n=index),
                                           self.client_socket, return_response=True)
            response = self.sensors
        return response


class Hand:
    def __init__(self, hand_string, client_socket):
        self.client_socket = client_socket
        hand_string = hand_string.upper()
        self.hand = hand_string[0] if len(hand_string) > 1 else hand_string
        assert self.hand in ["L", "R"]
        self.closed = False
        self.holding_object = False
        self.sensors = [None] * 5

    def get_coordinates(self, absolute_coordinates=False):
        """
        Get the coordinates of the hand relative to the agent's body.
        :param absolute_coordinates: Unimplemented.
        Considering allowing the coordinates to either be relative to the origin or relative to the agent.
        :return: (X, Y) coordinates of hand relative to body
        """
        send('sensorRequest,{h}P\n'.format(h=self.hand), self.client_socket)
        current_location = receive(self.client_socket, split_on_comma=True, return_first_response=True)
        return float(current_location[1]), float(current_location[2])

    def get_distance(self, x, y):
        """
        Get distance from position (x,y)
        :param x: Location in the x-axis.
        :param y: Location in the y-axis.
        :return: The euclidean distance to the point given.
        """
        x0, y0 = self.get_coordinates()
        return math.sqrt((x0-x)*(x0-x)+(y0-y)*(y0-y))

    def apply_force(self, x, y):
        send('addForce,{hand}Hvec,{x},{y}\n'.format(hand=self.hand, x=x, y=y), self.client_socket, return_response=True)

    def move_to(self, x, y, tolerance=1.5):
        """
        Move to point (x,y) within a specified tolerance.
        WARNING: If it is impossible to move to (x,y), this will infinite loop.
        :param x: Location in the x-axis.
        :param y: Location in the y-axis.
        :param tolerance: Minimum distance to an object before the hand is considered to be on top of it.
        :return:
        """
        # TODO: Keep track of how long the function has been looping so it doesn't loop forever.

        # Convert (x,y) from Unity item units (whatever they are) to detailed vision units (0.0 - 30.20)
        x = -2.25 + x*0.148
        y = 1.65 + y*0.1475

        # Keep a copy of unread to revert to, since this does not use send(). Oherwise, a huge number of
        # useless results would end up in unread
        global unread
        unreadCpy = unread
        # Move hand in x and y directions
        # WARNING: randomly causes problems with send().
        # Might be fixed; it is a bit random.
        # Note that this is likely caused by not receiving the socket data for the reflex functions,
        # clogging up the socket's responses in send()
        send('setReflex, lock{h}X,{h}Px|!|{x},sensorRequest|{h}P;addForce|{h}HH|[350*({x}-{h}Px)]\n'
             .format(h=self.hand, x=x), self.client_socket, return_response=True)
        send('setReflex, lock{h}Y,{h}Py|!|{y},sensorRequest|{h}P;addForce|{h}HV|[350*({y}-{h}Py)]\n'
             .format(h=self.hand, y=y), self.client_socket, return_response=True)

        # Wait until sufficiently close, then return
        while self.get_distance(x, y) > tolerance:
            time.sleep(0.5)
        unread = unreadCpy

    def grab(self):
        """
        Apply grabbing force and update holding status
        :return: None
        """
        send('addForce,{h}HG,5\n'.format(h=self.hand), self.client_socket, return_response=True)
        send('sensorRequest,{h}2\n'.format(h=self.hand), self.client_socket)
        response = receive(self.client_socket, split_on_comma=True, return_first_response=True)[1]
        self.closed = True
        if response == "1":
            self.holding_object = True

    def release(self):
        """
        Stop applying grabbing force and update holding status
        :return: None
        """
        send('addForce,{h}HR,5\n'.format(h=self.hand), self.client_socket, return_response=True)
        self.closed = False
        self.holding_object = False

    def get_sensor(self, index=None):
        """
        :param index: The index of the sensor reading to retrieve.

            If num is unspecified, returns a list of all hand sensor readings.
            0 is top, increases counterclockwise.
                  0
               1     4
                  H
                2   3
            Something like this. It's a pentagon, OK? We're CS majors, not artists.
        :return: A string of the form s,p,tmp,tx1,tx2,tx3,tx4, where:

            • s - the sensor’s code
            • p - 0 if the sensor detects nothing (in which case all following values will be 0),
                1 if something was detected
            • tmp - The temperature value detected, as a float
            • tx1-tx4 - The texture detected. This is four floats meant to describe the
                quality of the texture.
        """
        if index is not None:
            send('sensorRequest,{hand}{n}\n'.format(hand=self.hand, n=index), self.client_socket)
            response = receive(self.client_socket, split_on_comma=True)
            self.sensors[index] = response
        else:
            for index in range(5):
                self.sensors[index] = send('sensorRequest,{hand}{n}\n'.format(hand=self.hand, n=index),
                                           self.client_socket, return_response=True)
            response = self.sensors
        return response


class GameObject:
    """
    Contains data of objects encountered on Unity's side.
    May be expanded to contain additional data.
    """

    def __init__(self, object_name, x, y, is_moving):
        self.name = object_name
        self.x = x
        self.y = y
        self.is_moving = is_moving

    def __eq__(self, other):
        return self.name == other


class Items:
    """
    Contains functions responsible for creating items in the world in real-time.
    """

    # TODO: finish implementing create_item functions

    def __init__(self, client_socket):
        self.client_socket = client_socket

    def drop_item(self, name, x, y):
        send('dropItem,{name},{x},{y}\n'.format(name=name, x=x, y=y), self.client_socket)

    def create_item(self, name, file_path, x, y, mass=50, physics=1,
                    initial_rotation=0, endorphins=0, kinematic_properties=0):
        send('createItem,{name},{fp},{x},{y},{m},{phy},{init_rot},{endorphins},{k_prop}\n'
             .format(name=name, fp=file_path, x=x, y=y, m=mass, phy=physics,
                     init_rot=initial_rotation, endorphins=endorphins, k_prop=kinematic_properties),
             self.client_socket)


class Vision:
    """
    Controls the vision of the agent.
    """
    # TODO: consider storing self.objects as a dictionary for faster retrieval and just generally clean up this mess...

    def __init__(self, client_socket):
        self.client_socket = client_socket
        self.vision = []
        self.objects = []
        self.update()

    def update(self, view_type='detailed', row_length=None):
        """
        :param view_type: Must be 'detailed' or 'peripheral'
        :param row_length: Allows the user to manually define how to break the vision response into a matrix.
        :return: None
        """
        assert view_type in ['D', 'P', 'detailed', 'peripheral']
        if view_type == 'D':
            view_type = 'detailed'
        elif view_type == 'P':
            view_type = 'peripheral'

        if row_length is None:
            # Get number of pixels read by sensor.
            row_length = 16
            if view_type == 'detailed':
                row_length = 31

        # get sensor reading
        if view_type == 'detailed':
            send('sensorRequest,MDN\n', self.client_socket)
        else:
            send('sensorRequest,MPN\n', self.client_socket)
        response = receive(self.client_socket)
        # print(response)
        if len(response) == 0:
            print("The socket is not connected in PAGI World. Reset the socket connection.")
            return
        response = response[0]
        perception = response.split(",")
        # Parse received input into a matrix which represents the visual perception of the agent.
        # Start at one to skip the included MDN.
        self.vision = [perception[i:i+row_length] for i in range(1, len(perception), row_length)]

        # Potential alternative to existing function. Still needs a lot more work.
        # currently_detected_objects = set([item for row in self.vision[:y0] for item in set(row[:x0]) if item])

        # Update the objects in vision and determine if previously detected objects have moved.
        currently_detected_objects = []
        for y, each_row in enumerate(self.vision):
            for x, object_name in enumerate(each_row):
                if object_name and object_name not in currently_detected_objects:  # If we haven't already detected:
                    # TODO: Please find a way to get rid of this.
                    x_location, y_location = self.locate_object(object_name)
                    currently_detected_objects.append(object_name)
                    if object_name not in self.objects:
                        self.objects.append(GameObject(object_name, x_location, y_location, True))
                    else:  # object has been here, check if it has moved
                        for item in self.objects:
                            if item == object_name:
                                if x_location == item.x and y_location == item.y:  # Hasn't moved
                                    item.moving = False
                                else:  # Has moved.
                                    # Could probably determine the velocity of the object with these values.
                                    item.moving = True
                                    item.x = x_location
                                    item.y = y_location
                                break

        # Delete objects that are no longer in field of view.
        for i, previously_detected_object in enumerate(self.objects):
            if previously_detected_object not in currently_detected_objects:
                del self.objects[i]

    def _does_not_contain(self, detected_object, search_list=None):
        if search_list is None:
            search_list = self.objects
        for previously_detected_object in search_list:
            if detected_object == previously_detected_object:
                return False
        return True

    def get_object(self, name):
        """
        Returns full GameObject that has the given name
        :param name: Name of an object to search for.
        :return: GameObject with the given name.
        """
        for item in self.objects:
            if item.name == name:
                return item
        return None

    def _print_objects(self):
        """
        Go through all the objects, print their name, coordinates, and whether they're is_moving.
        :return: None
        """
        print("========Objects========")
        for i, each_object in enumerate(self.objects):
            parameters = {
                "i": i,
                "name": each_object.name,
                "x": each_object.x,
                "y": each_object.y,
                "is_moving": each_object.moving
            }
            print('''Object {i}:
                     \tName: {name}
                     \tCoordinates: ({x},{y})"
                     \tMoving: {moving}'''
                  .format(**parameters))

    def locate_object(self, name, x0=None, y0=None):
        """
        what does this do?...
        :param name:
        :param x0:
        :param y0:
        :return:
        """
        # TODO: Find out what this does and optimize it.
        if x0 is None:
            x0 = len(self.vision[0])
        if y0 is None:
            y0 = len(self.vision)
        number_of_coordinates = 0
        x_sum = 0
        y_sum = 0
        for y, row in enumerate(self.vision[:y0]):
            for x, object_name in enumerate(row[:x0]):
                if object_name == name:
                    x_sum += x
                    y_sum += y
                    number_of_coordinates += 1
        if number_of_coordinates == 0:
            return None
        # Wtffffffffff is this shit
        x_coordinate = x_sum / number_of_coordinates
        y_coordinate = y_sum / number_of_coordinates
        return x_coordinate, y_coordinate


# ==================================================================
# ===============================AGENT==============================
# ==================================================================
class Agent:
    def __init__(self, client_socket):
        self.client_socket = client_socket
        self.left_hand = Hand("L", self.client_socket)
        self.right_hand = Hand("R", self.client_socket)
        self.vision = Vision(self.client_socket)
        self.body = Body(self.client_socket)

    def find_object(self, name, search_mode="P"):
        """
        Search for an object with the given name.
        :param name: The name of the object you are searching for.
        :param search_mode: describes the options for the search, which are either P for peripheral visual sensors
            only, D for detailed visual sensors only, and PD for both.
        :return: A string of the form findObj,objName[,s1][,s2]... where:

            • objName - the name of the object being searched for (see below)
            • si - the visual sensor at which the object was found.

            Although this is not a complete list of all the possible objName values (since it
            will be updated frequently), let this serve as a partial guide:
                • Ramps: rightRamp, leftRamp, floatingRightRamp, floatingLeftRamp
                • Wall and block pieces: wallBlock, horizontalWall, verticalWall,
                    floatingWallBlock, floatingHorizontalWall, floatingVerticalWall,
                    iceBlock, lavaBlock, blueWall, greenWall, redWall
                • Dynamite: redDynamite, greenDynamite, blueDynamite
                • Rewards/Punishments: apple, bacon, redPill, bluePill, poison, steak
                • Other: soldier, medkit
        """
        send("findObj,{name},{mode}\n".format(name=name, mode=search_mode), self.client_socket)
        return receive(self.client_socket, split_on_comma=True)

    def send_force(self, x, y):
        send('addForce,BMvec,{x},{y}\n'.format(x=x, y=y), self.client_socket, return_response=True)

    def jump(self):
        send('addForce,J,30000\n', self.client_socket, return_response=True)

    def reset_rotation(self):
        """
        Resets rotation to 0 degrees.
        This can also be accomplished by passing 0 to `rotate` as its rotation_value parameter
        with absolute_angle set to True.
        :return: None
        """
        self.rotate(0, absolute_angle=True)

    def get_rotation(self, degrees=True):
        """
        Returns the rotation of the agent,relative to world-space.
        :param degrees: Determines if the rotation will be returned in degrees or radians.
        :return: A degree or radian value that represents the current rotation of the agent.
        """
        send('sensorRequest,A\n', self.client_socket)
        response = receive(self.client_socket, split_on_comma=True, return_first_response=True)
        rotation = float(response[1])
        return (rotation*180/math.pi) % 360 if degrees else rotation % (2*math.pi)

    def rotate(self, rotation_value, degrees=True, absolute_angle=False):
        """
        Rotates the agent to the given angle either relative to its current angle or relative to the world-space.
              0
        90  Agent  270
             180
        :param rotation_value: How far you want the agent to turn.
        :param degrees: Whether the input is a degree or radian value.
        :param absolute_angle: Determines whether angle is measured relative to the agent or relative to the world.
        :return: None
        """
        if not degrees:
            # Convert to degrees since that is what PAGI World uses to represent rotation by default.
            rotation_value *= 180/math.pi
        if absolute_angle:
            # Convert global direction to relative direction
            rotation_value -= self.get_rotation()
        # Ensure that the rotation value is between 0 and 359.
        rotation_value %= 360
        send('addForce,BR,{deg}\n'.format(deg=rotation_value), self.client_socket, return_response=True)
        send('addForce,LHH,0.01\n', self.client_socket, return_response=True)
        send('addForce,RHH,0.01\n', self.client_socket, return_response=True)

    def move_hand(self, paces):
        """
        Moves the agent the specified number of paces where one pace equals the width of the body of the agent.
        If the number of paces is negative, the hand will move to the left.
        :param paces: How far to move to move the hand. If negative, move to the left.
        :return: None
        """
        force = paces and (1, -1)[paces < 0] * 10800
        for i in range(abs(paces)):
            send("addForce,BMH,{force}\n".format(force=force), self.client_socket, return_response=True)
            time.sleep(1.1)

    def grab_object(self, name, hand=None, tolerance=1.5):
        """
        Moves specified hand to object with given name and grabs. If no hand is specified, uses the
        close one. If chosen hand is already holding something, it is released before is_moving to the
        new object.
        :param name:
        :param hand:
        :param tolerance:
        :return:
        """
        # Gather object data.
        goal_object = self.vision.get_object(name)
        x = goal_object.x
        y = goal_object.y

        # Select which hand to use.
        if hand is None:
            if x < 15:
                hand = "L"
            else:
                hand = "R"
        if hand == "L":
            hand_object = self.left_hand
        elif hand == "R":
            hand_object = self.right_hand
        else:
            print("WARNING: Invalid hand value for Agent.grabObj(). Expected 'L' or 'R'")

        # move to object and grab
        hand_object.release()
        hand_object.move_to(x, y, tolerance)
        time.sleep(3)
        hand_object.grab()

    def bring_hand_close(self, left_or_right):
        """
        UNIMPLEMENTED
        bring specified hand close to body
        """
        # TODO: Implement this function.
        if left_or_right == "R":
            pass
        elif left_or_right == "L":
            pass

    def say(self, text, speaker='P', duration=5, pos_x=10, pos_y=10):
        """
        You can have PAGI guy say things (and have them show up as speech bubbles).
        If you have no speaker, the coordinates are treated as absolute (so that 0,0 makes the
        bubble appear in the center of the screen).
        :param text: The text for the speaker to say. Do not use commas in this text.
        :param speaker: If you want PAGI guy to be the speaker, this is P. If you want
            a custom item you created to be the speaker, this is the name of that item.
            Otherwise, if there is no speaker, use N.
        :param duration: The length (in seconds) that this bubble will be visible.
        :param pos_x: The position of the speech bubble in the x direction, relative to the speaker.
        :param pos_y: The position of the speech bubble in the y direction, relative to the speaker.
        :return: None
        """
        if ',' in text:
            text = text.replace(',', '')
        send("say,{speaker},{text},{duration},{posX},{posY}\n".format(speaker=speaker, text=text, duration=duration,
                                                                      posX=pos_x, posY=pos_y),
             self.client_socket, return_response=True)
