cb = np.array([p])
temp = max(cb)
for i in range(temp.size):
    if temp[i:i+1:1]<0.0001:
        temp = np.delete(temp, i)
        cb = np.delete(cb, i)
print "cb size =",cb.size
print "temp size =",temp.size
indexes = peakutils.indexes(cb, thres=0.02/temp, min_dist=100)
file = open("Text File/peak_frequencies_2.txt","w")
i = 0
for item in indexes:
    i+=1
    file.write("%s " % i)
    file.write("%s " % indexes)