import sys
import unicodedata
import binascii
import re
import io
import os.path
import re
import time
from datetime import datetime
from types import SimpleNamespace
from math import log

# stats accumulation
stats = SimpleNamespace()
stats.total_in = 0   # input seeds read
stats.total_out = 0  # output words written
stats.censored = 0   # on the naughty list
stats.discarded = 0  # the resulting 'word' is too complicated to keep around
stats.counter = 0    # write output every time this reaches 1k
stats.cache_hit = 0  #
stats.cache_miss = 0

prefixes = """ 
    a al an ant anti at auto ba bad bi bin bio circum cis co contra de demi di dis double down
    e en epi es et ex extra fin for geo he hydro hyper i iac il im in infra inter ir
    macro meta mid min mis mono multi neg neo non o omni or over out pen pent penta poly post pre pro
    quad re semi sim stereo sub super tele tetra therm thermo tran tri triple u uber
    ultra un under uni ul up us zoo
""".split()

prefixes2 = """
    ab ante ap apo auf aut auto ben bene but cata circ com con contro counter dec deca dia dif dys
    ego eigen ein end endo equ equi eu ge hemi hetero hex hexa homeo homo hypo intra intro iso mini mit myo
    necro next ob oct octo omega pan per peri por port porta prop sept sym syn trans up xy zu zy
""".split()

prefixes.extend(prefixes2)

suffixes = """
    acy age al ance ence dom ee er fu ful hood ing ish ism ist ive
    less ly ment ness or ora ous ously ry ship ward wise y
""".split()

suffixes2 = """
    able ably ane aine ase at ate ated cide cline ed ede edly eer eering ein en ene ened est estly
    fy ible ic ide idem iest ify ion ite ity ize izer lex lexi man mance mancer mancy mat
    note noted ode ol ole org ose sum summed son ty ulate up ur xy yne
""".split()

suffixes.extend(suffixes2)

# including several fake prefixes
si_prefixes = """
    yotta zetta exa exbi peta pebi tera tebi giga gibi mega mebi kilo kibi hecto deca
    deci centi milli micro nano pico femto atto zepto yocto
    lotta nova novo hepa ento otta fito nea syto dea tredo una revo
""".split()


start = time.time_ns()
profile_active = True
def profile(msg):
    global start, profile_active
    if profile_active:
        print(f"{msg}: {(time.time_ns()-start) / 1000000} ms")
    if msg=="final":
        profile_active = False


def status(msg, src):
    now = datetime.now()
    out_str = f"{now:%Y%m%d %H:%M:%S}@{src}: {msg}"
    f = open(f"work/{now:%Y%m%d}.log", "a")
    f.write(out_str + '\n')
    f.close()
    print(out_str)


bigrams = {}
with open("lists/english_bigrams_1.txt") as f:
    for line in f:
        bigram_ref = line[0:2].lower()
        raw_freq = float(line[2:len(line)-1])  # skip \n
        score = 20.0 - log(raw_freq)
        bigrams[bigram_ref] = score
        # print ("%s scores %f" % (bigram_ref, score))


def bigram_score(bigram):
    max_bigram_score = 20.0
    return bigrams.get(bigram, max_bigram_score)


def complexity_score(w):
    word_score = 0.0
    length = len(w)
    for pos in range(1, length):
        bigram = w[pos - 1:pos + 1]
        bg_score = bigram_score(bigram)
        word_score += bg_score
    return word_score


complexity_cache = {}


def complexity_score_cached(w):
    global complexity_cache, stats
    if w in complexity_cache:
        stats.cache_hit += 1
        return complexity_cache[w]
    else:
        stats.cache_miss += 1
        new_score = complexity_score(w)
        complexity_cache[w] = new_score
        return new_score


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
        if word[0] != '@':
            bad_frags_trie.add(word)
        else:
            bad_words.add(word[1:])
bad_frags_re = re.compile(bad_frags_trie.pattern())

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


def pluralize_suffix(word):
    last_letter = word[-1]
    if last_letter in "hsxz":
        return "es"
    else:
        return "s"


cached_string_lists = {}
csl_hits = 0
csl_misses = 0


def strings_scoring_less_than(n, list):
    global cached_string_lists, csl_hits, csl_misses
    list_key = list[0]
    cache_key = list_key + ":" + str(n)
    if cache_key in cached_string_lists:
        csl_hits += 1
        return cached_string_lists[cache_key]
    else:
        result = [item for item in list if complexity_score_cached(item) < n]
        cached_string_lists[cache_key] = result
        csl_misses += 1
        return result


def process_seed(line):
    global stats
    seed = line
    #seed = strip_accents(line[:-1])
    #seed = re.sub('\ |\?|\.|\!|/|\;|\:|-|\'', '', seed.lower())
    if len(seed) > 0 and not seed.isalpha():
        print(f"Rejected {seed}")
        stats.rejected += 1
        return

    # bad seed?
    if seed not in bad_words:  # and not bad_frags_re.search(seed):
        seed_score = complexity_score(seed)

        if seed_score < 37:
            permutate(seed, seed_score, None, None, None)
            permutate(seed, seed_score,
                      strings_scoring_less_than(37 - seed_score, si_prefixes),
                      strings_scoring_less_than(37 - seed_score, prefixes),
                      strings_scoring_less_than(37 - seed_score, suffixes))

        # filter out exact matches from blacklist
        #words2 = [word for word in words if word not in bad_words]

        # filter out fragment matches from blacklist
        #words3 = [word for word in words2 if not bad_frags_re.search(word)]
        #stats.censored += (len(words) - len(words3))

        # censorship debugging:
        #removed = list(set(words) - set(words3))
        #import random
        #if len(removed) > 0:
        #    samp = random.choice(removed)
        #    print(f"removed {samp} because {bad_frags_re.search(samp)}")
    else:
        stats.censored += 100000
        status(f"blocked seed {seed}", outfile_prefix)

    # track stats
    stats.total_in += 1
    stats.counter += 1
    if stats.counter >= 100:
        # flush to disk
        for idx in range(256):
            folder = hexdigits[(idx & 0xf0) >> 4]
            suffix = hexdigits[idx & 0x0f]

            target_file = open(f"work/{folder}/{outfile_prefix}_{suffix}.txt", "a")
            target_file.writelines(buffers[idx])
            buffers[idx] = []
            target_file.close()

        s = stats
        o = outfile_prefix
        status(f"in:{s.total_in:,} out:{s.total_out:,} 🤬:{s.censored:,} 🗑️:{s.discarded:,} cache:{s.cache_hit:,} seed:{seed}", o)
        stats.counter = 0


hexdigits = "0123456789abcdef"

# For each of the 256 output files, maintain an array of strings to be joined at write-time
buffers = [[] for n in range(256)]


def permutate(seed, seed_score, siprefixes, prefixes, suffixes):
    """unrolled..."""
    global stats, buffers
    MAX_COMPLEXITY = 45

    if seed == "":
        return

    def write_results(word, score):
        if score >= MAX_COMPLEXITY:
            stats.discarded += 1
            # print(f"discarded {word} with score {score}")
        else:
            crc = binascii.crc32(word.encode("utf-8"))
            top_4_bits = (crc & 0xf0000000) >> 28
            nxt_4_bits = (crc & 0x0f000000) >> 24
            #out[top_4_bits][nxt_4_bits].write(f"{crc:08x} {score:02.0f} {word}\n")
            buffers[16 * top_4_bits + nxt_4_bits].append(f"{crc:08x} {score:02.0f} {word}\n")
            # print(f"{crc:08x} {score:02.0f} {word}")
            stats.total_out += 1

    def write_results_plural(word, score):
        """Pluralize without recomputing complexity"""
        ps = pluralize_suffix(word)
        if len(ps)==2:
            write_results(word + ps, score + bigram_score(word[-1] + ps[0]) + complexity_score_cached(ps))
        else: # 1
            write_results(word + ps, score + bigram_score(word[-1] + ps[0]))

    if siprefixes is None and prefixes is None and suffixes is None:
        write_results(word, score)
        write_results_plural(word, score)

    if prefixes is not None:
        for p in prefixes:
            prefix_cplx = complexity_score_cached(p)
            adj_cplx = bigram_score(p[-1] + seed[0])
            complexity = prefix_cplx + adj_cplx + seed_score
            word_out = p + seed
            if 0 and bad_frags_re.search(word_out):
                stats.censored += 1
                print(f"removed {word_out} because {bad_frags_re.search(word_out)}")
            else:
                write_results(word_out, complexity)
                write_results_plural(word_out, complexity)

    if suffixes is not None:
        for s in suffixes:
            suffix_cplx = complexity_score_cached(s)
            adj_cplx = bigram_score(seed[-1] + s[0])
            complexity = seed_score + adj_cplx + suffix_cplx
            word_out = seed + s
            if 0 and bad_frags_re.search(word_out):
                stats.censored += 1
                print(f"removed {word_out} because {bad_frags_re.search(word_out)}")
            else:
                write_results(word_out, complexity)
                write_results_plural(word_out, complexity)

    if siprefixes is not None:
        for sip in siprefixes:
            sipfx_cplx = complexity_score_cached(sip)
            adj_cplx = bigram_score(sip[-1] + seed[0])
            complexity = sipfx_cplx + adj_cplx + seed_score
            word_out = sip + seed
            if 0 and bad_frags_re.search(word_out):
                stats.censored += 1
                print(f"removed {word_out} because {bad_frags_re.search(word_out)}")
            else:
                write_results(word_out, complexity)
                write_results_plural(word_out, complexity)

    if prefixes is not None and suffixes is not None:
        for p in prefixes:
            for s in suffixes:
                prefix_cplx = complexity_score_cached(p)
                suffix_cplx = complexity_score_cached(s)
                adj_cplx1 = bigram_score(p[-1] + seed[0])
                adj_cplx2 = bigram_score(seed[-1] + s[0])
                complexity = prefix_cplx + adj_cplx1 + seed_score + adj_cplx2 + suffix_cplx
                word_out = p + seed + s
                if 0 and bad_frags_re.search(word_out):
                    stats.censored += 1
                    print(f"removed {word_out} because {bad_frags_re.search(word_out)}")
                else:
                    write_results(word_out, complexity)
                    write_results_plural(word_out, complexity)

    if siprefixes is not None and suffixes is not None:
        for sip in siprefixes:
            for s in suffixes:
                sipfx_cplx = complexity_score_cached(sip)
                suffix_cplx = complexity_score_cached(s)
                adj_cplx1 = bigram_score(sip[-1] + seed[0])
                adj_cplx2 = bigram_score(seed[-1] + sip[0])
                complexity = sipfx_cplx + adj_cplx1 + seed_score + adj_cplx2 + suffix_cplx
                word_out = sip + seed + s
                if 0 and bad_frags_re.search(word_out):
                    stats.censored += 1
                    print(f"removed {word_out} because {bad_frags_re.search(word_out)}")
                else:
                    write_results(word_out, complexity)
                    write_results_plural(word_out, complexity)

    if siprefixes is not None and prefixes is not None:
        for sip in siprefixes:
            for p in prefixes:
                sipfx_cplx = complexity_score_cached(sip)
                prefix_cplx = complexity_score_cached(p)
                adj_cplx1 = bigram_score(sip[-1] + p[0])
                adj_cplx2 = bigram_score(p[-1] + seed[0])
                complexity = sipfx_cplx + adj_cplx1 + prefix_cplx + adj_cplx2 + seed_score
                word_out = sip + p + seed
                if 0 and bad_frags_re.search(word_out):
                    stats.censored += 1
                    print(f"removed {word_out} because {bad_frags_re.search(word_out)}")
                else:
                    write_results(word_out, complexity)
                    write_results_plural(word_out, complexity)

    if siprefixes is not None and prefixes is not None and suffixes is not None:
        for sip in siprefixes:
            for p in prefixes:
                for s in suffixes:
                    sipfx_cplx = complexity_score_cached(sip)
                    prefix_cplx = complexity_score_cached(p)
                    suffix_cplx = complexity_score_cached(s)
                    adj_cplx1 = bigram_score(sip[-1] + p[0])
                    adj_cplx2 = bigram_score(p[-1] + seed[0])
                    adj_cplx3 = bigram_score(seed[-1] + s[0])
                    complexity = sipfx_cplx + adj_cplx1 + prefix_cplx + adj_cplx2 + seed_score + adj_cplx3 + suffix_cplx
                    word_out = sip + p + seed + s
                    if 0 and bad_frags_re.search(word_out):
                        stats.censored += 1
                        print(f"removed {word_out} because {bad_frags_re.search(word_out)}")
                    else:
                        write_results(word_out, complexity)
                        write_results_plural(word_out, complexity)


seeds = []

if is_test:
    # representative data via
    # % shuf -n 100 lists/seeds.txt
    seeds = io.StringIO("""weevyou
jyyidyao
auhyaoz
yosmiubr
iblaid
skyibsyou
aestiu
poicsiu
graumo
iahyyolp
imyoors
slyalyee
tsiudyaye
ruilfoa
sbozau
rayerkyi
eeboopr
fuezyui
theyeraye
floinae
yipreaky
vyoessoye
eidrast
hieloye
chrilsou
blyingo
yiulsya
uisyoent
joistee
thayesyoo
kauhyle
prevle
aryyouny
iacsoef
zaeb
smoidyue
yanseyecs
bluethou
audyaex
msoempae
uizyyoph
iuphayery
oicisn
iazyyiby
oofyyist
pseimpai
kauveu
sweyedyeu
feusheu
smeodoo
syuelkie
oagoelp
iofaofy
treyesyao
scuorsae
iudyezy
uachriogy
tsouxya
aulyaun
shyilyui
otyeyeky
jaudse
bdioryyo
ueksasc
byyilia
tyoursie
oojaing
lilphuo
skeeksoa
oyelseyems
cayezh
oagalt
iesyoiby
dseicyou
opeeb
eisbaiky
oibleorm
chuiboe
csoosniu
euchyag
iusmeiby
tweithe
eagsoufy
kaujyie
diuprui
heyekyyi
oalpheix
oamseerth
tustya
aipleebs
ouquuit
plouxa
lyuryoo
eyeshomy
slyontie
kyiajyou
ayeskoss
iugyeiw
yisbucy
osmiuby
""").readlines()

else:
    f = open(sys.argv[1], "r")
    seeds = f.readlines()
    f.close()

for seed in [s.rstrip() for s in seeds]:
    process_seed(seed)

#temp = open('lists/seed_cplx.txt', 'w')
# looking at initial seeds
#for line in open('lists/seeds.txt'):
#    seed = line.strip()
#    score = complexity_score(seed)
#    temp.write(f"{score:02.0f} {seed}\n")

print(stats)
print(f"{csl_hits} {csl_misses}")
