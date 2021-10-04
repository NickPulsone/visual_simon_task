# usage: sudo python3 reac_deb.py [mac address] [# of samples] [file_name.csv]

from __future__ import print_function
from mbientlab.metawear import MetaWear, libmetawear, parse_value
from mbientlab.metawear.cbindings import *
from time import sleep, time
from threading import Event
import sys, random, csv, os

DELAY = 5	# delay time between stimuli
s1 = s2 = True
k = int(sys.argv[2])
i = 0
data = []
motorArray = []

# clunky way of pseudo-random selection of desired outputs
for y in range(k):
    motorArray.append(i)
    i += 1
    if i == 4:
        i = 0


# callback when gpio input state found
# this may be the most convoluted way to read a GPIO in the history of
# computing and I'm not sure whose fault it is
def data_handler1(context, data):
    global s1
    s1 = bool(parse_value(data))


libmetawear.callback1 = FnVoid_VoidP_DataP(data_handler1)


def data_handler2(context, data):
    global s2
    s2 = bool(parse_value(data))


libmetawear.callback2 = FnVoid_VoidP_DataP(data_handler2)


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

    while (s1 and s2):  # wait for input
        libmetawear.mbl_mw_datasignal_read(signal1)
        sleep(0.004)
        libmetawear.mbl_mw_datasignal_read(signal2)
        sleep(0.004)  # bad but polling too quick causes stability issues

    if j % 2:  # determine if input was correct
        correct = not (s2)
    else:
        correct = not (s1)

    reaction_time = time() - start
    libmetawear.mbl_mw_gpio_clear_digital_output(device.board, j)

    while (not (s1 and s2)):  # debouncing
        libmetawear.mbl_mw_datasignal_read(signal1)
        sleep(0.004)
        libmetawear.mbl_mw_datasignal_read(signal2)
        sleep(0.004)

    print("%r reaction to motor %d was %f seconds" % (correct, j, reaction_time))
    data.append([j, correct, reaction_time])


# set up metatracker
device = MetaWear(sys.argv[1])
device.connect()
print("\nConnected")

libmetawear.mbl_mw_gpio_set_pull_mode(device.board, 0, 1)  # 0 = pull up
libmetawear.mbl_mw_gpio_set_pull_mode(device.board, 1, 1)  # 1 = pull down
libmetawear.mbl_mw_gpio_set_pull_mode(device.board, 2, 1)  # 2 = float
libmetawear.mbl_mw_gpio_set_pull_mode(device.board, 3, 1)
libmetawear.mbl_mw_gpio_set_pull_mode(device.board, 4, 0)
libmetawear.mbl_mw_gpio_set_pull_mode(device.board, 5, 0)

clear_outputs()  # cleans ungraceful shutdown
print("configured pins")

# subscribe to gpio inputs
signal1 = libmetawear.mbl_mw_gpio_get_digital_input_data_signal(device.board, 4)
libmetawear.mbl_mw_datasignal_subscribe(signal1, None, libmetawear.callback1)

signal2 = libmetawear.mbl_mw_gpio_get_digital_input_data_signal(device.board, 5)
libmetawear.mbl_mw_datasignal_subscribe(signal2, None, libmetawear.callback2)
print("subscribed listener\n")

# give user a countdown
print("Starting in:")
for num in [3, 2, 1]:
    print(str(num) + "...")
    sleep(1.0)
print("GO!!\n")

# starting reaction testing
while len(motorArray):
    # global motorArray
    # sleep(random.randrange(1, 10))  # random delay vibration
    j = random.randrange(0, len(motorArray))  # select random motor

    reaction_time(motorArray[j])

    motorArray.pop(j)  # delete this option from the array
    sleep(DELAY) # give delay time between stimuli

# write results to file
with open(sys.argv[3], 'w') as reac_file:
    writer = csv.writer(reac_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(['motor', 'correct button', 'reaction time (s)'])
    for a in data:
        writer.writerow([a[0], a[1], a[2]])
# os.system("chmod 666 {}".format(sys.argv[3]))  # metawear python only runs with sudo

# shut down
libmetawear.mbl_mw_datasignal_unsubscribe(signal1)
libmetawear.mbl_mw_datasignal_unsubscribe(signal2)
print("\nunsubscribed")
device.disconnect()
print("disconnected")
