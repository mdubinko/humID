import binascii
import sys

def hextet(i):
    '''6-hex-digit padded string. E.g. 0-> "000000" or 255-> "0000FF" '''
    return str.format('{:06X}', i)

# output files
outfiles = []
for n in range(0,16):
    outfiles.append(open("lookup%x.txt" % n, "a"))

count = 0
total = 0
with open(sys.argv[1]) as f:
    for line in f:
        s = line[:-1]
        csum = binascii.crc32(s.encode('utf-8'))
        csum &= 0xffffff
        ofs = ((csum & 0xf00000) >> 20)
        #print("%s %s %x" % (hextet(csum), s, ofs))
        count += 1
        total += 1
        if count >= 1000000:
            print(str(total))
            count = 0
        outfiles[ofs].write("%s %s\n" % (hextet(csum), s))

for file in outfiles:
    file.close()
