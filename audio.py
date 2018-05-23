import pyaudio
import wave
import numpy as np
import matplotlib.pyplot as plt
import scipy.io.wavfile as wavfile
import pylab as pl
from scipy import signal
from numpy.fft import fft, fftshift
import os, sys, math, copy
from scipy.signal import get_window
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)),'Library/'))
import stft

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
        
        '''
        #hamming window 2
        fftbuffer = np.zeros(N)
        mX1 = np.zeros(N)
        fftbuffer[hN-hM:hN+hM] = np.hamming(M)
        X = fft(fftbuffer)
        #f, t, X = signal.stft(fftbuffer, self.rates, nperseg=1000)
        mX = 20*np.log10(abs(X))
        mX1[:hN] = mX[hN:]
        mX1[N-hN:] = mX[:hN]
        plt.plot(np.arange(-hN, hN), mX1-max(mX), 'r', lw=1.5)
        plt.axis([-hN,hN,-60,0])
        plt.tight_layout()
        plt.show()
        '''
        
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
        file = open("Text File/peaklocation.txt","w")
        i = 0
        for item in self.peakDetection(p, 7):
            i+=1
            file.write("%s) " % str(i))
            file.write("%s\t" % item)
            file.write("%s\n" % p[item])
        file.close()
        
        #proses STFT scipy
        INT16_FAC = (2**15)-1
        INT32_FAC = (2**31)-1
        INT64_FAC = (2**63)-1
        norm_fact = {'int16':INT16_FAC, 'int32':INT32_FAC, 'int64':INT64_FAC,'float32':1.0,'float64':1.0}
        H = chunk/2 #bisa di set manual'
        x = self.datas
        x = np.float32(x)/norm_fact[x.dtype.name]
        fs = self.rates
        w = get_window('hamming',chunk)#'''bisa di set'''
        mX, pX = stft.stftAnal(x, fs, w, chunk, H)
        y = stft.stftSynth(mX, pX, M, H)
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
        binFreq = fs*np.arange(chunk*maxplotfreq/fs)/chunk
        plt.pcolormesh(frmTime, binFreq, np.transpose(mX[:,:int(chunk*maxplotfreq/fs+1)]))
        plt.xlabel('time (sec)')
        plt.ylabel('frequency (Hz)')
        plt.title('magnitude spectrogram')
        plt.autoscale(tight=True)
        print binFreq
        
        plt.subplot(4,1,3)
        numFrames = int(pX[:,0].size)
        frmTime = H*np.arange(numFrames)/float(fs)                             
        binFreq = fs*np.arange(chunk*maxplotfreq/fs)/chunk                       
        plt.pcolormesh(frmTime, binFreq, np.transpose(np.diff(pX[:,:int(chunk*maxplotfreq/fs+1)],axis=1)))
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
        
        pl.plot(mX[50,:])
        pl.show()
        
        pl.plot(pX[50,:])
        pl.show()
        
        
        
        #print mX.shape
        #proses finding peak
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

    def peakDetection(self, mX, t):
    	thresh = np.where(mX[1:-1]>t, mX[1:-1], 0);             # locations above threshold
    	next_minor = np.where(mX[1:-1]>mX[2:], mX[1:-1], 0)     # locations higher than the next one
    	prev_minor = np.where(mX[1:-1]>mX[:-2], mX[1:-1], 0)    # locations higher than the previous one
    	ploc = thresh * next_minor * prev_minor                 # locations fulfilling the three criteria
    	ploc = ploc.nonzero()[0] + 1                            # add 1 to compensate for previous steps
    	return ploc
    
# Usage example for pyaudio
a = AudioFile("NewData/")
a.play()
a.close()
