
http://home.wlu.edu/~levys/software/kbhit.py

http://support.microsoft.com/kb/99261/ja

ar = [14, 665, 807, 878]
ar = [16,146,670,929,1028]
br = []
for e in range(len(ar)-1):
	br.append(ar[e+1] - ar[e])

br[-1] += ar[0]
for e in br: print "%4d  %3.1f" % (e, e * 100.0/ar[-1])

