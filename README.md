# visual_simon_task
Implements a visual simon task. Adapted from: https://github.com/NTorname/simon_tester/blob/master/reac_deb.py, NERVE Centre, UML.
Requires Python 2.7

There are 4 different simon task programs that can be run:
  1) User recieves visual stimuli, responds on the keyboard. (visual_finger.py)
  2) User recieves visual stimuli, responds with the foot pedals. (visual_pedal.py)
  3) User recieves stimuli from SOP, responds on the keyboard. (motor_finger.py)
  4) User recieves stimuli from SOP, responds with the foot pedals. (motor_pedal.py)

To perform any of these tests, start the K5 Omnia Laptop, then open up the command prompt.

Then type "set mtr=FE:F7:6E:7D:D0:5F"

Then type "CD Desktop" followed by "CD visual_simon_task"

Lastly type the python command corresponding to the test you would like to perform. 
Most of them follow the form "python <test_name>.py %mtr% <#of trials> <subject number>_SimonTask.csv"
  
Only "visual_finger.py" has a different form: "python visual_finger.py"
  
For each test, the user will recieve a countdown to begin. At this point, it is a good idea to follow from step 5 of the following instructions: https://docs.google.com/document/d/16ZwuxSvv3aDUHkBFbj8lzuDkrzWp-0yJBJbz7StB9LM/edit
