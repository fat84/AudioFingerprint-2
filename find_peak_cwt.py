#proses finding peak
peakind = signal.find_peaks_cwt(p, np.arange(1,10))
print "peakind=",peakind #index masing-masing peak
print "p[peakind]=",p[peakind] #power masing-masing index peak
print "f[peakind]",f[peakind] #frekuensi masing-masing index peak
