# usage: python motor_finger.py [mac address] [# of samples] [file_name.csv]

from __future__ import print_function
from mbientlab.metawear import MetaWear, libmetawear, parse_value
from mbientlab.metawear.cbindings import *
from time import time, sleep
from threading import Event
import sys, random, csv, os
import msvcrt

DELAY = 1		# Delay time between each stimulus
MAX_DELAY_TIME = 5      # Maximum allowable delay time in seconds
s1 = s2 = True
k = int(sys.argv[2])
i = 0
data = []
motorArray = []
A_KEY = 97  # ASCII "a" is 97
L_KEY = 108  # ASCII "l" is 108

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


def reaction_time(j):
    libmetawear.mbl_mw_gpio_set_digital_output(device.board, j)
    key = ""
    start = time()
    while time() - start < MAX_DELAY_TIME:
        reac_time = time() - start
        if msvcrt.kbhit():
            key = msvcrt.getch()
            break
    # Determine the correct answer
    if j % 2 == 1:
        correct_answer = "LEFT"
    else:
        correct_answer = "RIGHT"

    # Determine if the answer was correct, append to data accordingly
    if (time() - start) >= MAX_DELAY_TIME:
        correct = False
        print("Failed to respond in the alloted time.\n")
        data.append([j, correct, -1])
    else:
        if (key == 'l' and (j % 2 == 1)) or (key == 'a' and (j % 2 == 0)):
            correct = True
        else:
            correct = False
        print("%r reaction to motor %d was %f seconds" % (correct, j, reac_time))
        data.append([j, correct_answer, correct, reac_time])

    libmetawear.mbl_mw_gpio_clear_digital_output(device.board, j)


# set up metatracker
device = MetaWear(sys.argv[1])
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

    reaction_time(motorArray[j])

    motorArray.pop(j)  # delete this option from the array
    # sleep based on predetermined "lag" time
    sleep(DELAY)

# write results to file
with open(sys.argv[3], 'w') as reac_file:
    writer = csv.writer(reac_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(['motor', 'correct answer', 'was correct', 'reaction time (s)'])
    for a in data:
        writer.writerow([a[0], a[1], a[2]])
#os.system("chmod 666 {}".format(sys.argv[3]))  # metawear python only runs with sudo

# shut down
device.disconnect()
print("\ndisconnected")
