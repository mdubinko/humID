import sys
from types import SimpleNamespace

argc = len(sys.argv)
files = [sys.stdin] if argc < 2 else sys.argv[1:]
for f in files:
    # stats accumulation
    s = SimpleNamespace()
    s.bestwords = ["" for x in range(2**24)]
    s.id_min = 9999999999
    s.id_max = -1

    with open(f) as fp:
        for line in fp:
            parsed = line.split(" ")
            humid = int(parsed[0], base=16)
            score = int(parsed[1])
            word = parsed[2].strip()

            if humid < s.id_min:  # this should only happen once, on the first line
                s.id_min = humid

            if humid < s.id_max:
                sys.exit(f"{f} was not sorted: {humid:0{8}x} vs {s.id_max:0{8}x}")

            if humid > s.id_max:  # this should only happen once per new humid
                s.id_max = humid
                s.bestwords[humid - s.id_min] = word

    with open(f"{s.id_min:0{8}x}_lookup.txt", "w") as fp:
        for a in s.bestwords:
            fp.writelines(a + "\n")
