import pyaudio
import wave
import numpy as np
import matplotlib.pyplot as plt
import scipy.io.wavfile as wavfile
import pylab as pl
from numpy.fft import fft, fftshift
import os, sys
from scipy.signal import get_window
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)),'Library/'))
import stft
import peakdetect

INT16_FAC = (2**15)-1
INT32_FAC = (2**31)-1
INT64_FAC = (2**63)-1
norm_fact = {'int16':INT16_FAC, 'int32':INT32_FAC, 'int64':INT64_FAC,'float32':1.0,'float64':1.0}
class AudioFile:
    global chunk
    chunk = 1024
    def __init__(self, file):
        """ Init audio stream """ 
        self.rates, self.datas = wavfile.read(file)
        '''
        noise = np.random.normal(0,10,self.datas.shape)
        i = 0
        for f in noise:
            self.datas[i] += f
            i += 1
        print self.datas
        wavfile.write("piano_n.wav",self.rates,self.datas)
        '''
        self.wf = wave.open(file, 'rb')
        wavfile.write("noised.wav",self.rates,self.datas)
        self.wf = wave.open("noised.wav", 'rb')
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format = self.p.get_format_from_width(self.wf.getsampwidth()),
            channels = self.wf.getnchannels(),
            rate = self.wf.getframerate(),
            output = True
        )

    def play(self):
        """ Play entire file """
        data = self.wf.readframes(chunk)
        while data != '':
            self.stream.write(data)
            data = self.wf.readframes(chunk)
        
        #save data to file
        file = open("Text File/signal_data.txt","w")
        for item in self.datas:
            file.write("%s " % item)
        file.close()
        '''
        #Framing
        framerate = self.rates
        print framerate                            #menentukan jumlah frame
        frame = round(len(self.datas)/framerate)    #mengukur banyak data/frame
        hop = 10                                     #jumlah frame yang diperiksa
        overlap = 5                                #lompatan frame
        a = 0
        while a < frame:
            f_data = self.datas[a*int(frame):(a+hop)*int(frame)]
            f_time = np.arange(a*(f_data.size/hop),(a+hop)*(f_data.size/hop))/float(self.rates)
            title = "Frame",a/50+1,"Time-domain"
            plt.title(title)
            plt.xlabel("Time")
            plt.ylabel("Amplitude")
            plt.plot(f_time,f_data)
            plt.show()
            a += overlap
            
        '''
        '''
        for i in range(hop):
            f_data = self.datas[i*int(frame):(i+1)*int(frame)]
            f_time = np.arange(i*f_data.size,(i+1)*f_data.size)/float(self.rates)
            plt.title("Frame Time-domain")
            plt.xlabel("Time")
            plt.ylabel("Amplitude")
            plt.plot(f_time,f_data)
            plt.show()
        '''
        
        '''
        f_time_sec = f_time[-1]
        f_data = np.asarray(())
        f_time = np.asarray(())
        for i in range(int(frame)):
            if len(f_data) == 0:
                f_data = self.datas[i*framerate:(i+1)*framerate]
                f_time = i*f_time_sec
            else:
                f_data = np.hstack((f_data,self.datas[i*framerate:(i+1)*framerate]))
                f_time = np.hstack((f_time,i*f_time_sec))
        if len(self.datas) % framerate > 0:
            f_data = np.hstack((f_data,self.datas[(i+1)*framerate:]))
            temp = (i+1)*f_time_sec
            f_time = np.hstack((f_time,temp))
        mod = len(self.datas) % framerate
        antimod = len(self.datas) - mod
        f_data = np.reshape(f_data[:antimod],(-1,framerate))
        sisa_f_data = f_data[antimod:]
        print f_data
        print sisa_f_data
        print f_time
        '''
        
        #proses STFT
        N = 2048
        M = 501     #'''bisa di set'''
        H = M/2     #bisa di set manual'
        
        x = self.datas
        x = np.float32(x)/norm_fact[x.dtype.name]
        fs = self.rates
        w = get_window('hamming',M)
        
        mX, pX = stft.stftAnal(x, fs, w, N, H)
        y = stft.stftSynth(mX, pX, M, H)
        file = open("Text File/mX.txt","w")
        for j in range(len(mX)):
            for item in mX[j]:
                file.write("%s " % item)
            file.write("\n\n")
        file.close()
        
        
        plt.figure(figsize=(12, 9))
        maxplotfreq = 5000.0
        
        plt.subplot(4,1,1)
        plt.plot(np.arange(x.size)/float(fs), x)
        plt.axis([0, x.size/float(fs), min(x), max(x)])
        plt.ylabel('amplitude')
        plt.xlabel('time (sec)')
        plt.title('input sound: x')
        
        plt.subplot(4,1,2)
        numFrames = int(mX[:,0].size)
        frmTime = H*np.arange(numFrames)/float(fs)
        binFreq = fs*np.arange(N*maxplotfreq/fs)/N
        plt.pcolormesh(frmTime, binFreq, np.transpose(mX[:,:int(N*maxplotfreq/fs+1)]))
        plt.xlabel('time (sec)')
        plt.ylabel('frequency (Hz)')
        plt.title('magnitude spectrogram')
        plt.autoscale(tight=True)
        
        file = open("Text File/STFT frequencies.txt","w")
        for item in binFreq:
            file.write("%s\n" % item)
        file.close()
        
        plt.subplot(4,1,3)
        numFrames = int(pX[:,0].size)
        frmTime = H*np.arange(numFrames)/float(fs)
        binFreq = fs*np.arange(N*maxplotfreq/fs)/N
        plt.pcolormesh(frmTime, binFreq, np.transpose(np.diff(pX[:,:int(N*maxplotfreq/fs+1)],axis=1)))
        plt.xlabel('time (sec)')
        plt.ylabel('frequency (Hz)')
        plt.title('phase spectrogram (derivative)')
        plt.autoscale(tight=True)
        
        plt.subplot(4,1,4)
        plt.plot(np.arange(y.size)/float(fs), y)
        plt.axis([0, y.size/float(fs), min(y), max(y)])
        plt.ylabel('amplitude')
        plt.xlabel('time (sec)')
        plt.title('output sound: y')
        
        plt.tight_layout()
        plt.show(block=False)
        
        
        #print mX.shape
        #proses finding peak
        temp = []
        for i in range(mX.shape[0]):
            temp.append(min(mX[i]))
        minimum = min(temp)
        temp = []
        for i in range(mX.shape[0]):
            temp.append(max(mX[i]))
        maximum = max(temp)
        t = 0.8
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
        #print "ploc =",ploc
        #print "peak location =",peak_loc
        
        #print len(peak_loc)
        file = open("Text File/peaks location.txt","w")
        for item in peak_loc:
            file.write("%s\n" % item)
        file.close()
        
        file = open("Text File/peaks magnitude.txt","w")
        for item in peak_loc:
            file.write("%s " % item)
            for i in range(len(mX[item])):
                file.write("%s " % mX[item,i])
            file.write("\n\n")
        file.close()
        
        pmag = mX[peak_loc]
        
        pl.plot(mX[-10,:])
        pl.xlabel('Index')
        pl.ylabel('Value')
        pl.show()
        '''
        plt.plot(pX[-10,:])
        pl.xlabel('Index')
        pl.ylabel('Value')
        pl.show()
        '''
        
        freqaxis = fs*np.arange(N/2)/float(N)
        plt.plot(freqaxis,mX[peak_loc[0],:-1])
        pl.xlabel("Frequency")
        pl.ylabel("Magnitude")
        pl.show()
        
        print "freqaxis shape =",freqaxis.shape
        print "mX peak shape =",mX[peak_loc].shape
        
        file = open("Text File/peak frequencies.txt","w")
        file.write("Frequency\tMagnitude\n")
        for item in peak_loc:
            file.write("%s\t" % freqaxis[item])
            file.write("%s\n" % mX[peak_loc[0],item])
        file.close()
        
        pl.plot(fs * peak_loc/ float(N), pmag)
        pl.xlabel("Frequency")
        pl.ylabel("Magnitude")
        pl.show()
        
        #execfile("find_peak_cwt.py")

        '''
        fval = []
        for i in range(len(f)-1):
            if f[i]!=f[i+1]:
                flag = 0
                if len(fval)!=0:
                    for j in range(len(fval)):
                        if fval[j]!=f[i]:
                            flag = 1
                        else:
                            flag = 0
                            break
                    if flag==1:
                        fval.append(f[i])
                else:
                    fval.append(f[i])
        if len(f)==len(fval)+1:
            print("fft berhasil")
        '''        

    def close(self):
        """ Graceful shutdown """ 
        self.stream.close()
        self.p.terminate()
    
# Usage example for pyaudio
a = AudioFile("NewData/piano.wav")
a.play()
a.close()