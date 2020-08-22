#!/bin/zsh

pause()
{
    echo "$*"; read -k1 -s
}
echo "What is a RUNME? Like README, but executable."
pause "If you've read this script and have about 5Tb disk available, hit any key to proceed. Otherwise Ctrl+C to exit."

## In practice, though, even the author generally uses this as a source to copy/paste from

## PREREQUISITES (Mac)
## coreutils:
brew install coreutils

## ..you might find useful: gnu parallel
brew install parallel
## Citation:
##  O. Tange (2018): GNU Parallel 2018, Mar 2018, ISBN 9781387509881,
##  DOI https://doi.org/10.5281/zenodo.1146014


## 1. Generate lots of random pronouncable seeds.
## And for subsequent parallel processing, split this file up into modest-sized pieces
python3 bin/genseeds.py
sort -u --random-sort lists/seeds.txt > lists/seeds_shuffled.txt
gsplit -a 2 -l 333000 -x --additional-suffix=.txt lists/seeds_shuffled.txt lists/seeds_

## 1.1 (aside)
# if you tweak genseeds.py to emit additional syllables or vowels, and you want to run the following
# steps on just the newly-available seeds, use the following command:
# comm -23 lists/new_seeds_sorted.txt lists/previous_seeds_sorted.txt > lists/seeds_diff.txt

## 2. The heavy lifting is done by this python script. It
##    a. massively expands the list of words by making multiple prefix/suffix permutations of each seed
##    b. Writes the hash into a uniquely named file in the right directory of work/
##       It is perfectly acceptable--and recommended--to have a bunch of these running in parallel
mkdir work
cd work
mkdir 0 1 2 3 4 5 6 7 8 9 a b c d e f
cd ..

## (No longer needed) Make sure you can open lots of files
sudo launchctl limit maxfiles 65536 200000
ulimit -n 65536
# and then...
python3 bin/compute.py lists/seed_words_00.txt #etc.

## 3.
## The above will have produced a LOT files in the format documented in README.md:

## Merge sort, round 1
LC_ALL=C
# Careful with this next one, unless you have a LOT of memory and IO bandwidth
parallel --eta sort -u {} -o {.}_sorted.txt ::: work/[0-9a-f]/seeds_??_?.txt
# conserve memory and IO bandwidth (bonus: write to external drive)
for f in work/?/seeds_??_?.txt; do sort -u -o /Volumes/8TbExt/humID/${f:h}/${f:t:r}_sorted.txt $f; done

## round 2, in each directory
for slice in 0 1 2 3 4 5 6 7 8 9 a b c d e f; do echo ${slice}; sort -u -m -o 04May_merge${slice}_sorted.txt seeds_??_${slice}_sorted.txt; done

## examine some statistics of generated & sorted data
python3 bin/stats.py

## 4. From this ocean we need to search for the 'most readable' word for each number 0-2^32


## 5. Check whether the database has at least one entry for every possible value 0 - 2^32 - 1.


## 6. Merge all the individual files into a master dictionary file with the One True identifier per index