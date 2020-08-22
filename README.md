# humID

Humane GUIDs and other identifiers
Implemented with code highly optimized-for-a-purpose

Suppose you had to read an arbitrary IPv6 address over the phone. How difficult would that be?

How about a 160 bit Ethereum address? Or a good old-fashioned GUID?

Suppose your webapp uses GUIDs internally, but they end up exposed in a URL.
You could blast out the usual GUID syntax, with seemingly randomly-placed dashes. Or you could spit out 22 charcters of base64 line noise.

Or you could do better. That's where this project comes in.

My initial thought was to assemble a list of 256 short, easily-pronounceable words, assigning one to each number 0-255.
Then you could replace each byte in an identifier with a word. Say 192.168.10.20 to spam.eggs.foo.bar.
But that doesn't get you much. Why not a dictionary of 65536 words? Then we can map two bytes to each word.
In this era of big data, why not go full 32-bit?

And 'words' don't necessarily have to appear in the dictionary--just be more-or-less pronounceable.

So far so good, but if the project depends on a single global dictionary, there's bound to be problems.
1) There's always the possibility of an inappropriate word appearing in the lookup table. Maybe not even a classic
swear word...say the middle four letters of a nine-letter made-up word are a horrible slur in Urdu.
2) Trademarks. What if someone comes along with a cease-and-desist letter, demanding to remove an entry?

Either of these events would require changing the global lookup table, possibly invalidating all the existing stored
data, URLs, etc. encoded with it. No good. But there's an even more insidious problem.

3) What I consider pronouncable isn't universal. Out of all the words in various languages there's little agreement on
what is "easily" pronouncable. I wouldn't even know how to evaluate "pronouncable" words in CJK languages.

So we can't rely on a global lookup table.

Instead, it uses a deliberately-simple hash function. *Any* sequence of UTF-8 bytes can be hashed down to 32 bits. There's even a well-known CRC32 algorithm (as used in ZIP files) with implementations in Python in many other languages.

Let's do this. For every integer in the 32-bit space, let's find a conveniently short 'word'.

To translating from word -> int we can use the well-known CRC32 algorithm (as defined in PKZIP among other places).
Translating from int -> word is trickier. We need some kind of a database.

In this initial implementation, words use only [a-z].

```python
def word_hash(s):
    crc = binascii.crc32(bytes(s, 'utf-8'))
    return crc & 0xffffff
```

If you want to make your own dictionary, go for it. It could use CJK langauges, or emoji, or nothing but offensive
words. Knock yourself out. Just maybe this would be the basis for a decent password generator.

Some Examples

IPv4 address:
  * 127.0.0.1 = 0x7F000001 -> "diheskoa"
  
GUID:
  (hang on, let me generate a fresh GUID, reformatted into 32-bit chunks)
  * 799fb281-97924eaf-a483de8d-cfc7bf6b -> "esiareenmat-evyothode-antetoingleor-henosnoed"

IPv6 address:
  (randomly generating one of these too)
  * 6518:ec1d:838d:7582:0d24:b68c:c672:9e6c -> "deadieerausm:eonuirsose:aniemeaxeer:ottaualealal"
  
Latitude/Longitude

By mapping Latitude -/+ 90 -> 16-bits and Longitude from -/+ 180 -> 16-bits
you can represent a small patch of the Earth's surface with a single word -- with a resolution better than a few meters

  * 37.4663, -121.9750 = 0xb549, 0x2943 -> "bioboubu"


Room for improvement. Yes.

The more seeds I throw at this thing, the better they get on average.
It would be fun to roll out a language model to construct "pronouncable" words from a model, to use as seeds.
An alternative approach is to go deep into the mathematics of the CRC32 algorithm to get better and
minting new words (with a given CRC32) on-the-fly.


Data Availability
I have the whole dataset -- all 16 million seeds * 1 million permutations each with complexity scores
(but filtered for performance reasons to only words with a complexity score <=45)
I'm happy to share this, but at 3+ TB it's too big for me to host online.
Contact me and we can make arrangements to ship around hard drives or something.


Data Statistics
256 files, each containing words for 2^24 CRC32 hashes
Format:
    XXXXXXXX NN WORD\n
    where each field is separated by a single space
    where XXXXXXXX is a hex 32-bit number
    where NN is the word complexity score (lower is better)
    where WORD is the [a-z]+ word in question
    where \n is a single newline character

In total:
  * 123,206,094,434 distinct words
  * mapped to 4,294,967,296 hashes
  * consuming 3,216,005,781,219 bytes uncompressed

On average it would take harmonic_number(2^32) rounds to complete the collection
harmonic_number(2^32) = 22.8
number of rounds completed =  28.7

Final output consists of 256 files, each containing exactly 2^24 lines
Each about 85.4MiB, 7zipped