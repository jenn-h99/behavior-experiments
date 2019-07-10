#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 24 15:48:29 2019

@author: sebastienmaille
"""
import time
import RPi.GPIO as GPIO
import numpy as np
import os
import getpass
import matplotlib.pyplot as plt
import h5py


#------------------------------------------------------------------------------
#Define some classes!
#------------------------------------------------------------------------------

class Stim(object):

    def __init__(self,name,pin,io):
        self.name = name
        self.pin = pin
        self.io = io
        self.GPIOsetup()
        self._licks = []
        self._t_licks = []
        self.lickstep = 0
        self.num_samples = 0

    def __str__(self):
        return'The {} {} associated to pin {}'.format(self.io,self.name,self.pin)

    def GPIOsetup (self):
        #Set up the GPIO pins you will be using as inputs or outputs
        GPIO.setup(self.pin, self.io)

    def reward(self, size, rate = 1 ):

        #size            - Size of reward in ml
        #rate            - Rate of flow in ml/sec

        #Calculate the reward_delay (duration of reward delivery) based on the given parameters
        reward_delay = 1/rate * size

        #Turn on the water dispenser
        GPIO.output(self.pin, True)

        #You'll have to account for the time it
        #takes for the water to get to the mouthpiece
        #Control the size of the reward
        time.sleep(reward_delay)

        #Turn off the water dispenser
        GPIO.output(self.pin, False)

    def lick(self, sampling_rate, sampling_duration):
        #records the licks at a given sampling rate
        self._licks = []
        self._t_licks = []

        #calculate the number of samples needed
        self.num_samples = int(sampling_duration * sampling_rate)

        for i in range(self.num_samples):

            if GPIO.input(self.pin):
                #register lick
                self._licks.append(1)
                self._t_licks.append(time.time())

            else:
                #register no lick
                self._licks.append(0)
                self._t_licks.append(time.time())

            #wait for next sample and update step
            time.sleep(1/sampling_rate)

class Tones():

    def __init__(self, frequency, tone_length):


        #Create a string that will be the name of the .wav file
        self.name = str(frequency) + 'Hz'
        self.freq = frequency

        #create a waveform called self.name from frequency and tone_length
        os.system(f'sox -V0 -r 44100 -n -b 8 -c 2 {self.name}.wav synth {tone_length} sin {frequency} vol -10dB')

    def play(self):
        #send the wav file to the sound card
        os.system(f'play -V0 {self.name}.wav')

class Data():

    def __init__(self, n_trials):
        '''
        Creates an instance of the class Data which will store parameters for
        each trial, including lick data and trial type information.

        Parameters
        -------
        n_trials  : int
            Specifies the number of trials to initialize


        Info
        --------
        self.t_experiment : str
            Stores the datetime where the behavior session starts

        self.t_start : np.ndarray
            Stores time of start for each trial

        self.tone : str
            Stores whether tone corresponded to 'l' or 'r'
        self.t_tone : np.ndarray
            Stores time of tone onset

        self.lick_r : dict
            A list of dictionaries where .lick_r[trial]['t'] stores the times
            of each measurement, and .lick_r[trial]['volt'] stores the voltage
            value of the measurement.
        self.v_rew_r : np.ndarray
            Stores reward volume
        self.t_rew_r : np.ndarray
            Stores time of reward onset

        '''

        self.t_experiment = time.strftime("%Y.%b.%d__%H:%M:%S",
                                     time.localtime(time.time()))
        self.date_experiment = time.strftime("%Y.%b.%d",
                                     time.localtime(time.time()))
        self.t_start = np.empty(n_trials) #start times of each trial
        self.t_end = np.empty(n_trials)

        self._t_start_abs = np.empty(n_trials) #Internal var. storing abs.
                            #start time in seconds for direct comparison with
                            #time.time()

        self.tone = np.empty(n_trials, dtype = str) #L or R
        self.t_tone = np.empty(n_trials)

        self.lick_r = np.empty(n_trials, dtype = dict) #stores licks from R lickport
        self.lick_l = np.empty_like(self.lick_r) #stores licks from L lickport


        self.v_rew_l = np.empty(n_trials) #stores reward volumes from L lickport
        self.t_rew_l = np.empty(n_trials) #stores reward times from L lickport
        self.v_rew_r = np.empty(n_trials) #stores reward volumes from L lickport
        self.t_rew_r = np.empty(n_trials) #stores reward times from L lickport


    def store(self, filename = None):
        if filename is None:
            filename = str(mouse_number) + str(self.date_experiment) + '.hdf5'

        with h5py.File(filename, 'w') as f:
            #Set attributes of the file
            f.attrs['animal'] = mouse_number
            f.attrs['time_experiment'] = self.t_experiment
            f.attrs['user'] = getpass.getuser()

            dt = h5py.special_dtype(vlen = np.dtype('int32')) #Predefine variable-length
                                                            #dtype for storing t, volt

            t_start = f.create_dataset('t_start', data = self.t_start)
            t_end = f.create_dataset('t_end', data = self.t_end)

            #Create data groups for licks, tones and rewards.
            lick_l = f.create_group('lick_l')
            lick_r = f.create_group('lick_r')

            tone = f.create_group('tone')

            rew_l = f.create_group('rew_l')
            rew_r = f.create_group('rew_r')

            #Preinitialize datasets for each sub-datatype within licks, tones
            #and rewards
            lick_l_t = lick_l.create_dataset('t', (n_trials,), dtype = dt)
            lick_l_volt = lick_l.create_dataset('volt', (n_trials,), dtype = dt)
            lick_r_t = lick_r.create_dataset('t', (n_trials,), dtype = dt)
            lick_r_volt = lick_r.create_dataset('volt', (n_trials,), dtype = dt)

            tone_t = tone.create_dataset('t', data = self.t_tone, dtype = 'f16')
            tone_type = tone.create_dataset('type', data = self.tone)

            rew_l_t = rew_l.create_dataset('t', data = self.t_rew_l)
            rew_l_v = rew_l.create_dataset('vol', data = self.v_rew_l)
            rew_r_t = rew_r.create_dataset('t', data = self.t_rew_r)
            rew_r_v = rew_r.create_dataset('vol', data = self.v_rew_r)

            for trial in range(n_trials):
                lick_l_t[trial] = self.lick_l[trial]['t']
                lick_l_volt[trial] = self.lick_l[trial]['volt']
                lick_r_t[trial] = self.lick_r[trial]['t']
                lick_r_volt[trial] = self.lick_r[trial]['volt']

            #Finally, store metadata for each dataset/groups
            lick_l.attrs['title'] = 'Lick signal acquired from the left \
                lickport; contains times (s) and voltages (arb. units)'
            lick_r.attrs['title'] = 'Lick signal acquired from the right \
                lickport; contains times (s) and voltages (arb. units)'
            tone.attrs['title'] = 'Information about the delivered tones each \
                trial; contains times (s) and tone-type (a string denoting \
                whether the tone was large, small or nonexistent)'
            rew_l.attrs['title'] = 'Reward delivered to the left lickport; \
                contains time of reward (s) and its volume (uL)'
            rew_r.attrs['title'] = 'Reward delivered to the right lickport; \
                contains time of reward (s) and its volume (uL)'
            t_start.attrs['title'] = 'When the trial begins (s)'
            t_end.attrs['title'] = 'When the trial ends (s)'

    def plot(self, trial):
        '''
        parameters
        --------
        trial : int
            The trial to plot

        '''
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        ax.plot(self.lick_r[trial]['t'], self.lick_r[trial]['volt'], 'r')
        ax.plot(self.lick_l[trial]['t'], self.lick_l[trial]['volt'], 'g')

        ax.plot([self.t_tone, self.t_tone], [0, 5], 'k', linewidth = 2)

        ax.plot([self.t_rew_l, self.t_rew_l], [0, 5], 'b', linewidth = 2)
        ax.plot([self.t_rew_r, self.t_rew_r], [0, 5], 'b', linewidth = 2)

        plt.savefig('data_plt.pdf')

class Stepper():
    
    def __init__(self, enablePIN, directionPIN, stepPIN, emptyPIN):
        self.enablePIN = enablePIN
        self.directionPIN = directionPIN
        self.stepPIN = stepPIN
        self.emptyPIN = emptyPIN
 
    def stepper(self):
        
        GPIO.setup(self.enablePIN, GPIO.OUT, initial=0)
        GPIO.setup(self.directionPIN, GPIO.OUT, initial=0)
        GPIO.setup(self.stepPIN, GPIO.OUT, initial=0)
        GPIO.setup(self.emptyPIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
     
        if GPIO.input(self.emptyPIN):
            GPIO.output(self.enablePIN, 1)
            GPIO.output(self.directionPIN, 1)
            for i in range(1600):
                GPIO.output(self.stepPIN, 1)
                time.sleep(0.07)
                GPIO.output(self.stepPIN, 0)
                time.sleep(0.07)
        else:
            print('the syringe is empty')
    
    def reward()