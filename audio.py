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

class AudioFile:
    global chunk
    chunk = 1024
    def __init__(self, file):
        """ Init audio stream """ 
        self.wf = wave.open(file, 'rb')
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format = self.p.get_format_from_width(self.wf.getsampwidth()),
            channels = self.wf.getnchannels(),
            rate = self.wf.getframerate(),
            output = True
        )
        self.rates, self.datas = wavfile.read(file)

    def play(self):
        """ Play entire file """
        data = self.wf.readframes(chunk)
        while data != '':
            self.stream.write(data)
            data = self.wf.readframes(chunk)
    
        #proses Hamming Window
        A = fft(self.datas, chunk*2) / 25.5
        mag = np.abs(fftshift(A))
        M = 64
        N = len(self.datas)
        hN = N/2     
        hM = M/2
        freq = np.linspace(-hN, hN, len(A))
        response = 20 * np.log10(mag)
        response = np.clip(response, -100, 100)
        
        plt.plot(freq, response)
        plt.title("Frequency response of Hamming window")
        plt.ylabel("Magnitude [dB]")
        plt.xlabel("Normalized frequency [cycles per sample]")
        plt.axis('tight')
        plt.show()
        
        
        #save data to file
        file = open("Text File/signal_data.txt","w")
        for item in self.datas:
            file.write("%s " % item)
        file.close()
        
        #time domain
        plt.title("Wave-Time Domain")
        plt.ylabel("Amplitude")
        plt.xlabel("Time")
        plt.plot(self.datas)
        plt.show()
        
        #proses FFT
        p = 20*np.log10(np.abs(np.fft.rfft(self.datas[:])))/5
        f = np.linspace(0, self.rates, len(p))/2
        #save FFT to file
        file = open("Text File/fft_frequencies.txt","w")
        i=0
        for item in f:
            file.write("%s) " % str(i+1))
            file.write("%s\t:" % item)
            file.write(" %s\n" % p[i])
            i+=1
        file.close()
        #frequency domain
        
        pl.plot(f, p)
        plt.title("Wave-Frequency Domain (FFT)")
        pl.xlabel("Frequency(Hz)")
        pl.ylabel("Power(dB)")
        pl.show()
        
        #proses STFT scipy
        INT16_FAC = (2**15)-1
        INT32_FAC = (2**31)-1
        INT64_FAC = (2**63)-1
        norm_fact = {'int16':INT16_FAC, 'int32':INT32_FAC, 'int64':INT64_FAC,'float32':1.0,'float64':1.0}
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
        #file = open("Text File/STFT Frequencies.txt","w")
        #i = 0
        #j = 0
        #for itemI in mX:
         #   i+=1
          #  for itemJ in mX[]
        
        
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
        treshold = (minimum - maximum)*(1-t)
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
a = AudioFile("piano.wav")
a.play()
a.close()
