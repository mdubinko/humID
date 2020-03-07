import random

# TODO: weirdo consonants: aBLE succeSSFul liTTLe educaTION
init = []
post = []
init.extend("b bd bl br bs by c ch chr cl cr cs ct cy d dr ds dy f fl fr fy g gl gr gs gy h hy j jy k ks ky".split())
post.extend("b       br bs by c ch     cl    cs ct cy d    ds dy f       fy g       gs gy h hy j jy k ks ky".split())

init.extend("l                         lph ls lt ly m    ms my n          ns    ny p ph pl pr ps py qu r   ".split())
post.extend("l ld lf lg ll lk lm ln lp lph ls lt ly m mp ms my n nd ng nk ns nt ny p ph    pr ps py    r rk".split())

init.extend("             ry s sb sc sh sk sl sm sn sp    st sv sw sy t th tr ts tw ty v vy w wh x y z zh zy".split())
post.extend("rm rs rt rth ry s    sc sh sk    sm sn sp ss st       sy t th    ts    ty v vy w    x y z zh zy".split())

vowels = "a e i o u ae ai ao au aye ea ee ei eo eu eye ia ie io iu oa oe oi oo oye ou ua ue ui uo ya yi yo you".split()

# single syllable seeds: V CV CVC CVCe VC VCe Cle
syllables1 = []
syllables1.extend(vowels)
syllables1.extend([c1 + v for c1 in init for v in vowels])
syllables1.extend([c1 + v + c2 for c1 in init for v in vowels for c2 in post])
syllables1.extend([c1 + v + c2 + "e" for c1 in init for v in vowels for c2 in post])
syllables1.extend([v + c2 for v in vowels for c2 in post])
syllables1.extend([v + c2 + "e" for v in vowels for c2 in post])
syllables1.extend([c + "le" for c in post])

# two syllable seeds: VCle CVCle VCV CVCV VCV VCVC
syllables2 = []
syllables2.extend([v + c2 + "le" for v in vowels for c2 in post])
syllables2.extend([c1 + v + c2 + "le" for c1 in init for v in vowels for c2 in post])
syllables2.extend([v1 + c + v2 for v1 in vowels for c in init for v2 in vowels])
syllables2.extend([c1 + v1 + c2 + v2 for c1 in init for v1 in vowels for c2 in post for v2 in vowels])
syllables2.extend([v1 + c1 + v2 for v1 in vowels for c1 in init for v2 in vowels])
syllables2.extend([v1 + c1 + v2 + c2 for v1 in vowels for c1 in init for v2 in vowels for c2 in post])

print(len(syllables1))
print(len(syllables2))

with open("lists/seeds.txt", "w") as f:
    for s in syllables1:
        f.write(f"{s}\n")
    for s in syllables2:
        f.write(f"{s}\n")

print(random.choice(syllables1))
print(random.choice(syllables1))
print(random.choice(syllables1))
print(random.choice(syllables1))
print(random.choice(syllables1))

print(random.choice(syllables2))
print(random.choice(syllables2))
print(random.choice(syllables2))
print(random.choice(syllables2))
print(random.choice(syllables2))
