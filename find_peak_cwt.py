#proses finding peak
peakind = signal.find_peaks_cwt(p, np.arange(1,10))

#save to peak file
file = open("Text File/peak_frequencies.txt","w")
i=0
for item in f[peakind]:
    file.write("%s) " % str(i+1))
    file.write("%s\t:" % item)
    file.write(" %s\n" % p[i])
    i+=1
file.close()
'''
print "peakind=",peakind #index masing-masing peak
print "p[peakind]=",p[peakind] #power masing-masing index peak
print "f[peakind]",f[peakind] #frekuensi masing-masing index peak
'''
