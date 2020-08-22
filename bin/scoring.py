import sys
from math import log
import itertools

from datetime import datetime

import time
start = time.time_ns()
profile_active = True
def profile(msg):
    global start, profile_active
    if profile_active:
        print(f"{msg}: {(time.time_ns()-start) / 1000000} ms")
    if msg=="final":
        profile_active = False

bigrams = {}
with open("lists/english_bigrams_1.txt") as f:
    for line in f:
        bigram_ref = line[0:2].lower()
        raw_freq = float(line[2:len(line)-1])  # skip \n
        score = 20.0 - log(raw_freq)
        bigrams[bigram_ref] = score
        # print ("%s scores %f" % (bigram_ref, score))

len_alpha = 26

bigrams_fast1 = []
zero_point = ord('a')
for let1 in range(len_alpha):
    for let2 in range(len_alpha):
        bigrams_fast1.append(20.0)
print(len(bigrams_fast1))
with open("lists/english_bigrams_1.txt") as f:
    for line in f:
        raw_freq = float(line[2:len(line)-1])  # skip \n
        score = 20.0 - log(raw_freq)
        byte1 = ord(line[0].lower())
        byte2 = ord(line[1].lower())
        idx = (byte1 - zero_point)*len_alpha + (byte2 - zero_point)
        bigrams_fast1[idx] = score


def complexity_score(w):
    word_score = 0.0
    max_bigram_score = 20.0
    length = len(w)
    for pos in range(1, length):
        bigram = w[pos - 1:pos + 1]
        bigram_score = bigrams.get(bigram, max_bigram_score)
        word_score += bigram_score
    return word_score


a = 0
b = 0
c = 0
d = 0
e = 0
g = 0

def complexity_score_fast(w):
    global a, b, c, d, e, g
    word_score = 0.0
    bytes = [ord(cr) for cr in w]
    ts = time.time_ns()
    a += (time.time_ns() - ts)
    ts = time.time_ns()
    length = len(bytes)
    b += (time.time_ns() - ts)

    for pos in range(1, length):
        ts = time.time_ns()
        first = (bytes[pos - 1] - zero_point)*len_alpha
        c += (time.time_ns() - ts)
        ts = time.time_ns()
        second = (bytes[pos] - zero_point)
        d += (time.time_ns() - ts)
        ts = time.time_ns()
        ofs = first + second
        e += (time.time_ns() - ts)
        ts = time.time_ns()
        word_score += bigrams_fast1[ofs]
        g += (time.time_ns() - ts)
    return word_score


lines = []
with open(sys.argv[1]) as f:
    lines = f.readlines()
print(len(lines))

start = time.time_ns()

#for line in lines:
#    score = complexity_score(line)
#
#profile(f"method1 {complexity_score('hello')}")

start = time.time_ns()

for line in lines:
        score = complexity_score_fast(line)

profile(f"method2 {complexity_score_fast('hello')}")

print(f"a {a / 1000000}")
print(f"b {b / 1000000}")
print(f"c {c / 1000000}")
print(f"d {d / 1000000}")
print(f"e {e / 1000000}")
print(f"g {g / 1000000}")
