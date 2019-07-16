#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 15 16:57:22 2019

@author: sebastienmaille
"""

import time
import RPi.GPIO as GPIO
import numpy as np
import os
import threading
import core

#------------------------------------------------------------------------------
#Set experimental parameters:
#------------------------------------------------------------------------------

mouse_number = input('mouse number: ' ) #asks user for mouse number

n_trials = 10 #number of trials in this block
delay_length = 1 #length of delay between sample tone and go cue, in sec
response_delay = 1 #length of time for animals to give response

L_tone_freq = 1000 #frequency of sample tone in left lick trials
R_tone_freq = 4000 #frequency of sample tone in right lick trials
go_tone_freq = 500 #frequency of go tone

#reward_size = 0.01 #size of water reward, in mL

#----------------------------
#Assign GPIO pins:
#----------------------------

servo_PWM = 17 #PWM pin for servo that adjusts lickport distance

L_enablePIN = 23 #enable pin for left stepper motor
L_directionPIN = 24 #direction pin for left stepper motor
L_stepPIN = 25 #step pin for left stepper motor
L_emptyPIN = 20 #empty switch pin for left stepper motor
L_lickometer = 12 #input pin for lickometer (black wire)


R_enablePIN = 10 #enable pin for right stepper motor
R_directionPIN = 9 #direction pin for right stepper motor
R_stepPIN = 11 #step pin for right stepper motor
R_emptyPIN = 21 #empty switch pin for right stepper motor
R_lickometer = 16 #input pin for lickometer (black wire)

#----------------------------
#Initialize class instances for experiment:
#----------------------------

#Turn off the GPIO warnings
GPIO.setwarnings(False)

#Set the mode of the pins (broadcom vs local)
GPIO.setmode(GPIO.BCM)

#set the enable pins for L and R stepper motors to 1 to prevent overheating
GPIO.setup(L_enablePIN, GPIO.OUT, initial = 1)
GPIO.setup(R_enablePIN, GPIO.OUT, initial = 1)

#create Stepper class instances for left and right reward delivery
water_L = core.stepper(L_enablePIN, L_directionPIN, L_stepPIN, L_emptyPIN)
water_R = core.stepper(R_enablePIN, R_directionPIN, R_stepPIN, R_emptyPIN)

#create lickometer class instances for left and right lickometers
lick_port_L = core.lickometer(L_lickometer)
lick_port_R = core.lickometer(R_lickometer)

#create tones
tone_L = core.tones(L_tone_freq, 1)
tone_R = core.tones(R_tone_freq, 1)

tone_go = core.tones(go_tone_freq, 0.75)

#----------------------------
#Initialize experiment
#----------------------------

#Set the time for the beginning of the block
trials = np.arange(n_trials)
data = core.data(n_trials, mouse_number)

for trial in trials:
    data._t_start_abs[trial] = time.time()*1000 #Set time at beginning of trial
    data.t_start[trial] = data._t_start_abs[trial] - data._t_start_abs[0]

    #create thread objects for left and right lickports
    thread_L = threading.Thread(target = lick_port_L.Lick, args = (40, 5))
    thread_R = threading.Thread(target = lick_port_R.Lick, args = (40, 5))

    thread_L.start() #Start threads for lick recording
    thread_R.start()

    left_trial_ = np.random.rand() < 0.5 #decide if it will be a L or R trial

    #Left trial:---------------------------------------------------------------
    if left_trial_ is True:
        data.tone[trial] = 'L' #Assign data type
        data.t_tone[trial] = time.time()*1000 - data._t_start_abs[trial]
        tone_L.Play() #Play left tone

        time.sleep(delay_length) #Sleep for some delay

        tone_go.Play() #Play go tone
        
        length_L = len(lick_port_L._licks)
        length_R = len(lick_port_R._licks)
        response = False
        response_start = time.time()*1000
        
        while response == False:
            if sum(lick_port_R._licks[(length_R-1):]) > 0:
                response = 'R'
            
            elif sum(lick_port_L._licks[(length_L-1):]) > 0:
                response = 'L'

            elif time.time()*1000 - response_start > response_delay:
                response = 'N'

        if response == 'L':
            data.t_rew_l[trial] = time.time()*1000 - data._t_start_abs[trial]
            data.v_rew_l[trial] = 5
            water_L.Reward() #Deliver L reward
            data.t_end[trial] = time.time()*1000 - data._t_start_abs[0] #store end time

    #Right trial:--------------------------------------------------------------
    else:
        data.tone[trial] = 'R' #Assign data type
        data.t_tone[trial] = time.time()*1000 - data._t_start_abs[trial]
        tone_R.Play() #Play left tone

        time.sleep(delay_length) #Sleep for delay_length

        tone_go.Play() #Play go tone
        
        length_L = len(lick_port_L._licks)
        length_R = len(lick_port_R._licks)
        response = False
        response_start = time.time()*1000
        
        while response == False:
            if sum(lick_port_L._licks[(length_L-1):]) > 0:
                response = 'L'
            
            elif sum(lick_port_R._licks[(length_R-1):]) > 0:
                response = 'R'

            elif time.time()*1000 - response_start > response_delay:
                response = 'N'
        
        if response == 'R':
            data.t_rew_r[trial] = time.time()*1000 - data._t_start_abs[trial]
            data.v_rew_r[trial] = 5
            water_R.Reward() #Deliver R reward   
            data.t_end[trial] = time.time()*1000 - data._t_start_abs[0] #store end time

    #---------------
    #Post-trial data storage
    #---------------
    
    #Make sure the threads are finished
    thread_L.join()
    thread_R.join()

    #Store and process the data
    data_list = [data.lick_l, data.lick_r]
    lick_list = [lick_port_L, lick_port_R]

    for ind, obj in enumerate(data_list):
        obj[trial] = {}
        obj[trial]['t'] = lick_list[ind]._t_licks
        obj[trial]['volt'] = lick_list[ind]._licks

    #Pause for the ITI before next trial
    ITI_ = 1.5
#    while ITI_ > 10:
#        ITI_ = np.random.exponential(scale = 2)

    time.sleep(ITI_)


data.Store() #store the data

#delete the .wav files created for the experiment
os.system(f'rm {L_tone_freq}Hz.wav')
os.system(f'rm {R_tone_freq}Hz.wav')
os.system(f'rm {go_tone_freq}Hz.wav')

#Clean up the GPIOs
GPIO.cleanup()