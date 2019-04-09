prefixes = ['anti', 'auto', 'bi', 'bio', 'circum', 'co', 'contra', 'de', 'demi', 'dis', 'double', 'down', 'epi', 'extra', 'geo', 'hydro', 'hyper', 'il', 'im', 'in', 'ir', 'infra', 'inter', 'macro', 'meta', 'mid', 'mis', 'mono',
            'multi', 'non', 'omni', 'over', 'out', 'penta', 'poly', 'post', 'pre', 'pro', 'quadra', 're', 'semi', 'stereo', 'sub', 'super', 'tele', 'tetra', 'thermo', 'trans', 'tri', 'triple', 'uber', 'ultra', 'un', 'under', 'up']
suffixes = ['acy', 'age', 'al', 'ance', 'ence', 'dom', 'ee', 'er', 'ful' 'hood', 'ing', 'ish', 'ism', 'ist', 'ive', 'less', 'ment', 'ness', 'or', 'ous', 'ously', 'ry', 'ship', 'ward', 'wise']

si_prefixes = ['yotta', 'zetta', 'exa', 'peta', 'tera', 'giga', 'mega', 'kilo', 'hecto', 'deca', 'deci', 'centi', 'milli', 'micro', 'nano', 'pico', 'femto', 'atto', 'zepto', 'yocto']
prefixes.extend(si_prefixes)

badwords = set()
badfrags = []

with open("bad.words.txt") as badw:
    for line in badw:
        word = line[:-1]
        if word[0] == '@':
            badwords.add(word[1:])
        else:
            badfrags.append(word)

# output file
fulldict = open("fulldict.txt", "w")
total = 0
count = 0

with open("baredict.txt") as f:
    for line in f:
        word = line[:-1]
        if word == '':
            break
        words = [word]
        words.extend([pf + word for pf in prefixes])
        words.extend([word + sf for sf in suffixes])
        words.extend([pf + word + sf for pf in prefixes for sf in suffixes])
        # words.extend([pf1 + pf2 + word for pf1 in prefixes for pf2 in prefixes if pf1 != pf2])
        # words.extend([pf1 + pf2 + word + sf for pf1 in prefixes for pf2 in prefixes for sf in suffixes if pf1 != pf2])
        # print(words)

        # filter out fragment matches from blacklist
        words2 = []
        for w in words:
            accept = True
            for frag in badfrags:
                if frag in w:
                    accept = False
            if accept:
                words2.append(w)
        # print("len is %d" % len(words2))

        # filter out exact matches from blacklist
        words3 = [word for word in words2 if word not in badwords]

        fulldict.write('\n'.join(words3))
        ln = len(words3)
        total += ln
        count += ln
        if count > 100000:
            print("len is %d" % ln)
            print(words3[:10])
            print(total)
            count = 0

fulldict.close()