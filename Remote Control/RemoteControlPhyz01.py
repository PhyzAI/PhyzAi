# PhyzAI remote control using a PS4 controller
# with an on-screen display of position
#
# Initial Rev, RKD 2024-07

# Libraries to install
# - pip install pygame
# - pip install opencv-python
# - pip install numpy   # for the display
# - put zmaestro.py in same directory as this file

# Also install the Maestro driver and control
# - https://www.pololu.com/file/0J266/maestro-windows-130422.zip
# - run Maestro Control Center
# - in Serial Settings, choose "USB Dual Port"
# - and choose "Never Sleep"


# Info Links
# Search for Playstation 4 Controller here:
# https://www.pygame.org/docs/ref/joystick.html 
#
# Servo controller "Maestro Mini"
# https://www.pololu.com/product/1350/resources
# https://github.com/frc4564/maestro


import pygame
import zmaestro as maestro
import cv2 
import numpy as np


# Image Definitions

enable_GUI = True

image_size_x = 800
image_size_y = 600



# Servo Definitions

head_x_channel = 1   # Determine what these actually are on Phyz's Maestro board with Maestro Control Center
head_y_channel = 0
head_tilt_channel = 2
arm_left_channel = 3 
arm_right_channel = 4

head_x_range = (1520*4, 1620*4, 1728*4)  # Get these from real PhyzAI Maestro board
head_y_range = (735*4, 936*4, 1136*4)
head_tilt_range = (1344*4, 1450*4, 1552*4) 
arm_left_range = (1008*4, 1008*4, 3008*4)  #FIXME: Need to get these.
arm_right_range = (1008*4, 1008*4, 3008*4)



# PS4 Buttons
ps4_button = {
    0: 'Cross',
    1: 'Circle',
    2: 'Square',
    3: 'Triangle',
    4: 'Share',
    5: 'PS Button',
    6: 'Options',
    7: 'L. Stick In',
    8: 'R. Stick In',
    9: 'Left Bumper', 
    10: 'Right Bumper',
    11: 'D-pad Up',
    12: 'D-pad Down',
    13: 'D-pad Left',
    14: 'D-pad Right',
    15: 'Touch Pad Click',
}





def draw_pos(pos_x,pos_y, angle=0, left_arm=0, right_arm=0): 
    """ Draw an image of the current head and arm positions """

    image = np.zeros((image_size_y,image_size_x,3), dtype=np.uint8)

    # Getting the height and width of the image 
    height = image.shape[0] 
    width = image.shape[1] 
    
    # Drawing the lines 
    cv2.line(image, (0, 0), (width, height), (0, 0, 255), 5) 
    cv2.line(image, (width, 0), (0, height), (0, 0, 255), 5) 

    # Ellipse for the head
    axesLength = (50, 100) 
    startAngle = 0
    endAngle = 360
    color = (255, 0, 0) 
    thickness = 5
    cv2.ellipse(image, (pos_x, pos_y), axesLength, 
           angle, startAngle, endAngle, color, thickness)
    
    # Ellipse of left arm
    axesLength = (10, int(50-40*left_arm)) 
    startAngle = 0
    endAngle = 360
    color = (255, 0, 0) 
    thickness = 5
    cv2.ellipse(image, (pos_x-70, pos_y+40-int(40*left_arm)), axesLength, 
           0, startAngle, endAngle, color, thickness)
    
    # Ellipse of right arm
    axesLength = (10, int(50-40*right_arm)) 
    startAngle = 0
    endAngle = 360
    color = (255, 0, 0) 
    thickness = 5
    cv2.ellipse(image, (pos_x+70, pos_y+40-int(40*right_arm)), axesLength, 
           0, startAngle, endAngle, color, thickness)
        
    # Show the image 
    cv2.imshow('image', image) 
  


############
### MAIN ###
############

pygame.init()

# FIXME: Choose correct com-port and device
#servo = maestro.Controller('COM5', device=1)  # Phyz; Check COM port in Windows Device Manager
servo = maestro.Controller('COM3', device=2)  # Keith @ home; Check COM port in Windows Device Manager

j = pygame.joystick.Joystick(0)   # Assume we only have 1
j.init()

clock = pygame.time.Clock()

# Set head and arms (in image) to middle
pos_x = image_size_x//2
pos_y = image_size_y//2
head_angle = 0
left_arm = 0
right_arm = 0

# Set head servos to nominal
servo.setTarget(head_x_channel, head_x_range[1])
servo.setTarget(head_y_channel, head_y_range[1])
servo.setTarget(head_tilt_channel, head_tilt_range[1])
servo.setTarget(arm_left_channel, arm_left_range[1])
servo.setTarget(arm_right_channel, arm_right_range[1])


try:
    while True:
        clock.tick(70)

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.JOYBUTTONDOWN:
                #print("Button Pressed: ", )
                print(event.dict, event.joy, ps4_button[event.button], 'pressed')
                #time.sleep(0.5)
            elif event.type == pygame.JOYBUTTONUP:
                print(event.dict, event.joy, ps4_button[event.button], 'released')
                #time.sleep(0.5)

                if event.button == 9:
                    # go back to center
                    pos_x = image_size_x//2
                    pos_y = image_size_y//2
                    servo.setTarget(head_x_channel, head_x_range[1])
                    servo.setTarget(head_y_channel, head_y_range[1])

                elif event.button == 10:
                    head_angle = 0
                    servo.setTarget(head_tilt_channel, head_tilt_range[1])
                    servo.setTarget(head_tilt_channel, head_tilt_range[1])
                    servo.setTarget(arm_left_channel, arm_left_range[1])
                    servo.setTarget(arm_right_channel, arm_right_range[1])
        
        left_stick_x_axis = j.get_axis(0)
        left_stick_y_axis = j.get_axis(1)
        right_stick_x_axis = j.get_axis(2)
        right_stick_y_axis = j.get_axis(3)
        arm_left_axis = (j.get_axis(4) + 1) / 2   # change (-1,1) to (0,1)
        arm_right_axis = (j.get_axis(5) + 1) / 2 

        #print(f"{left_stick_x_axis:.2f},{left_stick_y_axis:.2f},"
        #      f"{right_stick_x_axis:.2f},{right_stick_y_axis:.2f},"
        #      f"{arm_left_axis:.2f},{arm_right_axis:.2f},")
        

        x_step = 20
        y_step = 10
        
        deadzone = 0.1
        curr_x = servo.getPosition(head_x_channel)
        curr_y = servo.getPosition(head_y_channel)
        curr_tilt = servo.getPosition(head_tilt_channel)
            
        if (abs(left_stick_x_axis) > deadzone) and left_stick_x_axis < 0:
            pos_x -= 5
            servo.setTarget(head_x_channel, curr_x - x_step)

        elif (abs(left_stick_x_axis) > deadzone) and left_stick_x_axis > 0:
            pos_x += 5
            servo.setTarget(head_x_channel, curr_x + x_step)
        
        if (abs(left_stick_y_axis) > deadzone) and left_stick_y_axis < 0:
            pos_y -= 2
            servo.setTarget(head_y_channel, curr_y - y_step)
        elif (abs(left_stick_y_axis) > deadzone) and left_stick_y_axis > 0:
            pos_y += 2
            servo.setTarget(head_y_channel, curr_y + y_step)

        if (abs(right_stick_x_axis) > deadzone) and right_stick_x_axis < 0:
            head_angle -= 1
            servo.setTarget(head_tilt_channel, curr_tilt - 5)
        elif (abs(right_stick_x_axis) > deadzone) and right_stick_x_axis > 0:
            head_angle += 1
            servo.setTarget(head_tilt_channel, curr_tilt + 5)


        curr_left_pos = int(arm_left_axis * (arm_left_range[2] - arm_left_range[0]) + arm_left_range[0])
        servo.setTarget(arm_left_channel, curr_left_pos)
        curr_right_pos = int(arm_right_axis * (arm_right_range[2] - arm_right_range[0]) + arm_right_range[0])
        servo.setTarget(arm_right_channel, curr_right_pos)

        print("arms: ", curr_left_pos, curr_right_pos)


        if enable_GUI:
            draw_pos(pos_x, pos_y, head_angle, arm_left_axis, arm_right_axis)
        
        
except KeyboardInterrupt:
    print("EXITING NOW")
    j.quit()