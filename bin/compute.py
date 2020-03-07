import sys
import unicodedata
import binascii
import re
import io
import os.path
import re
from datetime import datetime
from types import SimpleNamespace
from math import log


import time
start = time.time_ns()
profile_active = True
def profile(msg):
    global start, profile_active
    if profile_active:
        print(f"{msg}: {(time.time_ns()-start) / 1000000} ms")
    if msg=="final":
        profile_active = False

prefixes = """
    a al an ant anti at auto ba bad bi bin bio circum cis co contra de demi di dis double down
    e en epi es et ex extra fin for geo he hydro hyper i iac il im in infra inter ir
    macro meta mid min mis mono multi neg neo non o omni or over out pen pent penta poly post pre pro
    quad re semi sim stereo sub super tele tetra therm thermo tran tri triple u uber
    ultra un under uni ul up us zoo
""".split()

suffixes = """
    acy age al ance ence dom ee er fu ful hood ing ish ism ist ive
    less ly ment ness or ora ous ously ry ship ward wise y
""".split()

# including several fake prefixes
si_prefixes = """
    yotta zetta exa exbi peta pebi tera tebi giga gibi mega mebi kilo kibi hecto deca
    deci centi milli micro nano pico femto atto zepto yocto
    lotta nova novo hepa ento otta fito nea syto dea tredo una revo
""".split()

# including a blank word at the beginning!
test_words = io.StringIO("""
a
b
c
d
e
ant
bug
cat
dog
elf
""")

bigrams = {}
with open("lists/english_bigrams_1.txt") as f:
    for line in f:
        bigram_ref = line[0:2].lower()
        raw_freq = float(line[2:len(line)-1])  # skip \n
        score = 20.0 - log(raw_freq)
        bigrams[bigram_ref] = score
        # print ("%s scores %f" % (bigram_ref, score))


def complexity_score(w):
    word_score = 0.0
    max_bigram_score = 20.0
    length = len(w)
    for pos in range(1, length):
        bigram = w[pos - 1:pos + 1]
        bigram_score = bigrams.get(bigram, max_bigram_score)
        word_score += bigram_score
    return word_score


def strip_accents(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')


class Trie:
    """Regex::Trie in Python. Creates a Trie out of a list of words. The trie can be exported to a Regex pattern.
    The corresponding Regex should match much faster than a simple Regex union.
    based on
    https://stackoverflow.com/questions/42742810/speed-up-millions-of-regex-replacements-in-python-3
    thanks, Eric Duminil!
    """
    def __init__(self):
        self.data = {}

    def add(self, word):
        ref = self.data
        for char in word:
            ref[char] = char in ref and ref[char] or {}
            ref = ref[char]
        ref[''] = 1

    def dump(self):
        return self.data

    def quote(self, char):
        return re.escape(char)

    def _pattern(self, pData):
        data = pData
        if "" in data and len(data.keys()) == 1:
            return None

        alt = []
        cc = []
        q = 0
        for char in sorted(data.keys()):
            if isinstance(data[char], dict):
                try:
                    recurse = self._pattern(data[char])
                    alt.append(self.quote(char) + recurse)
                except:
                    cc.append(self.quote(char))
            else:
                q = 1
        cconly = not len(alt) > 0

        if len(cc) > 0:
            if len(cc) == 1:
                alt.append(cc[0])
            else:
                alt.append('[' + ''.join(cc) + ']')

        if len(alt) == 1:
            result = alt[0]
        else:
            result = "(?:" + "|".join(alt) + ")"

        if q:
            if cconly:
                result += "?"
            else:
                result = "(?:%s)?" % result
        return result

    def pattern(self):
        return self._pattern(self.dump())


bad_words = set()
bad_frags_trie = Trie()
with open("lists/bad.words.txt") as badw:
    for line in badw:
        word = line[:-1]
        if word[0] == '@':
            bad_frags_trie.add(word[1:])
        else:
            bad_words.add(word)
bad_frags_re = re.compile(bad_frags_trie.pattern())

# stats accumulation
stats = SimpleNamespace()
stats.total_in = 0   # input seeds read
stats.total_out = 0  # output words written
stats.rejected = 0   # non-alpha (should never happen)
stats.censored = 0   # on the naughty list
stats.discarded = 0  # the resulting 'word' is too complicated to keep around
stats.counter = 0    # write output every time this reaches 1k

# 256 output files
argc = len(sys.argv)
outfile_prefix = ""
is_test = False
if not argc == 2:
    print("no filename specified; using test data")
    outfile_prefix = "TEST"
    is_test = True
else:
    outfile_prefix = os.path.basename(sys.argv[1]).split(".")[0]

hexdigits = "0123456789abcdef"
out = []
for folder in hexdigits:
    handles = []
    for suffix in hexdigits:
        handles.append(open(f"db/{folder}/{outfile_prefix}_{suffix}.txt", "w"))
    out.append(handles)


def pluralize(word):
    last_letter = word[-1]
    if last_letter in "hsxz":
        return word + "es"
    else:
        return word + "s"


def process_line(line):
    profile("A")
    global stats, out
    seed = strip_accents(line[:-1])
    seed = re.sub('\ |\?|\.|\!|/|\;|\:|-|\'', '', seed.lower())
    if len(seed)>0 and not seed.isalpha():
        print(f"Rejected {seed}")
        stats.rejected += 1
        return
    words = [seed]
    profile("B")
    words.extend([seed + sfx for sfx in suffixes])
    words.extend([pluralize(seed + sfx) for sfx in suffixes])

    words.extend([pfx + seed for pfx in prefixes])
    words.extend([pluralize(pfx + seed) for pfx in prefixes])

    words.extend([pfx + seed + sfx for pfx in prefixes for sfx in suffixes])
    words.extend([pluralize(pfx + seed + sfx) for pfx in prefixes for sfx in suffixes])

    words.extend([si + seed for si in si_prefixes])
    words.extend([pluralize(si + seed) for si in si_prefixes])

    words.extend([si + seed + sfx for si in si_prefixes for sfx in suffixes])
    words.extend([pluralize(si + seed + sfx) for si in si_prefixes for sfx in suffixes])

    words.extend([si + pfx + seed for si in si_prefixes for pfx in prefixes])
    words.extend([pluralize(si + pfx + seed) for si in si_prefixes for pfx in prefixes])

    words.extend([si + pfx + seed + sfx for si in si_prefixes for pfx in prefixes for sfx in suffixes])
    words.extend([pluralize(si + pfx + seed + sfx) for si in si_prefixes for pfx in prefixes for sfx in suffixes])

    # filter out exact matches from blacklist
    profile("C")
    words2 = [word for word in words if word not in bad_words]

    # filter out fragment matches from blacklist
    profile("D")
    words3 = [word for word in words2 if not bad_frags_re.search(word)]
    stats.censored += (len(words) - len(words3))

    # censorship debugging:
    #removed = list(set(words) - set(words3))
    #import random
    #if len(removed) > 0:
    #    samp = random.choice(removed)
    #    print(f"removed {samp} because {bad_frags_re.search(samp)}")

    # finally, process each word from this seed
    profile("E")
    for w in words3:
        # decide if this one is too complicated to keep
        complexity = complexity_score(w)
        if complexity >= 45:
            stats.discarded += 1
            continue

        crc = binascii.crc32(w.encode("utf-8"))
        top_4_bits = (crc & 0xf0000000) >> 28
        nxt_4_bits = (crc & 0x0f000000) >> 24
        out[top_4_bits][nxt_4_bits].write(f"{crc:08x} {complexity:02.0f} {w}\n")
        #print(f"{crc:08x} {complexity:02.2f} {w}")
        stats.total_out += 1

    # track stats
    profile("F")
    stats.total_in += 1
    stats.counter += 1
    if stats.counter >= 100:
        s = stats
        n = datetime.now()
        print(f"{n} in:{s.total_in:,} out:{s.total_out:,} 🚫:{s.rejected:,} 🤬:{s.censored:,} 🗑️:{s.discarded:,}")
        stats.counter = 0
        # flush to disk
        for fld in out:
            for fp in fld:
                fp.flush()
    profile("final")


if is_test:
    with test_words:
        for line in test_words:
            process_line(line)
else:
    with open(sys.argv[1]) as f:
        for line in f:
            process_line(line)
