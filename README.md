# humID

Human-friendly GUIDs and other identifiers:

Suppose you had to read an arbitrary IPv6 address over the phone. How difficult would that be?

How about a 160 bit Ethereum address?

Or suppose your webapp uses GUIDs internally, but they end up exposed in a URL.
How could you ensure 'human readable' URLs?

That's where this project comes in.

My initial thought was to assemble a list of 256 short, easily-pronounceable words, assigning one to each number 0-255.
Then you could replace each byte in an identifier with a word. Say 192.168.10.20 to spam.eggs.foo.bar.
But that doesn't get you much. Why not a dictionary of 65536 words? Then we can map two bytes to each word.


And 'words' don't necessarily have to appear in the dictionary--just be pronounceable. So perhaps we can get up to 24 bits of information in a 'dictionary' of 16 million words.

So far so good, but if the project depends on a single global dictionary, there's bound to be problems.
1) There's always the possibility of an inappropriate word appearing in the lookup table. Maybe not even a classic
swear word...say the middle four letter of a nine-letter made-up word are a horrible slur in Urdu.
2) Trademarks. What if someone comes along with a cease-and-desist letter, demanding to remove an entry?

Either of these events would require changing the global lookup table, possibly invalidating all the existing stored
data, URLs, etc. encoded with it. No good. But there's an even more insidious problem.

3) What I consider pronouncable isn't universal. I don't find certain European  spellings "easily" pronouncable, but my friends in
Deutchland might disagree. I wouldn't even know how to evaluate "pronouncable" words in CJK languages.

So we can't rely on a global lookup table.

Instead, it uses a deliberately-simple hash function. *Any* sequence of UTF-8 bytes can be hashed down to 24 bits.
To make it useful, I can provide a default lookup table (by feeding *lots* of words into the hash and keeping
a reverse lookup table, then weeding it down to the most pronounceable entry for each of the 16 million keys.)

TODO: this paragraph is 16-bit-specific. Rework. So suppose an existing identifier included "superhero" (representing binary data 0x388D) but for one of the reasons
given above, that word had to be removed. An equivalent is "sublimely" representing the same bits.
Completely interchangable. All an implementation needs to translate words to data is to implement the hash function.

The hash function is CRC32 (as used in the ZIP format), discarding from the final answer all but the lowest 24 bits.
This is well known, well-supported, and simple to implement. Most programming langauges already have it in a library.

Python implementation

import binascii

def word_hash(s):
    crc = binascii.crc32(bytes(s, 'utf-8'))
    return crc & 0xffffff


= The Default Dictionary =

The default dictionary has the following characteristics:
1) It uses only the characters [a-z]. No digits, capital letters, whitespace, or punctuation.
2) It's based on /usr/share/dict/words plus some randomly-generated pseudowords and word-like prefixes and suffixes.
3) A bit of manual tweaking to make it better and more readable

If you want to make your own dictionary, go for it. It could use CJK langauges, or emoji, or nothing but offensive
words. Knock yourself out.

= Specific Use Cases =

Since the default dictionary avoids punctuation, it makes possible some common cases.

TODO: IPv4 address: You can use a dot to separate two words, each of which represents two octets.
192.168.0.1 -> udusk.gymnasium
1.1.1.1 -> aft.aft
Google 172.217.6.78 -> reversication.oast

TODO: GUID: You can use - to separate eight words, for a total of 128 bits.
(hang on, let me generate a fresh GUID)
799f b281 9792 4eaf a483 de8d cfc7 bf6b -> trouca-coastwise-udens-howl-quino-ymq-complacent-kovil

(hmm. This might be a good password generator too)

TODO: IPv6 address: You can use : to separate eight words.
As with numeric IPv6 addresses, you can use :: to replace long strings of 0s.
Otherwise, it's almost the same as GUID representation.

Latitude/Longitude

By mapping Latitude 0-360 -> 0-16 million and Latitude from +/- 90 -> 0-65535
you can represent a small patch of the Earth's surface with two words with a precision better than a few meters




