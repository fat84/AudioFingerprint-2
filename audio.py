import pyaudio
import wave
import sys
import struct
import numpy as np
import matplotlib.pyplot as plt
import scipy.io.wavfile as wavfile
import pylab as pl
from scipy import signal
from numpy.fft import fft, fftshift
import peakutils


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
        f = np.linspace(0, self.rates, len(p))
        
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

        #proses finding peak
        execfile("find_peak_cwt.py")

        '''
        #proses Hamming Window
        A = fft(self.datas, chunk*2) / 25.5
        mag = np.abs(fftshift(A))
        freq = np.linspace(-0.5, 0.5, len(A))
        response = 20 * np.log10(mag)
        response = np.clip(response, -100, 100)
        
        
        plt.plot(freq, response)
        plt.title("Frequency response of Hamming window")
        plt.ylabel("Magnitude [dB]")
        plt.xlabel("Normalized frequency [cycles per sample]")

        plt.axis('tight')
        plt.show()
        
        
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
a = AudioFile("NewData/dog_bark4.wav")
a.play()
a.close()
