# usage: python3 visual_pedal.py [# of samples] [file_name.csv]
# Run the program by going to the command line. Type "CD Desktop\Python_Cognitive_Tasks\visual_simon_task" and hit enter.
# Here you can type the above command where it says "usage" to run the program.

# The program reads the signal from the foot pedals using the Metawear library
#   See line 112 to see the code reading the foot pedals' status.

from __future__ import print_function
from mbientlab.metawear import MetaWear, libmetawear, parse_value
from mbientlab.metawear.cbindings import *
from time import sleep, time
import cv2
import screeninfo
from threading import Event
import sys, random, csv, os

MAX_DELAY_TIME = 5  # Maximum time in seconds user allowed before it moves on to the next image
LAG_DELAY_TIME = 2  # Time between stimuli
s1 = s2 = True  # Signals for the pedal inputs
k = int(sys.argv[1])  # Number of trials (images) user has to respond to
i = 0  # Counter
MTR = "FE:F7:6E:7D:D0:5F" # change if using a different device

# Filepaths of images used for visual simon test
img_files = ["simon_images\\ll.jpg",
             "simon_images\\lr.jpg",
             "simon_images\\rl.jpg",
             "simon_images\\rr.jpg"]
index_explanations = ["Left Side/ Left Pointing",
                      "Right Side/ Left Pointing",
                      "Left Side/ Right Pointing",
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
    # libmetawear.mbl_mw_gpio_clear_digital_output(device.board, 4)
    # libmetawear.mbl_mw_gpio_clear_digital_output(device.board, 5)


# Runs the visual simon test with a given delay in seconds, array of indices
# of img_files, corresponding to trials and an array of image files/locations (img_files)
def run_simon_task(arrow_array, img_files):
    # Holds user results to be returned
    data = []
    correct_answers = []  # Keeps track of correct answers

    # Determine which screen to display on
    screen_id = 0

    # Get the size of the screen
    screen = screeninfo.get_monitors()[screen_id]

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
        img = cv2.imread(img_files[image_index])
        arrow_array.pop(arrow_index)

        # Adjust the window to make it full screen
        window_name = 'projector'
        cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
        cv2.moveWindow(window_name, screen.x - 1, screen.y - 1)
        cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN,
                              cv2.WINDOW_FULLSCREEN)
        cv2.imshow(window_name, img)

        # Track the time, allowing user only the allotted time
        # to make a response
        now = time()
        while (time() - now) < MAX_DELAY_TIME:
            # Display image and wait for a key to be pressed
            cv2.waitKey(1)
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
        # Record that the user guessed, determine correctness
        else:
            if (image_index < 2 and not s1) or (image_index >= 2 and not s2):
                got_correct_answer = True
            else:
                got_correct_answer = False
            data.append([image_index, index_explanations[image_index], correct_answers[-1], got_correct_answer, reaction_time])
            if image_index < 2:
                print(str(got_correct_answer) + " guess, correct was \"Left\" in " + str(reaction_time) + " seconds.\n")
            else:
                print(str(got_correct_answer) + " guess, correct was \"Right\" in " + str(reaction_time) + " seconds.\n")
        cv2.destroyAllWindows()

        # Debouncing - wait for inputs to reset. To be debugged.
        while not (s1 and s2):
            libmetawear.mbl_mw_datasignal_read(signal1)
            sleep(0.004)
            libmetawear.mbl_mw_datasignal_read(signal2)
            sleep(0.004)

        sleep(LAG_DELAY_TIME)  # lag time between stimuli

    return data


# ~~~~~ Main Program beigins here ~~~~~
if __name__ == '__main__':
    # set up metatracker
    device = MetaWear(MTR)
    device.connect()
    print("\nConnected")

    # Uneccessary since we are disreguarding the shock pads
    # libmetawear.mbl_mw_gpio_set_pull_mode(device.board, 0, 1)  # 0 = pull up
    # libmetawear.mbl_mw_gpio_set_pull_mode(device.board, 1, 1)  # 1 = pull down
    # libmetawear.mbl_mw_gpio_set_pull_mode(device.board, 2, 1)  # 2 = float
    # libmetawear.mbl_mw_gpio_set_pull_mode(device.board, 3, 1)
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
    results = run_simon_task(arrowArray, img_files)

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
