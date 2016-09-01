from __future__ import print_function
from pagi_api import *
import random
import cv2
import numpy as np
from time import sleep


def nothing(x):
    '''Placeholder function so the trackbar has an empty callback function'''
    pass


# def draw_maze_in_pagi_world(camera_index=0, trans_x=0, trans_y=0, delay=0, maze_scale_ratio=0.2, buffer_size=10000, use_rolling_average=True,
#                             scale_down_ratio=0.75, scale_up_ratio=None):
#     #cs = connect_socket('10.100.5.87', 42209)
#
#     # Create an agent and bind it to the port you just opened.
#     # agent = Agent(cs)
#     #item = Items(cs)
#     cv2.namedWindow('Threshhold')
#
#     current_iter = 0
#
#     if scale_up_ratio is None:
#         scale_up_ratio = 1 / scale_down_ratio
#     # Define constants here.
#     kernel = np.ones((5, 5), np.uint8)
#     # A BGR color value used to denote the color thresholded for the occupancy grid
#     # This is also the color used to draw lines, thus how we get the ^^^^^^^^^^^^^^
#     track_color = (0, 0, 255)
#     if use_rolling_average:
#         first_run = True
#         rolling_average_image = None
#         cv2.namedWindow("Rolling Average")
#         cv2.createTrackbar("Frame Fade", "Rolling Average", 95, 100, nothing)
#         cv2.createTrackbar("Detection Strength", "Rolling Average", 40, 100, nothing)
#     cv2.namedWindow("Occupancy")
#     cv2.createTrackbar("Line Thickness", "Occupancy", 0, 25, nothing)
#     # Declare the interface through which the camera will be accessed
#     camera = cv2.VideoCapture(camera_index)
#
#     while True:
#         # Get a boolean value determining whether a frame was successfuly grabbed
#         # from the camera and then the actual frame itself.
#         able_to_retrieve_frame, img = camera.read()
#         if not able_to_retrieve_frame:
#             print("Camera is not accessible. Is another application using it?")
#             print("Check to make sure other versions of this program aren't running.")
#             break
#         resized = cv2.resize(img, (0, 0), fx=scale_down_ratio, fy=scale_down_ratio)
#         gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
#         blur = cv2.GaussianBlur(gray, (21, 21), 0)
#         ret, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
#         thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=1)
#         thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)
#         cv2.imshow("Threshold", thresh)
#
#
#         # Canny edge detection and Hough Line Transform
#         edges = cv2.Canny(thresh, 50, 150, apertureSize=3)
#         min_line_length = 100  # 85
#         max_line_gap = 85  # 100
#         # Try to find points which look like lines according to our settings.
#         lines = cv2.HoughLinesP(edges, 1, np.pi/180, 100, None, min_line_length, max_line_gap)
#
#         # If we find some lines to draw, draw them and display them.
#         if lines is not None:
#             # This allows us to adjust the thickness of the lines on the fly
#             line_thickness = cv2.getTrackbarPos("Line Thickness", "Occupancy")
#             for x1, y1, x2, y2 in lines[0]:
#                 # Draw the lines based on the gathered points
#                 cv2.line(resized, (x1, y1), (x2, y2), track_color, line_thickness)
#             # Display those happy little lines overlaid on our original image
#             cv2.imshow("Image with Overlay", resized)
#             # Threshold the image looking for those red lines we just drew and display the result
#             occupancy_map = cv2.inRange(resized, track_color, track_color)
#             cv2.imshow("Occupancy", occupancy_map)
#
#             if use_rolling_average:
#                 if not first_run:
#                     alpha = cv2.getTrackbarPos("Frame Fade", "Rolling Average")/100.0
#                     beta = cv2.getTrackbarPos("Detection Strength", "Rolling Average")/100.0
#                     rolling_average_image = cv2.addWeighted(rolling_average_image, alpha, occupancy_map, beta, 0)
#                     occupancy_map = rolling_average_image
#                     cv2.imshow("Rolling Average", rolling_average_image)
#                     result = cv2.add(thresh, rolling_average_image)
#                     cv2.imshow("Rolling Occupancy", result)
#                     coordinates_of_lines = np.where(rolling_average_image > 100)
#                     coordinates_of_pixels_which_make_up_lines = tuple(zip(coordinates_of_lines[0],
#                                                                           coordinates_of_lines[1]))
#                     def create_point_scaler(scale_ratio):
#                         def scale_point(point):
#                             return tuple(map(lambda x: int(round(x * scale_ratio, 0)), point))
#                         return scale_point
#
#                     scale_point = create_point_scaler(maze_scale_ratio)
#
#                     transformed_list_of_points = set(map(scale_point, coordinates_of_pixels_which_make_up_lines))
#                     for x, y in transformed_list_of_points:
#                         #item.create_item('wall' + str(current_iter), '/home/robolab/Desktop/brickWall.jpg',
#                         #                 x + trans_x, y + trans_y)
#                         current_iter = (current_iter + 1) % buffer_size
#                         sleep(delay)
#
#                     # """
#                     # with open("TestStream.txt", 'w') as file_supreme:
#                     #     for each_line in rolling_average_image:
#                     #         for each_char in each_line:
#                     #             if each_char > 100:
#                     #                 file_supreme.write('1')
#                     #             else:
#                     #                 file_supreme.write('0')
#                     #         file_supreme.write('\n')
#                     # #return "JUST CAUSE 3"
#                     # print("Height:", len(rolling_average_image))
#                     # print("Length:", len(rolling_average_image[0]))
#                     # """
#                 else:
#                     rolling_average_image = occupancy_map
#                     first_run = False
#
#     # Clean up, go home
#     camera.release()
#     cv2.destroyAllWindows()


def pagi_test():
    # If you leave it blank it will try to find the IP itself.
    # Otherwise, you can type in an IP manually:
    # cs = connectSocket(ip="128.113.243.43")

    # You can also type a port if you're not using the default 42209:
    # cs = connectSocket(ip="128.113.243.43", port=230)

    # Create an interface to talk to the agent through.
    cs = connect_socket('25.138.248.159', 42209)

    # Create an agent and bind it to the port you just opened.
    agent = Agent(cs)
    item = Items(cs)

    # def read_file(filepath, trans_x, trans_y):
    #     with open(filepath, 'r') as the_file:
    #         for y, line in enumerate(reversed(list(the_file))):
    #             for x, character in enumerate(line):
    #                 if character == '1':
    #                     item.create_item('wall' + str(x) + '_' + str(y), '/home/robolab/Desktop/brickWall.jpg',
    #                                      x + trans_x, y + trans_y)
    #                 if character == '2':
    #                     item.create_item('roomba', '/home/robolab/Desktop/roomba.jpeg', 3 * (x + trans_x),
    #                                      3 * (y + trans_y))
    #
    # read_file('/Users/brandonyoung/Desktop/TestStream.txt', -30, 3)

    try:
        while True:
            # Check any new messages that were sent
            responses = receive(cs)
            for r in responses:
                print("Message received: " + str(r))

            # x = GameObject(agent, apple, 0, 0, 1)

            if random.random() < 0.9:
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
                # item.create_item('wall1', '/home/robolab/Desktop/brickWall.jpg', '13', '11', '50', '1', '0', '0', '0')
                # agent.send_text('hello there')
                # agent.say('hi there')
                agent.send_text('hello')
                break
            else:
                print("not")

        # agent.reset_rotation()
        # item.drop_item('apple', 10, 10)
    finally:
        close_client(cs)


def main():
    # draw_maze_in_pagi_world(0, scale_down_ratio=0.5, maze_scale_ratio=0.1, delay=0.002, buffer_size=5000)
    pagi_test()

if __name__ == "__main__":
    main()