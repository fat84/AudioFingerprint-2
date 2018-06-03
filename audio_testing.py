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
import csv

#path to training data
source   = "development_set/"
modelpath = "speaker_models/"
test_file = "development_set_test.txt"        
file_paths = open(test_file,'r')

gmm_files = [os.path.join(modelpath,fname) for fname in os.listdir(modelpath) if fname.endswith('.gmm')]

#Load the Gaussian gender Models
models    = [cPickle.load(open(fname,'r')) for fname in gmm_files]
speakers   = [fname.split("/")[-1].split(".gmm")[0] for fname in gmm_files]

# Read the test directory and get the list of test audio files 
x = []
for path in file_paths:   
    
    path = path.strip()   
    print path
    rates,audio = read(source + path)
    #Framing
    framerate = 100                            #menentukan jumlah frame
    frame = round(len(audio)/framerate)    #mengukur banyak data/frame
    hop = 5                                     #jumlah frame yang diperiksa
    overlap = 10                                #lompatan frame
    a = 0
    while a < framerate:
        f_data = audio[a*int(frame):(a+hop)*int(frame)]
        f_time = np.arange(a*(f_data.size/hop),(a+hop)*(f_data.size/hop))/float(rates)
        a += overlap
    
        INT16_FAC = (2**15)-1
        INT32_FAC = (2**31)-1
        INT64_FAC = (2**63)-1
        norm_fact = {'int16':INT16_FAC, 'int32':INT32_FAC, 'int64':INT64_FAC,'float32':1.0,'float64':1.0}
        f_data = np.float32(f_data)/norm_fact[f_data.dtype.name]
        w = get_window('hamming',501)
        H = 501/2
        mX, pX = stft.stftAnal(f_data, rates, w, 2048, H)
        minimum = np.min(mX)
        maximum = np.max(mX)
        t = 0.5
        treshold = (minimum + maximum)*(1-t)
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
        #print "score =",log_likelihood
        print "highest score =",np.max(log_likelihood)
        print "\tdetected as - ", speakers[winner]
        time.sleep(1.0)
        x.append(path)
        temp = str(np.min(f_time))
        k = temp.split('.')
        l = k[0]+','+k[1]
        x.append(l)
        temp = str(np.max(f_time))
        k = temp.split('.')
        l = k[0]+','+k[1]
        x.append(l)
        temp = str(np.max(log_likelihood))
        k = temp.split('.')
        l = k[0]+','+k[1]
        x.append(l)
        x.append(speakers[winner])
    time.sleep(2.0)
    
x = np.array(x)
x = np.reshape(x,(-1,5))
csvfile = open("csvData.xls","w")
for v in x:
    for z in v:
        csvfile.write('%s' % str(z))
        csvfile.write('\t')
    csvfile.write("\n")
csvfile.close()
