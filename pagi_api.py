from __future__ import print_function
import socket
import time
import math
import select


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
    client_socket.connect((ip_address, port))
    client_socket.setblocking(0)
    return client_socket


def close_client(client_socket):
    """
    Closes connection to PAGI World; must be called to interact with pagi_api outside of pagi_api.py
    """
    client_socket.close()


unread = []  # stores all unread messages from socket


def send(message, client_socket, encode_message=True):
    """
    WARNING: seems to randomly ignore responses from the socket, causing an infinite loop
    (possibly) PREVENTS client_socket.recv FROM WORKING OUTSIDE THIS FUNCTION
    calls socket.send(out) and returns corresponding value of socket.recv()
    waits for socket to respond before exiting
    :param message: A string that is to be sent to PAGI world over the network.
    :param client_socket:
    :param encode_message:
    :return: None
    """
    if encode_message:
        message = encode(message)
    client_socket.send(message)


def receive(client_socket, split_on_comma=False, return_first_response=False, max_receive_size=16384):
    readable = select.select([client_socket], [], [], 0.25)  # timeout/1000
    if readable[0]:
        # Read message and add to messages.
        responses = decode(client_socket.recv(max_receive_size)).split('\n')
        responses = [c for c in responses if c != ""]
        if split_on_comma:
            responses = [response.split(',') for response in responses]
        return responses[0] if return_first_response else responses
    return []


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
    UNIMPLEMENTED
    Holds body sensors.
    """

    def __init__(self, client_socket):
        self.sensors = []
        self.client_socket = client_socket

    def get_sensor(self, num=None):
        """
        :param num: The index of the sensor reading to retrieve.
        :return: The specified body sensor reading.
        If num is unspecified, returns a list of all body sensor readings.
        0 is top, increases counterclockwise.
        """
        # TODO: Implement this method.
        pass


class Hand:
    def __init__(self, hand_string, client_socket):
        self.client_socket = client_socket
        self.hand = hand_string.upper()
        if len(self.hand) > 1:
            self.hand = self.hand[0]
        assert self.hand in ["L", "R"]
        self.closed = False
        self.holding_object = False
        self.sensors = []

    def get_coordinates(self, absolute_coordinates=False):
        """
        Get the coordinates of the hand relative to the agent's body.
        :param absolute_coordinates: Unimplemented.
        Considering allowing the coordinates to either be relative to the origin or relative to the agent.
        :return: (X, Y) coordinates of hand relative to body
        """
        print(absolute_coordinates)
        send('sensorRequest,' + self.hand + 'P\n', self.client_socket)
        current_location = receive(self.client_socket, split_on_comma=True, return_first_response=True)
        x = float(current_location[1])
        y = float(current_location[2])
        return x, y

    def send_force(self, x, y):
        send('addForce,{hand}Hvec,{x},{y}\n'.format(hand=self.hand, x=x, y=y), self.client_socket)

    def get_distance(self, x, y):
        """
        Get distance from position (x,y)
        :param x: Location in the x-axis.
        :param y: Location in the y-axis.
        :return: The euclidean distance to the point given.
        """
        x0, y0 = self.get_coordinates()
        return math.sqrt((x0-x)**2+(y0-y)**2)

    def move_hand(self, x, y, tolerance=1.5):
        """
        Move to point (x,y) within a specified tolerance.
        WARNING: If it is impossible to move to (x,y), this will infinite loop.
        :param x: Location in the x-axis.
        :param y: Location in the y-axis.
        :param tolerance: Minimum distance to an object before the hand is considered to be on top of it.
        :return:
        """
        # TODO: Keep track of how long the function has been looping so it doesn't loop forever.
        # TODO: Fix this function! Continues the move the hand to the desired position.

        # Convert (x,y) from Unity item units (whatever they are) to detailed vision units (0.0 - 30.20)
        x = -2.25 + x*0.148
        y = 1.65 + y*0.1475

        hand = self.hand

        # Keep a copy of unread to revert to, since this does not use send().
        # Otherwise, a huge number of useless results would end up in unread.
        global unread
        unread_copy = unread

        # Move hand in x and y directions
        # WARNING: randomly causes problems with send().
        # Might be fixed; it is a bit random.
        # Note that this is likely caused by not receiving the socket data for the reflex functions,
        # clogging up the socket's responses in send()
        send('setReflex, lock{h}X,{h}Px|!|{x},sensorRequest|{h}P;addForce|{h}HH|[350*({x}-{h}Px)]\n'
             .format(h=hand, x=x), self.client_socket)
        send('setReflex, lock{h}Y,{h}Py|!|{y},sensorRequest|{h}P;addForce|{h}HV|[350*({y}-{h}Py)]\n'
             .format(h=hand, y=y), self.client_socket)

        # Wait until sufficiently close, then return
        while self.get_distance(x, y) > tolerance:
            time.sleep(0.5)
        unread = unread_copy

    def grab(self):
        """
        Apply grabbing force and update holding status
        :return: None
        """
        send('addForce,{h}HG,5\n'.format(h=self.hand), self.client_socket)
        send('sensorRequest,{h}2'.format(h=self.hand), self.client_socket)
        response = receive(self.client_socket)[0].split(',')[1]
        self.closed = True
        if response == "1":
            self.holding_object = True

    def release(self):
        """
        Stop applying grabbing force and update holding status
        :return: None
        """
        send('addForce,{h}HR,5\n'.format(h=self.hand), self.client_socket)
        self.closed = False
        self.holding_object = False


class GameObject:
    """
    Contains data of objects encountered on Unity's side.
    May be expanded to contain additional data.
    """

    def __init__(self, object_name, x, y, movement):
        self.name = object_name
        self.x = x
        self.y = y
        self.moving = movement

    def __eq__(self, other):
        return self.name == other


class Items:
    """
    Contains functions responsible for creating items in the world in real-time.
    """
    # TODO: finish implementing create_item function

    def __init__(self, client_socket):
        self.client_socket = client_socket

    def drop_item(self, name, x, y):
        self.name = name
        self.x = x
        self.y = y
        send('dropItem,{name},{x},{y}\n'.format(name=self.name, x=self.x, y=self.y), self.client_socket)

    def create_item(self, file_path, x, y, mass, physics, initial_rotation, endorphins, kinematic_properties):
        self.file_path = file_path
        self.x = x
        self.y = y
        self.mass = mass
        self.physics = physics
        self.init_rotation = initial_rotation
        self.endorphins = endorphins
        self.kinematic_properties = kinematic_properties
        send('createItem,{fp},{x},{y},{m},{phy},{init_rot},{endor},{k_prop}'.format(fp=self.file_path, x=self.x, y=self.y, m=self.mass, phy=self.physics, init_rot=self.init_rotation, endor=self.endorphins, k_prop=self.kinematic_properties))


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

    def update(self, view_type='detailed'):
        """
        :param view_type: Must be 'detailed' or 'peripheral'
        :return: None
        """
        if view_type not in ['detailed', 'peripheral']:
            # set view_type to detailed if invalid (may not properly check for validity...)
            view_type = 'detailed'

        # Get number of pixels read by sensor.
        x0, y0 = 16, 11
        if view_type == 'detailed':
            x0, y0 = 31, 21

        # get sensor reading
        send('sensorRequest,MDN\n', self.client_socket)
        response = receive(self.client_socket)[0]
        perception = response.split(",")
        # Parse received input into a matrix which represents the visual perception of the agent.
        # Start at one to skip the included MDN.
        self.vision = [perception[i:i+x0] for i in range(1, len(perception), y0)]

        # Potential alternative to existing function. Still needs a lot more work.
        # currently_detected_objects = set([item for row in self.vision[:y0] for item in set(row[:x0]) if item])

        # Update the objects in vision and determine if previously detected objects have moved.
        currently_detected_objects = []
        for y in range(y0):
            for x in range(x0):
                object_name = self.get(x, y)
                if object_name and object_name not in currently_detected_objects:  # If we haven't already detected:
                    x_location, y_location = self.locate_object(object_name, x0, y0)
                    currently_detected_objects.append(object_name)
                    if object_name not in self.objects:
                        self.objects.append(GameObject(object_name, x_location, y_location, True))
                    else:  # object has been here, check if it has moved
                        for item in self.objects:
                            if item == object_name:
                                if x_location == item.x and y_location == item.y:  # Hasn't moved
                                    item.moving = False
                                else:  # Has moved.
                                    item.moving = True
                                    item.x = x_location
                                    item.y = y_location
                                break

        # Delete objects that are no longer in field of view.
        for i, previously_detected_object in enumerate(self.objects):
            if previously_detected_object not in currently_detected_objects:
                del self.objects[i]

    def get(self, x, y):
        return self.vision[y][x]

    def does_not_contain(self, detected_object, search_list=None):
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

    def print_objects(self):
        """
        Go through all the objects, print their name, coordinates, and whether they're moving.
        :return: None
        """
        print("========Objects========")
        for i, each_object in enumerate(self.objects):
            parameters = {
                "i": i,
                "name": each_object.name,
                "x": each_object.x,
                "y": each_object.y,
                "moving": each_object.moving
            }
            print('''Object {i}:
                     \tName: {name}
                     \tCoordinates: ({x},{y})"
                     \tMoving: {moving}'''
                  .format(**parameters))

    def locate_object(self, name, x0, y0):
        """
        what does this do?...
        :param name:
        :param x0:
        :param y0:
        :return:
        """
        # TODO: Find out what this does and optimize it.
        number_of_coordinates = 0
        x_sum = 0
        y_sum = 0
        for y in range(y0):
            for x in range(x0):
                if self.get(x, y) == name:
                    x_sum += x
                    y_sum += y
                    number_of_coordinates += 1
        if number_of_coordinates == 0:
            return None
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

    def find_object(self, name):
        """
        Search for an object with the given name.
        :param name:
        :return:
        """
        # TODO: Implement this function.
        send("findObj,{name},P".format(name=name))
        response = receive(self.client_socket)
        print(response)

    def send_force(self, x, y):
        send('addForce,BMvec,{x},{y}\n'.format(x=x, y=y), self.client_socket)

    def jump(self):
        send('addForce,J,30000\n', self.client_socket)

    def reset_rotation(self):
        """
        Resets rotation to 0 degrees.
        This can also be accomplished by passing 0 to `rotate` as its rotation_value parameter
        :return: None
        """
        r = self.get_rotation()
        self.rotate(0)

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

    def rotate(self, rotation_value, degrees=True, absolute_angle=True):
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
        send('addForce,BR,{deg}\n'.format(deg=rotation_value), self.client_socket)
        send('addForce,LHH,0.01\n', self.client_socket)
        send('addForce,RHH,0.01\n', self.client_socket)

    def move_agent(self, paces):
        """
        Moves the agent the specified number of paces where one pace equals the width of the body of the agent.
        If the number of paces is negative, the hand will move to the left.
        :param paces: How far to move to move the hand. If negative, move to the left.
        :return: None
        """
        force = paces and (1, -1)[paces < 0] * 10800
        for i in range(abs(paces)):
            send("addForce,BMH,{force}\n".format(force=force), self.client_socket)
            time.sleep(1.1)

    def grab_object(self, name, hand=None, tolerance=1.5):
        """
        Moves specified hand to object with given name and grabs. If no hand is specified, uses the
        close one. If chosen hand is already holding something, it is released before moving to the
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
        hand_object.move_hand(x, y, tolerance)
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
