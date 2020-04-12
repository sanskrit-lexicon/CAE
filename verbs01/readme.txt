
Analysis of cae verbs and upasargas, revised
This work was done in a temporary subdirectory (temp_verbs) of csl-orig/v02/cae/.

The shell script redo.sh reruns 5 python programs, from mwverb.py to preverb1.py.


* mwverbs
python mwverb.py mw ../../mw/mw.txt mwverbs.txt
#copy from v02/mw/temp_verbs
#cp ../../mw/temp_verbs/verb.txt mwverbs.txt
each line has 5 fields, colon delimited:
 k1
 L
 verb category: genuinroot, root, pre,gati,nom
 cps:  classes and/or padas. comma-separated string
 parse:  for pre and gati,  shows x+y+z  parsing prefixes and root

* mwverbs1.txt
python mwverbs1.py mwverbs.txt mwverbs1.txt
Merge records with same key (headword)
Also  use 'verb' for categories root, genuineroot, nom
and 'preverb' for categories pre, gati.
Format:
 5 fields, ':' separated
 1. mw headword
 2. MW Lnums, '&' separated
 3. category (verb or preverb)
 4. class-pada list, ',' separated
 5. parse. Empty for 'verb' category. For preverb category U1+U2+...+root

* cae_verb_filter.

python cae_verb_filter.py ../cae.txt  cae_verb_filter.txt

At some point in the past, markup was added to cae to identify verbs.
'<vlex type="root"/>'
The current analysis uses only this one pattern for verbs.

Total 1078 entries identified as verbs.

Format of file cae_verb_filter.txt:
;; Case 0001: L=21, k1=aMh, k2=aMh, code=V
;; Case 0003: L=291, k1=aNkay, k2=aNkay, code=V

* cae_verb_filter_map
python cae_verb_filter_map.py cae_verb_filter.txt mwverbs1.txt cae_verb_filter_map.txt

Get correspondences between cae verb spellings and
 - cae verb spellings
 - mw verb spellings

Format of cae_verb_filter_map.txt:
 Adds a field mw=xxx to each line of cae_verb_filter.txt,
indicating the MW root believed to correspond to the CAE root.
For example, aMSay in CAE is believed to correspond to aMS in MW.
;; Case 0001: L=21, k1=aMh, k2=aMh, code=V, mw=aMh
;; Case 0001: L=13, k1=aMSay, k2=aMSay, code=N, mw=aMS

In 6 cases, no correspondence could be found. These use 'mw=?'. For example:
;; Case 0129: L=7404, k1=kAkAy, k2=kAkAy, code=V, mw=?

* cae_preverb1.txt
python preverb1.py slp1 ../cae.txt cae_verb_filter_map.txt mwverbs1.txt cae_preverb1.txt
python preverb1.py deva ../cae.txt cae_verb_filter_map.txt mwverbs1.txt cae_preverb1_deva.txt

For each of the entries of cae_verb_filter_map.txt, the program analyzes the
text of CAE looking for upasargas.  An upsarga is identifed by the regex pattern
`'<div n="p">— *{#([a-zA-Z]+)#}` or the similar pattern `'<div n="p"> *{#([a-zA-Z]+)#}`

The number of upasargas found is reported on a line for the verb entry.
The first CAE verb entry has no upasargas:
;; Case 0001: L=21, k1=aMh, k2=aMh, code=V, #upasargas=0, mw=aMh (same)

The seventh CAE verb entry has 7 upasargas:
```
;; Case 0007: L=340, k1=ac, k2=ac, code=V, #upasargas=7 (3/4), mw=ac (same)
01        apa         ac                 apAc                 apAc yes apa+ac
02          A         ac                   Ac                   Ac yes A+ac
03         ud         ac                 udac                 udac no 
04         ni         ac                 nyac                 nyac no 
05       pari         ac               paryac               paryac no 
06         vi         ac                 vyac                 vyac yes vi+ac
07        sam         ac                samac                samac no 
```
For each upasarga, an attempt is made to match the prefixed verb to a
known MW prefixed verb.  
In this example, three prefixed forms were found as MW verbs (apAc, Ac, and vyac);
while 4 prefixed forms were not found as MW verbs.

Altogether, there are currently 3099 prefixed forms matched to MW verbs ('yes' cases), 
and 255 'no' cases.


