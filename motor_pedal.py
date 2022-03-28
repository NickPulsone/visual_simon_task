# usage: python3 visual_pedal.py [# of samples] [file_name.csv]
# Run the program by going to the command line. Type "CD Desktop\Python_Cognitive_Tasks\visual_simon_task" and hit enter.
# Here you can type the above command where it says "usage" to run the program.

# The program tells a motor to vibrate using the Metawear library
#   See line 94 to see the code for sending a vibration to the motor
# The program reads the signal from the foot pedals using the Metawear library
#   See line 101 to see the code reading the foot pedals' status.

from __future__ import print_function
from mbientlab.metawear import MetaWear, libmetawear, parse_value
from mbientlab.metawear.cbindings import *
from time import sleep, time
from threading import Event
import sys, random, csv, os

MAX_DELAY_TIME = 6.0  # Maximum time in seconds user allowed before it moves on to the next image

LAG_DELAY_TIME = 3.0  # Time between stimuli. NOTE: Actual delay in the test will be DOUBLE this value

s1 = s2 = True  # Signals for the pedal inputs
k = int(sys.argv[1])  # Number of trials (images) user has to respond to
i = 0  # Counter
MTR = "FE:F7:6E:7D:D0:5F" # change if using a different device

# Array that shows index correspondance with particular stimuli 
index_explanations = ["Left Side/ Left Pointing",
                      "Left Side/ Right Pointing",
                      "Right Side/ Left Pointing",
                      "Right Side/ Right Pointing"]

# Create array that holds indices that reference a particular file
arrowArray = []
stimuliIndices = [0, 1, 2, 3]
for _ in range(int(k / 4)):
    arrowArray = arrowArray + stimuliIndices
for i in range(k % 4):
    arrowArray.append(i)


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


# clear outputs of gpio
def clear_outputs():
    libmetawear.mbl_mw_gpio_clear_digital_output(device.board, 0)
    libmetawear.mbl_mw_gpio_clear_digital_output(device.board, 1)
    libmetawear.mbl_mw_gpio_clear_digital_output(device.board, 2)
    libmetawear.mbl_mw_gpio_clear_digital_output(device.board, 3)
    #libmetawear.mbl_mw_gpio_clear_digital_output(device.board, 4)
    #libmetawear.mbl_mw_gpio_clear_digital_output(device.board, 5)


# Runs the visual simon test with a given delay in seconds given an array of indices
def run_simon_task(arrow_array):
    # Holds user results to be returned
    data = []
    correct_answers = []  # Keeps track of correct answers

    # Main loop of simon testing
    for i in range(len(arrowArray)):
        # Randomly select the image to open
        arrow_index = random.randrange(0, len(arrowArray))
        image_index = arrow_array[arrow_index]
        # Keep track of correct answer based on RNG
        if image_index <= 1:
            correct_answers.append("LEFT")
        else:
            correct_answers.append("RIGHT")
        arrow_array.pop(arrow_index)

        # Send motor vibration and track the time, allowing
        # the user only the allotted time to make a response
        libmetawear.mbl_mw_gpio_set_digital_output(device.board, image_index)
        now = time()
        
        # Read pedal signals until user responds to stimulu
        while (time() - now) < MAX_DELAY_TIME:
            # Wait for pedal to be pressed
            if not s1 or not s2:  # wait for input
                reaction_time = time() - now
                break
            # Read pedals, detect user input
            libmetawear.mbl_mw_datasignal_read(signal1)
            sleep(0.004)
            libmetawear.mbl_mw_datasignal_read(signal2)
            sleep(0.004)

        # Record that the user took too long if that was the case
        if (time() - now) >= MAX_DELAY_TIME:
            data.append([image_index, index_explanations[image_index], correct_answers[-1], False, -1.0])
            print("False response due to delayed input.\n")
            libmetawear.mbl_mw_gpio_clear_digital_output(device.board, image_index)
            sleep(LAG_DELAY_TIME)
            continue
        
        # Record that the user guessed, determine correctness
        else:
            if (not (image_index % 2) and not s1) or ((image_index % 2) and not s2):
                got_correct_answer = True
            else:
                got_correct_answer = False
            data.append([image_index, index_explanations[image_index], correct_answers[-1], got_correct_answer, reaction_time])
            if not (image_index % 2):
                print(str(got_correct_answer) + " guess, correct was \"Left\" in " + str(reaction_time) + " seconds.\n")
            else:
                print(str(got_correct_answer) + " guess, correct was \"Right\" in " + str(reaction_time) + " seconds.\n")
        
        # Debouncing - wait for inputs to reset.
        while not (s1 and s2):
            libmetawear.mbl_mw_datasignal_read(signal1)
            sleep(0.004)
            libmetawear.mbl_mw_datasignal_read(signal2)
            sleep(0.004)
        
        # Clear outputs and pause
        libmetawear.mbl_mw_gpio_clear_digital_output(device.board, image_index)
        sleep(LAG_DELAY_TIME)
    return data


# ~~~~~ Main Program beigins here ~~~~~
if __name__ == '__main__':
    # set up metatracker
    device = MetaWear(MTR)
    device.connect()
    print("\nConnected")

    # Initialize pedals and motors
    libmetawear.mbl_mw_gpio_set_pull_mode(device.board, 0, 1)  # 0 = pull up
    libmetawear.mbl_mw_gpio_set_pull_mode(device.board, 1, 1)  # 1 = pull down
    libmetawear.mbl_mw_gpio_set_pull_mode(device.board, 2, 1)  # 2 = float
    libmetawear.mbl_mw_gpio_set_pull_mode(device.board, 3, 1)
    libmetawear.mbl_mw_gpio_set_pull_mode(device.board, 4, 0)
    libmetawear.mbl_mw_gpio_set_pull_mode(device.board, 5, 0)

    clear_outputs()  # cleans ungraceful shutdown
    print("configured pins")

    # subscribe to inputs
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
    results = run_simon_task(arrowArray)

    # write results to file
    with open(sys.argv[2], 'w') as reac_file:
        writer = csv.writer(reac_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['Index', 'Index Explanations', 'Correct Answer', 'Is Correct', 'Time(s)'])
        for a in results:
            writer.writerow([a[0], a[1], a[2], a[3], a[4]])
    # os.system("chmod 666 {}".format(sys.argv[3]))  # metawear python only runs with sudo

    # shut down
    libmetawear.mbl_mw_datasignal_unsubscribe(signal1)
    libmetawear.mbl_mw_datasignal_unsubscribe(signal2)
    print("\nunsubscribed")
    device.disconnect()
    print("disconnected")
