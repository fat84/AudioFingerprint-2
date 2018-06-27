# -*- coding: utf-8 -*-
"""
Created on Sat May 26 00:57:15 2018

@author: Grenceng
"""

import os, sys
import cPickle
import numpy as np
from scipy.io.wavfile import read
import warnings
warnings.filterwarnings("ignore")
import time
from scipy.signal import get_window
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)),'Library/'))
import stft
import peakdetect

#path to training data
source   = "pendahuluan_set/"   
modelpath = "pendahuluan_models/"
test_file = "pendahuluan_set_test.txt"        
file_paths = open(test_file,'r')

gmm_files = [os.path.join(modelpath,fname) for fname in os.listdir(modelpath) if fname.endswith('.gmm')]

#Load the Gaussian gender Models
models    = [cPickle.load(open(fname,'r')) for fname in gmm_files]
speakers   = [fname.split("/")[-1].split(".gmm")[0] for fname in gmm_files]

# Read the test directory and get the list of test audio files 
for path in file_paths:   
    
    path = path.strip()   
    print path
    rates,audio = read(source + path)
    
    INT16_FAC = (2**15)-1
    INT32_FAC = (2**31)-1
    INT64_FAC = (2**63)-1
    norm_fact = {'int16':INT16_FAC, 'int32':INT32_FAC, 'int64':INT64_FAC,'float32':1.0,'float64':1.0}
    audio = np.float32(audio)/norm_fact[audio.dtype.name]
    w = get_window('hamming',501)
    H = 501/2
    mX, pX = stft.stftAnal(audio, rates, w, 2048, H)
    temp = []
    for i in range(mX.shape[0]):
        temp.append(min(mX[i]))
    minimum = min(temp)
    temp = []
    for i in range(mX.shape[0]):
        temp.append(max(mX[i]))
    maximum = max(temp)
    t = 0.5
    sebaran = np.arange(int(round(minimum)),int(round(maximum)))
    s_index = int(sebaran.size*(1-t))
    treshold = sebaran[s_index]
    print "treshold =",treshold
    ploc = peakdetect.peakDetection(mX,treshold)
    peak_loc = []
    for i in range(len(ploc)-1):
        if ploc[i] != ploc[i+1]:
            peak_loc.append(ploc[i])
    peak_loc.append(ploc[-1])
    peak_loc = np.array(peak_loc)
    
    vector   = mX[peak_loc]
    
    log_likelihood = np.zeros(len(models)) 
    
    for i in range(len(models)):
        gmm    = models[i]  #checking with each model one by one
        scores = np.array(gmm.score(vector))
        log_likelihood[i] = scores.sum()
    
    winner = np.argmax(log_likelihood)
    print "score =",log_likelihood
    print "highest score =",max(log_likelihood)
    print "\tdetected as - ", speakers[winner]
    time.sleep(1.0)