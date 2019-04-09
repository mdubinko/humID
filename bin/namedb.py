from random import choice
from string import ascii_lowercase
import binascii

ndb_size = 2**24
ndb_inmem = [set() for x in range(ndb_size) ]
ndb_filename = "namedb.txt"


def hextet(i):
    '''6-hex-digit padded string. E.g. 0-> "000000" or 255-> "0000FF" '''
    return str.format('{:06X}', i)


def word_hash(s):
    '''compute 24-bit hash of any given input'''
    crc = binascii.crc32(bytes(s, 'utf-8'))
    return crc & 0xffffff


# write a new, empty database
def ndb_new():
    with open(ndb_filename, "w") as f:
        for n in range(ndb_size):
            f.write(hextet(n) + '\n')
    f.close()


# read an existing database into memory
def ndb_read():
    with open(ndb_filename) as f:
        for line in f:
            words = line.split(" ")
            if line == "" or line.startswith("#") or line.startswith("\n"):
                continue
            idx = int(words[0], 16)
            #print("adding @" + str(idx))
            for w in words[1:]:
                if w != "\n":
                    ndb_inmem[idx].add(w.strip())
    f.close()


# write memory database to disk
def ndb_write():
    with open(ndb_filename, "w") as f:
        for n in range(ndb_size):
            f.write(hextet(n))
            for w in ndb_inmem[n]:
                f.write(" " + w)
            f.write("\n")
    f.close()


# hash and add a word
def ndb_add_word(w):
    idx = word_hash(w)
    ndb_inmem[idx].add(w)


def shortest_in_set(s):
    shortest = 9999
    for word in s:
        if len(word) < shortest:
            shortest = len(word)
    return shortest


# produce histogram of shortest words
def shortest_hist():
    hist = {}
    for n in range(ndb_size):
        shortest = shortest_in_set(ndb_inmem[n])
        if shortest > 8:
            print("" + str(hextet(n)) + "@")
            print(ndb_inmem[n])
        if shortest in hist:
            hist[shortest] = hist[shortest] + 1
        else:
            hist[shortest] = 1
    return hist

print(hextet(0))
print(hextet(0xff))
print(hextet(0xffff))
print(hextet(0xffffff))

#ndb_read()

#print(hextet(word_hash("")))
#print(hextet(word_hash("😀")))
#print(hextet(word_hash("❤️")))
#print(hextet(word_hash("💩")))
#print(hextet(word_hash("👍")))
#print(hextet(word_hash("🐍")))
#print(hextet(word_hash("🐷")))
#print(hextet(word_hash("🥚")))

#with open("/usr/share/dict/words") as f:
#    for line in f:
#        ndb_add_word(line.strip().lower())

#print(shortest_hist())

#ndb_write()