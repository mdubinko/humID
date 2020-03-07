#!/bin/zsh

pause()
{
    echo "$*"; read -k1 -s
}
echo "What is a RUNME? Like README, but executable."
pause "If you've read this script, hit any key to proceed. Otherwise Ctrl+C to exit."

## PREREQUISITES
## coreutils: brew install coreutils
## ..you might find useful gnu parallel: brew install parallel
## Citation:
##  O. Tange (2018): GNU Parallel 2018, Mar 2018, ISBN 9781387509881,
##  DOI https://doi.org/10.5281/zenodo.1146014


## 1. Generate lots of random pronouncable seeds.
## And for later parallel processing, split this file up into 8ish pieces
## or use the pre-made seeds_N.txt, where N ranges between 0 and 9
#python3 bin/genseeds.py
#sort -u lists/seeds.txt > lists/seeds_sorted.txt
#gsplit -a 1 -l 500000 -x --additional-suffix=.txt lists/seeds_sorted.txt lists/seeds_

## 1.1 (aside)
# if you modify genseeds.py to emit additional syllables or vowels, and you want to run the following
# steps on just the newly-available seeds, use the following command:
# comm -23 lists/new_seeds_sorted.txt lists/previous_seeds_sorted.txt > lists/seeds_diff.txt

## 2. The heavy lifting is done by this python script. It
##    a. massively expands the list of words by making multiple prefix/suffix permutations of each seed
##    b. Writes the hash into a uniquely named file in the right directory of db/
##       It is perfectly acceptable--and recommended--to have a bunch of these running in parallel
#mkdir db
#cd db
#mkdir 0 1 2 3 4 5 6 7 8 9 a b c d e f
#cd ..
## Make sure you can open lots of files
#sudo launchctl limit maxfiles 65536 200000
#ulimit -n 65536
#python3 bin/compute.py lists/seed_words_0.txt #etc.

## 3.
## The above will have produced a LOT files in this format:
## XXXXXXXX NN word
## where XXXXXXXX is a hex-formatted 32-bit number
## where NN is the word complexity score (lower is better)
## where word is the [a-z]+ word in question


## 4. From this ocean we need to search for the 'most readable' word for each number 0-2^32


## 5. Check whether the database has at least one entry for every possible value 0 - 2^32 - 1.


## 6. Merge all the individual files into a master dictionary file with the One True identifier per index