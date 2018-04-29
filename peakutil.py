cb = np.array([f])
temp = max(cb)
for i in range(temp.size):
    if temp[i:i+1:1]<0.0001:
        temp = np.delete(temp, i)
        cb = np.delete(cb, i)
print "cb size =",cb.size
print "temp size =",temp.size
indexes = peakutils.indexes(cb, thres=0.02/temp, min_dist=100)
print indexes
