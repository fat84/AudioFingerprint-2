# -*- coding: utf-8 -*-
"""
Created on Tue May 22 23:27:11 2018

@author: Grenceng
"""
import numpy as np
import math
import dft as DFT

def stftAnal(x, fs, w, N, H):
    M = w.size
    hM1 = int(math.floor((M+1)/2))
    hM2 = int(math.floor(M/2))
    x = np.append(np.zeros(hM2),x)
    x = np.append(x,np.zeros(hM2))
    pin = hM1
    pend = x.size-hM1
    w = w / sum(w)
    y = np.zeros(x.size)
    while pin<=pend:
		x1 = x[pin-hM1:pin+hM2]
		mX, pX = DFT.dftAnal(x1, w, N)
		if pin == hM1:
			xmX = np.array([mX])
			xpX = np.array([pX])
		else:
			xmX = np.vstack((xmX,np.array([mX])))
			xpX = np.vstack((xpX,np.array([pX])))
		pin += H
    return xmX, xpX

def stftSynth(mY, pY, M, H):
    hM1 = int(math.floor((M+1)/2))                   # half analysis window size by rounding
    hM2 = int(math.floor(M/2))                       # half analysis window size by floor
    nFrames = mY[:,0].size                           # number of frames
    y = np.zeros(nFrames*H + hM1 + hM2)              # initialize output array
    pin = hM1                  
    for i in range(nFrames):                         # iterate over all frames      
    	y1 = DFT.dftSynth(mY[i,:], pY[i,:], M)         # compute idft
    	y[pin-hM1:pin+hM2] += H*y1                     # overlap-add to generate output sound
    	pin += H                                       # advance sound pointer
    y = np.delete(y, range(hM2))                     # delete half of first window which was added in stftAnal
    y = np.delete(y, range(y.size-hM1, y.size))      # delete the end of the sound that was added in stftAnal
    return y