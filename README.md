# humID

Humane GUIDs and other identifiers:

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
swear word...say the middle four letter of a nine-letter made-up word are a horrible slur in Urdu.
2) Trademarks. What if someone comes along with a cease-and-desist letter, demanding to remove an entry?

Either of these events would require changing the global lookup table, possibly invalidating all the existing stored
data, URLs, etc. encoded with it. No good. But there's an even more insidious problem.

3) What I consider pronouncable isn't universal. I don't find certain European  spellings "easily" pronouncable, but my friends in
Deutchland might disagree. I wouldn't even know how to evaluate "pronouncable" words in CJK languages.

So we can't rely on a global lookup table.

Instead, it uses a deliberately-simple hash function. *Any* sequence of UTF-8 bytes can be hashed down to 32 bits. There's even a well-known CRC32 algorithm (as used in ZIP files) with implementations in Python in many other languages.

Let's do this. For every integer in the 32-bit space, let's find a conveniently short 'word'.

Translating from word -> int is simply running CRC32. Translating from int -> word is trickier. We need a huge lookup table.

In this initial implementation, words use only [a-z]. Identifiers longer than 32 bits can string together multiple words with spaces or other separator characters.

def word_hash(s):
    crc = binascii.crc32(bytes(s, 'utf-8'))
    return crc & 0xffffff

If you want to make your own dictionary, go for it. It could use CJK langauges, or emoji, or nothing but offensive
words. Knock yourself out. Just maybe this would be the basis for a decent password generator.

TODO: Examples

IPv4 address:
  * 127.0.0.1 ->
  
GUID:
  (hang on, let me generate a fresh GUID)
  * 799f b281 9792 4eaf a483 de8d cfc7 bf6b ->

(hmm. This might be a good password generator too)

IPv6 address:

Latitude/Longitude

By mapping Latitude 0-360 -> bottom 16-bits and Latitude from +/- 90 -> top 16-bits
you can represent a small patch of the Earth's surface with a single short word -- with a precision better than a few meters




