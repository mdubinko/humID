from random import choice
from string import ascii_lowercase
import binascii

import namedb

count = 0


with open("input.txt") as f:
    for line in f:
        s = line[:-1]
        csum = 0
        for c in s:
            csum = binascii.crc32(s.encode('utf-8'))
            csum &= 0xffff
            namedb.ndb_add_word(s)
            print "{0} -> {1}".format(s, str(csum))

#for n in range(100000):
#    s = ''.join(choice(ascii_lowercase) for i in range(12))
#    csum = 0
#    for c in s:
#        csum = binascii.crc32(s)
#        csum &= 0xffff
#        table[csum].add(s)
#        print "{0} -> {1}".format(s, str(csum))

#s = "abc"
#csum = 0
#for c in "abc":
#    csum = bsd_checksum_reduce(csum, c)
#
#println csum
#
#table[csum].add(s)

for x in range(10):
    print "{0} -> {1}".format(str(x), table[x])

local = (192*256) + 168
home = (127*256) + 0
gdns = (8*256) + 8

print "{0} -> {1}".format(str(local), table[local])
print "{0} -> {1}".format(str(home), table[home])
print "{0} -> {1}".format(str(gdns), table[gdns])
