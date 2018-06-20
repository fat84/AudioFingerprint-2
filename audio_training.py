# -*- coding: utf-8 -*-
"""
Created on Sat May 26 00:04:27 2018

@author: Grenceng
"""

import cPickle
import numpy as np
from scipy.io.wavfile import read
from sklearn.mixture import GMM 
import warnings
warnings.filterwarnings("ignore")
import os, sys
from scipy.signal import get_window
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)),'Library/'))
import stft
import peakdetect
    
    
#path to training data
source   = "development_set/"

#path where training speakers will be saved
dest = "speaker_models/"
train_file = "development_set_enroll.txt"
file_paths = open(train_file,'r')

count = 1
# Extracting features for each speaker (5 files per speakers)
features = np.asarray(())
for path in file_paths:
    path = path.strip()
    print path
    
    # read the audio
    rates,audio = read(source + path)
    
    INT16_FAC = (2**15)-1
    INT32_FAC = (2**31)-1
    INT64_FAC = (2**63)-1
    norm_fact = {'int16':INT16_FAC, 'int32':INT32_FAC, 'int64':INT64_FAC,'float32':1.0,'float64':1.0}
    audio = np.float32(audio)/norm_fact[audio.dtype.name]
    w = get_window('hamming',501)
    H = 501/2
    mX, pX = stft.stftAnal(audio, rates, w, 2048, H)
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
    
    vector = mX[peak_loc]
    
    if features.size == 0:
        features = vector
    else:
        features = np.vstack((features, vector))
    # when features of 5 files of speaker are concatenated, then do model training

    if count == 5:  
        gmm = GMM(n_components = 16, n_iter = 200, covariance_type='diag',n_init = 3)
        gmm.fit(features)
        # dumping the trained gaussian model
        picklefile = path.split("-")[0]+".gmm"
        cPickle.dump(gmm,open(dest + picklefile,'w'))
        print '+ modeling completed for data:',picklefile," with data point = ",features.shape
        features = np.asarray(())
        count = 0
    count = count + 1
    