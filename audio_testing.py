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

from Tkinter import *
import tkMessageBox as msgbox
import tkFileDialog
import scipy as scp
from PIL import Image, ImageTk
import matplotlib
from matplotlib import pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
matplotlib.use('TkAgg')



class Main:
    def __init__(self, parent, title):
        self.parent = parent
        self.parent.title(title)
        self.parent.config(background="#d7efea")
        self.komponen()
        self.path = ""
        global source, file_paths, models, speakers
        #path to training data
        source   = "development_set/"
        modelpath = "speaker_models/"
        test_file = "development_set_test.txt"    
        file_paths = open(test_file,'r')
        
        gmm_files = [os.path.join(modelpath,fname) for fname in os.listdir(modelpath) if fname.endswith('.gmm')]
        
        #Load the Gaussian gender Models
        models    = [cPickle.load(open(fname,'r')) for fname in gmm_files]
        speakers   = [fname.split("/")[-1].split(".gmm")[0] for fname in gmm_files]
        
    #GUI
    def komponen(self):
        self.opFrame = Frame(self.parent, bg="#4ae056")
        self.opFrame.grid(row=0, column=0,sticky=N)
        self.inputPupuhLbl = Label(self.opFrame, width=15, height=2, fg="black",
                                   text="Input Pupuh")
        self.inputPupuhLbl.grid(row=0, column=0, padx=5, pady=4, sticky=W)
        self.browseBtn = Button(self.opFrame, text="Browse", command=self.browseWav,
                                width=6, height=1, bg="#e5efd7")
        self.browseBtn.grid(row=0, column=1, padx=3, pady=4)
        self.FnameTxt = StringVar()
        self.inputPupuhEnt = Entry(self.opFrame, width=20, bd=2, textvariable=self.FnameTxt)
        self.inputPupuhEnt.grid(row=0, column=2, padx=3, pady=4)
        self.FnameTxt.set("Belum Ada Pupuh")
        self.WSizeTxt = StringVar()
        self.windowSizeEnt = Entry(self.opFrame, width=15, bd=2, textvariable=self.WSizeTxt)
        self.windowSizeEnt.grid(row=1, column=0, padx=5, pady=3, sticky=W)
        self.WSizeTxt.set("Window Size")
        self.OvlSizeTxt = StringVar()
        self.overlapSizeEnt = Entry(self.opFrame, width=15, bd=2, textvariable=self.OvlSizeTxt)
        self.overlapSizeEnt.grid(row=1, column=1, columnspan=2, padx=3, pady=3, sticky=W)
        self.OvlSizeTxt.set("Overlapping Size")
        self.PTreshTxt = StringVar()
        self.peakTresholdEnt = Entry(self.opFrame, width=15, bd=2, textvariable=self.PTreshTxt)
        self.peakTresholdEnt.grid(row=1, column=3, padx=3, pady=3, sticky=W)
        self.PTreshTxt.set("Peak Treshold")
        self.proccessEnt = Button(self.opFrame, width=10, text="Proccess", bg="#e5efd7",
                                  command=self.proses)
        self.proccessEnt.grid(row=2, column=3, padx=3, pady=3, sticky=W)
        
        
        self.plotFrame = Frame(self.parent, bg="#4ae056")
        self.plotFrame.grid(row=1, column=0,sticky=N)
    
    def browseWav(self):
        self.path = tkFileDialog.askopenfilename()
        if len(self.path) > 0:
            filename = self.path.split("/")[-1]
            self.FnameTxt.set(filename)
    
    def proses(self):
        if len(self.path) > 0:
            rates, audio = read(self.path)
            print "proses"
            framerate = rates                      #menentukan jumlah frame
            frame = round(len(audio)/framerate)         #mengukur banyak data/frame
            n_frames = 10                                   #jumlah frame yang diperiksa
            time_jump = 1                              #lompatan waktu (detik)
            a = 0                                       #index penunjuk frame
            c = []                                      #list conclusion
            while a < len(audio):
                f_data = audio[int(a):int(a+n_frames*framerate)]
                f_time = np.arange(a,(a + framerate * n_frames))/float(framerate)
                a += time_jump*rates
                INT16_FAC = (2**15)-1
                INT32_FAC = (2**31)-1
                INT64_FAC = (2**63)-1
                norm_fact = {'int16':INT16_FAC, 'int32':INT32_FAC, 'int64':INT64_FAC,'float32':1.0,'float64':1.0}
                f_data = np.float32(f_data)/norm_fact[f_data.dtype.name]
                w = get_window('hamming',int(self.WSizeTxt.get()))
                H = int(float(self.WSizeTxt.get())*float(self.OvlSizeTxt.get()))
                mX, pX = stft.stftAnal(f_data, rates, w, 2048, H)
                minimum = np.min(mX)
                maximum = np.max(mX)
                t = float(self.PTreshTxt.get())
                treshold = (minimum + maximum)*(1-t)
                print "treshold =",treshold
                ploc = peakdetect.peakDetection(mX,treshold)
                print a,ploc.size
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
                    
                    conclusion = np.argmax(log_likelihood)
                    print conclusion
                    c.append(speakers[conclusion])
            print c
        else:
            print "belum ada pupuh diinput"
        
    def temp(self):
        # Read the test directory and get the list of test audio files 
        w_sizes = [256,512,1024,2048, 4096]
        ov_sizes = [0.25,0.5,0.75]
        tresholds = np.arange(1,10)*0.1
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
                        n_frames = 10                                   #jumlah frame yang diperiksa
                        time_jump = 5                              #lompatan waktu (detik)
                        a = 0                                       #index penunjuk frame
                        while a < len(audio):
                            f_data = audio[int(a):int(a+n_frames*framerate)]
                            f_time = np.arange(a,(a + framerate * n_frames))/float(framerate)
                            a += time_jump*rates
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
                                x.append(speakers[winner])
                    #time.sleep(2.0)
                    print "len x:",len(x)
                    x = np.array(x)
                    x = np.reshape(x,(len(x)/5,5))
                    print x,"\n\n"
                    time.sleep(2)
                    df = pd.DataFrame(x)
                    df.to_excel("test/Test_"+str(w_sizes[ind_w])+
                                "_"+str(ov_sizes[ind_ov])+"_"+str(tresholds[ind_t])+
                                ".xls", index=False)

#==================== MAIN ====================#
root = Tk()
Main(root,".::Audio Fingerprint - Shazam Pupuh::.")
root.mainloop()