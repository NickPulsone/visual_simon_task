# usage: python visual_simon_task.py
import cv2
import csv
import screeninfo
from time import time, sleep
import random

OUTFILE_NAME = "results.csv"  # Name of output file (can include desired filepath destination)

DELAY_TIME = 5  # Maximum time user allowed before it moves on to the next image (seconds)
TOTAL_STIMULI = 10  # Number of stimuli for the test
A_KEY = 97  # ASCII "a" is 97
L_KEY = 108  # ASCII "l" is 108

# Filename and included path of each image of the arrows
# For current setup: img_files[0] -> left arrow on left side of screen
#                    img_files[1] -> left arrow on right side of screen
#                    img_files[2] -> right arrow on left side of screen
#                    img_files[3] -> right arrow on right side of screen
img_files = ["simon_images\\ll.jpg",
             "simon_images\\lr.jpg",
             "simon_images\\rl.jpg",
             "simon_images\\rr.jpg"]


# Runs a simon test simulation.
# Pre: delay is the maximum time user is allotted to give a response.
#      numImages is the number of images the user will have to respond to.
#      img_files is a list of strings, each of which contain the filepath/name
#                of a file with the arrow images.
# Post: Displays the results of the user's performace throughout the test.
#       Returns a the results for each test, one list per result (2D list collectively) of the form
#       [ [<int:index of img_files>, <bool:got answer correct>,
#          <double: reaction time in seconds or -1 if user ran out of time>], ...]
def run_simon_task(delay, num_images, img_files, outfile_name):
    # Create array that holds indices that reference a particular file
    # Roughly equal amount of each of the 4 image indices in the array
    arrow_array = []
    file_indices = [0, 1, 2, 3]
    for _ in range(int(num_images / 4)):
        arrow_array = arrow_array + file_indices
    for i in range(num_images % 4):
        arrow_array.append(i)

    # Determine which screen to display on
    screen_id = 0

    # Get the size of the screen
    screen = screeninfo.get_monitors()[screen_id]

    # Main loop of simon testing
    data = []  # Holds user results
    for i in range(TOTAL_STIMULI):
        # Randomly select the image to open
        arrow_index = random.randrange(0, len(arrow_array))
        image_index = arrow_array[arrow_index]
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
        while (time() - now) < DELAY_TIME:
            # Display image and wait for a key to be pressed
            key = cv2.waitKeyEx(1)
            if key == A_KEY or key == L_KEY:
                reaction_time = time() - now
                break
        # Record that the user took too long
        if (time() - now) >= delay:
            data.append([image_index, False, -1.0])
            print("False response due to delayed input.\n")
        else:
            # If the user responded within allotted time, determine if they pressed the correct key
            if (image_index < 2 and key == A_KEY) or (image_index >= 2 and key == L_KEY):
                got_correct_answer = True
            else:
                got_correct_answer = False
            # Record the results
            data.append([image_index, got_correct_answer, reaction_time])
            # Display the results of the individual test on the screen
            if image_index < 2:
                print(f"{got_correct_answer} guess \"Left\" in {reaction_time} seconds.\n")
            else:
                print(f"{got_correct_answer} guess \"Right\" in {reaction_time} seconds.\n")
        cv2.destroyAllWindows()
    # Write results to csv file
    with open(outfile_name, 'w') as reac_file:
        writer = csv.writer(reac_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['Index', 'Correct', 'Time(s)'])
        for a in data:
            writer.writerow([a[0], a[1], a[2]])


if __name__ == '__main__':
    # Outline simon task instructions and launch task after a few seconds
    print("Welcome to the visual simon task.")
    print("Place your left finger on the \"A\" key and your right finger on the \"L\" key.")
    print("\nThe rules are as follow: if you see an arrow pointing left, \npress the \"A\" key, "
          "and if you see and arrow pointing right press the \"L\" key. \nRespond as fast and as accurately as possible\n")
    sleep(2.0)
    print("Starting in:")
    for num in [3, 2, 1]:
        print(f"{num}...")
        sleep(1.0)
    print("GO!!\n")

    # Run simon test and write results to the defined file
    run_simon_task(DELAY_TIME, TOTAL_STIMULI, img_files, OUTFILE_NAME)
