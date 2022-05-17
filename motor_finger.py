# Instructions: open the command prompt using the windows search bar
# Run the program by going to the command line. Type "CD Desktop\Python_Cognitive_Tasks\visual_simon_task" and hit enter.
# Here you can type the command where it says "usage" to run the program.
# usage: python3 motor_finger.py [# of samples] [file_name.csv]

# This test recieves user input from the keyboard:
#   To respond "Left" if a motor vibration was felt on the left
#   side of either leg hit the "A" key.
#   To repond right accordingly, hit the "R" key.
#   See line 68 to see the code for the program recieving user input
# The program tells a motor to vibrate using the Metawear library
#   See line 52 to see the code for sending a vibration to the motor

from __future__ import print_function
from mbientlab.metawear import MetaWear, libmetawear, parse_value
from mbientlab.metawear.cbindings import *
from time import time, sleep
from threading import Event
import sys, random, csv, os
import msvcrt

MAX_DELAY_TIME = 5      # Maximum allowable delay time in seconds
LAG_DELAY_TIME = 2      # lag delay time
s1 = s2 = True
k = int(sys.argv[1])
i = 0
data = []
motorArray = []
A_KEY = 97  # ASCII "a" is 97
L_KEY = 108  # ASCII "l" is 108
MTR = "FE:F7:6E:7D:D0:5F" # change if using a different device

# clunky way of pseudo-random selection of desired outputs
for y in range(k):
    motorArray.append(i)
    i += 1
    if i == 4:
        i = 0


def clear_outputs():
    libmetawear.mbl_mw_gpio_clear_digital_output(device.board, 0)
    libmetawear.mbl_mw_gpio_clear_digital_output(device.board, 1)
    libmetawear.mbl_mw_gpio_clear_digital_output(device.board, 2)
    libmetawear.mbl_mw_gpio_clear_digital_output(device.board, 3)

# libmetawear.mbl_mw_gpio_clear_digital_output(device.board, 4)
# libmetawear.mbl_mw_gpio_clear_digital_output(device.board, 5)


def reaction_time(j, combination, correct_answer):
    # This is the function that sends the vibration signal to the motors
    libmetawear.mbl_mw_gpio_set_digital_output(device.board, j)
    key = ""
    start = time()
    while time() - start < MAX_DELAY_TIME:
        reac_time = time() - start
        if msvcrt.kbhit():
            key = msvcrt.getch()
            end_time = time()
            break
    
    # Determine if the answer was correct, append to data accordingly
    if (end_time - start) >= MAX_DELAY_TIME:
        correct = False
        print("Failed to respond in the alloted time.\n")
        data.append([j, combination, correct_answer, correct, -1])
    else:
        if (key.decode() == "l" and (j % 2 == 1)) or (key.decode() == "a" and (j % 2 == 0)):
            correct = True
        else:
            correct = False
        print("%r reaction to motor %d was %f seconds" % (correct, j, reac_time))
        data.append([j, combination, correct_answer, correct, reac_time])

    libmetawear.mbl_mw_gpio_clear_digital_output(device.board, j)


# set up metatracker
device = MetaWear(MTR)
device.connect()
print("\nConnected")

libmetawear.mbl_mw_gpio_set_pull_mode(device.board, 0, 1)  # 0 = pull up
libmetawear.mbl_mw_gpio_set_pull_mode(device.board, 1, 1)  # 1 = pull down
libmetawear.mbl_mw_gpio_set_pull_mode(device.board, 2, 1)  # 2 = float
libmetawear.mbl_mw_gpio_set_pull_mode(device.board, 3, 1)
#libmetawear.mbl_mw_gpio_set_pull_mode(device.board, 4, 0)
#libmetawear.mbl_mw_gpio_set_pull_mode(device.board, 5, 0)

clear_outputs()  # cleans ungraceful shutdown
print("configured pins")

# give user a countdown
print("Starting in:")
for num in [3, 2, 1]:
    print(str(num) + "...")
    sleep(1.0)
print("GO!!\n")

# start reaction testing
while len(motorArray):
    # global motorArray
    j = random.randrange(0, len(motorArray))  # select random motor

    # Determine the combination
    if motorArray[j] == 0:
        combination = "Left Leg/Left Motor"
    elif motorArray[j] == 1:
        combination = "Left Leg/Right Motor"
    elif motorArray[j] == 2:
        combination = "Right Leg/Left Motor"
    else:
        combination = "Right Leg/Right Motor"

    # Determine what the correct answer was based on the combination
    if motorArray[j] % 2 == 1:
        correct_answer = "LEFT"
    else:
        correct_answer = "RIGHT"

    reaction_time(motorArray[j], combination, correct_answer)

    motorArray.pop(j)  # delete this option from the array
    # sleep based on predetermined "lag" time
    sleep(LAG_DELAY_TIME)

# write results to file
with open(sys.argv[2], 'w') as reac_file:
    writer = csv.writer(reac_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(['motor', 'combination', 'correct answer', 'was correct', 'reaction time (s)'])
    for a in data:
        writer.writerow([a[0], a[1], a[2], a[3], a[4]])
#os.system("chmod 666 {}".format(sys.argv[3]))  # metawear python only runs with sudo

# shut down
device.disconnect()
print("\ndisconnected")
