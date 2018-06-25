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
import pandas as pd

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
w_sizes = [256,512,1024,2048, 4096]
ov_sizes = [0.5]
tresholds = np.arange(5,9)*0.1
paths = []
for path in file_paths:
    path = path.strip()
    paths.append(path)
    
for ind_w in range(len(w_sizes)):
    for ind_ov in range(len(ov_sizes)):
        for ind_t in range(len(tresholds)):
            print "treshold rate =",tresholds[ind_t]
            x = []                                         #list penampung data
            for ind_p in range(len(paths)):
                paths[ind_p] = paths[ind_p].strip()   
                print paths[ind_p]
                rates,audio = read(source + paths[ind_p])
                
                #Framing
                framerate = rates                      #menentukan jumlah frame
                frame = round(len(audio)/framerate)         #mengukur banyak data/frame
                n_frames = 1                                   #jumlah frame yang diperiksa
                time_jump = 1                              #lompatan waktu (detik)
                a = 0                                       #index penunjuk frame
                while a < len(audio):                    
                    f_data = audio[int(a):int(a+n_frames*framerate)]
                    f_time = np.arange(a,(a + framerate * n_frames))/float(framerate)
                    a += time_jump*rates
                    
                    start = time.time()
                    
                    INT16_FAC = (2**15)-1
                    INT32_FAC = (2**31)-1
                    INT64_FAC = (2**63)-1
                    norm_fact = {'int16':INT16_FAC, 'int32':INT32_FAC, 'int64':INT64_FAC,'float32':1.0,'float64':1.0}
                    f_data = np.float32(f_data)/norm_fact[f_data.dtype.name]
                    w = get_window('hamming',w_sizes[ind_w])
                    H = int(w_sizes[ind_w]*ov_sizes[ind_ov])
                    mX, pX = stft.stftAnal(f_data, rates, w, 2048, H)
                    minimum = np.min(mX)
                    maximum = np.max(mX)
                    t = tresholds[ind_t]
                    treshold = (minimum + maximum)*(1-t)
                    #print "treshold =",treshold
                    ploc = peakdetect.peakDetection(mX,treshold)
                    #print a,ploc.size
                    if ploc.size != 0:
                        peak_loc = []
                        for i in range(len(ploc)-1):
                            if ploc[i] != ploc[i+1]:
                                peak_loc.append(ploc[i])
                        peak_loc.append(ploc[-1])
                        peak_loc = np.array(peak_loc)
                        #print peak_loc.size,"\n"
                        vector   = mX[peak_loc]
                        
                        log_likelihood = np.zeros(len(models)) 
                        
                        for i in range(len(models)):
                            gmm    = models[i]  #checking with each model one by one
                            scores = np.array(gmm.score(vector))
                            log_likelihood[i] = scores.sum()
                        
                        winner = np.argmax(log_likelihood)
                        end = time.time()
                        elapsed=end-start
                        print(elapsed)
                        #print "score =",log_likelihood
                        #print "highest score =",np.max(log_likelihood)
                        #print "\tdetected as - ", speakers[winner]
                        #time.sleep(1.0)
                        x.append(paths[ind_p])
                        temp = str(np.min(f_time))
                        '''
                        k = temp.split('.')
                        l = k[0]+','+k[1]
                        '''
                        x.append(temp)
                        temp = str(np.max(f_time))
                        '''
                        k = temp.split('.')
                        l = k[0]+','+k[1]
                        '''
                        x.append(temp)
                        temp = str(np.max(log_likelihood))
                        k = temp.split('.')
                        l = k[0]+','+k[1]
                        x.append(l)
                        
                        temp= str(elapsed)
                        x.append(temp)
                        
                        x.append(speakers[winner])
            #time.sleep(2.0)
            print "len x:",len(x)
            x = np.array(x)
            x = np.reshape(x,(len(x)/6,6))
            print x,"\n\n"
            time.sleep(2)
            df = pd.DataFrame(x)
            df.to_excel("test/Test_"+str(w_sizes[ind_w])+
                        "_"+str(ov_sizes[ind_ov])+"_"+str(tresholds[ind_t])+
                        ".xls", index=False)
            
            