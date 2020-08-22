import sys
from types import SimpleNamespace

argc = len(sys.argv)
files = [sys.stdin] if argc < 2 else sys.argv[1:]
for f in files:
    # stats accumulation
    s = SimpleNamespace()
    s.cnt = 0
    s.histogram = [0 for x in range(2**24)]
    s.best = ["" for x in range(2**24)]
    s.secondbest = ["" for x in range (2**24)]
    s.secondnext = False
    s.id_min = 9999999999
    s.id_max = -1
    s.id_cnt = 0
    s.cnt_under_20 = 0
    s.cnt_under_25 = 0
    s.cnt_under_30 = 0
    s.cnt_under_35 = 0
    s.score_min = 99
    s.score_min_word = ""
    s.score_total = 0
    s.best_score_total = 0

    with open(f) as fp:
        for line in fp:
            parsed = line.split(" ")
            humid = int(parsed[0], base=16)
            score = int(parsed[1])
            word = parsed[2].strip()
            s.cnt += 1
            s.score_total += score

            if humid < s.id_min:  # this should only happen once, on the first line
                s.id_min = humid

            if humid < s.id_max:
                sys.exit(f"{f} was not sorted: {humid:0{8}x} vs {s.id_max:0{8}x}")

            if humid > s.id_max:  # this should only happen once per new humid
                s.id_max = humid
                s.id_cnt += 1
                s.best_score_total += score  # sorted; first score will be lowest
                s.best[humid - s.id_min] = line
                s.secondnext = True
                if score <= 20: s.cnt_under_20 += 1
                if score <= 25: s.cnt_under_25 += 1
                if score <= 30: s.cnt_under_30 += 1
                if score <= 35: s.cnt_under_35 += 1
            else:
                if s.secondnext:
                    s.secondbest[humid - s.id_min] = line
                    s.secondnext = False

            s.histogram[humid - s.id_min] += 1

            if score < s.score_min:
                s.score_min = score
                s.score_min_word = word

    avg_best_score = s.best_score_total / s.id_cnt
    avg_score = s.score_total / s.cnt
    empties = sum(1 for i in s.histogram if i == 0)
    with open(f"{s.id_min:0{8}x}_backup.txt", "w") as fp:
        for a, b in zip(s.best, s.secondbest):
            fp.writelines(a+b)
    print(f'{s.cnt:,} {s.id_min:0{8}x}-{s.id_max:0{8}x} {avg_best_score:.2f} {avg_score:.2f} ∅={empties} '
          f'<20,25,30,35={s.cnt_under_20},{s.cnt_under_25},{s.cnt_under_30},{s.cnt_under_35} {f} ')
