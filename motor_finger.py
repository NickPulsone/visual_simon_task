# usage: sudo python3 reac_deb.py [mac address] [# of samples] [file_name.csv]

from __future__ import print_function
from mbientlab.metawear import MetaWear, libmetawear, parse_value
from mbientlab.metawear.cbindings import *
from time import time, sleep, clock_gettime, CLOCK_MONOTONIC
from threading import Event
import sys, random, csv, os
import keyboard

DELAY_TIME = 5      # Maximum allowable delay time in seconds
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
    start = time()
    while time() - start < DELAY_TIME:
        reac_time = time() - start
        if keyboard.ispressed('a'):
            if j % 2:
                correct = True
            else:
                correct = False
            break
        if keyboard.ispressed('l'):
            if j % 2:
                correct = False
            else:
                correct = True
            break

    stop = clock_gettime(CLOCK_MONOTONIC)
    libmetawear.mbl_mw_gpio_clear_digital_output(device.board, j)

    print("%r reaction to motor %d was %f seconds" % (correct, j, reac_time))
    data.append([j, correct, reac_time])


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

# starting reaction testing
while len(motorArray):
    # global motorArray
    sleep(random.randrange(1, 10))  # random delay vibration
    j = random.randrange(0, len(motorArray))  # select random motor

    reaction_time(motorArray[j])

    motorArray.pop(j)  # delete this option from the array

# write results to file
with open(sys.argv[3], 'w') as reac_file:
    writer = csv.writer(reac_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(['motor', 'correct button', 'reaction time (s)'])
    for a in data:
        writer.writerow([a[0], a[1], a[2]])
os.system("chmod 666 {}".format(sys.argv[3]))  # metawear python only runs with sudo

# shut down
device.disconnect()
print("disconnected")