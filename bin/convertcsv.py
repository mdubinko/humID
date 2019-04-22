import sys
import csv
import os.path
import unicodedata
import binascii
from math import log

prefixes = ['anti', 'auto', 'bi', 'bio', 'circum', 'co', 'contra', 'de', 'demi', 'dis', 'double', 'down', 'epi',
            'extra', 'geo', 'hydro', 'hyper', 'il', 'im', 'in', 'ir', 'infra', 'inter', 'macro', 'meta', 'mid', 'mis',
            'mono',
            'multi', 'non', 'omni', 'over', 'out', 'penta', 'poly', 'post', 'pre', 'pro', 'quadra', 're', 'semi',
            'stereo', 'sub', 'super', 'tele', 'tetra', 'thermo', 'trans', 'tri', 'triple', 'uber', 'ultra', 'un',
            'under', 'up']
suffixes = ['acy', 'age', 'al', 'ance', 'ence', 'dom', 'ee', 'er', 'ful' 'hood', 'ing', 'ish', 'ism', 'ist', 'ive',
            'less', 'ment', 'ness', 'or', 'ous', 'ously', 'ry', 'ship', 'ward', 'wise']

si_prefixes = ['yotta', 'zetta', 'exa', 'peta', 'tera', 'giga', 'mega', 'kilo', 'hecto', 'deca', 'deci', 'centi',
               'milli', 'micro', 'nano', 'pico', 'femto', 'atto', 'zepto', 'yocto']
prefixes.extend(si_prefixes)

fake_si_prefixes = ['hepa', 'ento', 'otta', 'fito', 'nea', 'syto', 'dea', 'tredo', 'una', 'revo', 'harpo', 'groucho',
                    'gummo', 'zeppo', 'chico']
prefixes.extend((fake_si_prefixes))

bigrams = {}
default_score = 20.0
with open("lists/english_bigrams_1.txt") as f:
    for line in f:
        bigram = line[0:2].lower()
        raw_freq = float(line[2:len(line) - 1])  # skip \n
        score = 20.0 - log(raw_freq)
        bigrams[bigram] = score

# CSV file to have same name as input, with extension .csv
file_without_ext = os.path.splitext(sys.argv[1])[0]
csvfp = open(file_without_ext + ".csv", 'w')
csv_writer = csv.writer(csvfp, quoting=csv.QUOTE_MINIMAL)


def strip_accents(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s)
                   if unicodedata.category(c) != 'Mn')


def word_score(word):
    score = 0.0
    length = len(word)
    for pos in range(1, length):
        bigram = word[pos - 1:pos + 1]
        bigram_score = bigrams.get(bigram, default_score)
        score += bigram_score
    return score


total = 0
count = 0
progress = 0

# Realistically, the best way to get this into a database is via CSP
# Using the following...

with open(sys.argv[1]) as f:
    for line in f:
        #word = strip_accents(line[:-1])
        #word = re.sub('\ |\?|\.|\!|\/|\;|\:|-|\'', '', word.lower())
        word = line.rstrip()
        if word == '' or not word.isalpha():
            print("Rejected {word} " + word)
            continue
        words = [word]
        words.extend([pf + word for pf in prefixes])
        words.extend([word + sf for sf in suffixes])
        words.extend([pf + word + sf for pf in prefixes for sf in suffixes])

        # words.extend([pf1 + pf2 + word for pf1 in prefixes for pf2 in prefixes if pf1 != pf2])
        # words.extend([pf1 + pf2 + word + sf for pf1 in prefixes for pf2 in prefixes for sf in suffixes if pf1 != pf2])
        # print(words)

        for word in words:
            if len(word) > 20:
                continue
            csv_writer.writerow([word, binascii.crc32(word.encode('utf-8')), word_score(word)])

        ln = len(words)
        total += ln
        count += ln
        progress += 1
        if count > 100000:
            print("progress is %d from source, %d total" % (progress, total))
            print(words[:1])
            count = 0

csvfp.close()
