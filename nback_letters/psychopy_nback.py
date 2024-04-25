# -*- coding: utf-8 -*-
"""
N-back paradigm with 1-back and 2-back conditions, implemented with PsychoPy.
Can extend to multiple runs or more conditions by creating more text files
and appending to the letters/conditions lists.

@author: Sebastian C. Coleman, ppysc6@nottingham.ac.uk
"""

import numpy as np
from psychopy import visual, core, event
import os.path as op
import random

# set path
path = r"C:\Users\ppysc6\OneDrive - The University of Nottingham\Documents\python\psychopy_nback"

# which conditions to include
conditions = ["1back", "2back"]

# load letters for each condition (same process can be applied for runs with 
# different letter text files, e.g. "1back_run1_letters.txt")
letters = []
for condition in conditions:
    letters.append(np.genfromtxt(op.join(path, condition + '_letters.txt'), dtype='str'))
    
n_stims = np.shape(letters[0])[1]  # letters per block
t_stims = 1     # time elapsed per letter (s)
t_pause = 1     # pause between letters (s)
t_rest = 20     # total rest time per block (s)
n_blocks = np.shape(letters[0])[0]     # number of blocks per condition
t_instruction = 2   # instruction screen time (s)
t_block = (n_stims*(t_stims+t_pause))+t_rest+t_instruction
n_trials = 5   # total of each condition

# trigger settings
using_port= False
if using_port:
    from psychopy import parallel
    port = parallel.ParallelPort(address=int('FFF8',16))    #open serial port to start routine
trig_len = 10/600     # s

# trigger values
block_start = [1, 3] # for two conditions!!!!
rest_start = 2
trig_target = 4
trig_nontarget = 16
resp = 32

# find targets in letters
targets = []
for c, condition in enumerate(conditions):
    target_arr = np.zeros(np.shape(letters[c])) == 1  # all false to start
    
    if condition=="1back":
        for trial in np.arange(n_blocks):
            for letter in np.arange(n_stims)[1:]:   # start from index 1
                target_arr[trial,letter] = letters[c][trial,letter] == letters[c][trial,letter-1]
                
    if condition=="2back":
        for trial in np.arange(n_blocks):
            for letter in np.arange(n_stims)[2:]:   # start from index 1
                target_arr[trial,letter] = letters[c][trial,letter] == letters[c][trial,letter-2]
                
    targets.append(target_arr)

# make a random condition sequence (should probably hard code this)
condition_order = np.concatenate([[c] * n_trials for c in conditions])
random.shuffle(condition_order)

#%% create objects

#create a window
window = visual.Window(fullscr=False,monitor="testMonitor", units="norm")
window.color = "gray" 
    
# create intro screen
intro_screen = visual.TextStim(win=window,text="keep still!",color='red'
                      ,height=0.3,alignText='center',anchorHoriz='center',
                      anchorVert='center')

# draw intro screen while everything else loads
intro_screen.draw()
window.flip()

# create instruction screens
instr_screens = []
for condition in conditions:
    iscreen = visual.TextStim(win=window,text=condition,color='red'
                          ,height=0.4,alignText='center',anchorHoriz='center',
                          anchorVert='center')
    instr_screens.append(iscreen)
    
#create letter objects
letter_objects = []
for c, condition in enumerate(conditions):
    l = []
    for trial in np.arange(n_blocks):
        for letter in np.arange(n_stims):
            letter_object = visual.TextStim(win=window,text=letters[c][trial, letter],color='black'
                                  ,height=0.4,alignText='center',anchorHoriz='center',
                                  anchorVert='center')
            l.append(letter_object)
    letter_objects.append(np.reshape(l, np.shape(letters[c])))

# create fixation
fixation = visual.GratingStim(win=window, units="norm", size=[0.05,0.08], 
                          pos=[0,0], sf=0, color="red")


#%% run task

# Function definitions for task
global check
check = 0
def quit_exp(): # click escape key to end experiment early
    global check
    check = True
     
def send_trigger(data):
    if using_port:
        port.setData(data)
        core.wait(trig_len)
        port.setData(0)
    else:
        print("sending trigger: " + str(data))       
      
def btn_press():
    if using_port:
        port.setData(resp)
        core.wait(trig_len)
        port.setData(0)
    else:
        print("sending trigger: " + str(resp))
      
def block(cond_index):  # This is where the task is actually run
    # instruction screen
    clock = core.Clock()
    send_trigger(block_start[cond_index])
    while clock.getTime() < t_instruction:  # Clock times are in seconds
        if check:
            break
        instr_screens[cond_index].draw()
        window.flip()
    window.flip() 
    # task period
    t=t_instruction
    for stim in np.arange(n_stims):
        if check:
            break
        if targets[cond_index][blocknum[cond_index], stim]:
            send_trigger(trig_target) 
        else:
            send_trigger(trig_nontarget)
           
        while clock.getTime() < t+t_stims:
            if check:
                break
            letter_objects[cond_index][blocknum[cond_index], stim].draw()
            window.flip()
        while clock.getTime() < t+t_stims+t_pause:
            if check:
                break
            window.flip()
        t+=(t_stims+t_pause)
    # rest period        
    send_trigger(rest_start)
    while clock.getTime() < t_block:
        if check:
            break
        fixation.draw()
        window.flip()

# set active keys     
event.globalKeys.clear()     
event.globalKeys.add(key='escape', func=quit_exp)
event.globalKeys.add(key='b', func=btn_press)

# show intro screen and wait for space bar
window.flip()
intro_screen.draw()
window.flip()
event.Mouse(visible=False)
event.waitKeys(keyList="<space>")
core.wait(2)

# loop through all trials
blocknum=[0 for condition in conditions]
for condition in condition_order:
    cond_bool = [cond==condition for cond in conditions]
    cond_i = int(np.arange(len(conditions))[cond_bool])
    block(cond_i)
    blocknum[cond_i] += 1

# wait for space key to finish
intro_screen.draw()
window.flip()
event.waitKeys(keyList="<space>")
window.close()
core.quit()