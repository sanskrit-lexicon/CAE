#echo "remake mwverbs"
orig="../../../cologne/csl-orig/v02"
#python mwverb.py mw ${orig}/mw/mw.txt mwverbs.txt
#echo "remake mwverbs1"
#python mwverbs1.py mwverbs.txt mwverbs1.txt
mwverbs1="../../MWS/mwverbs/mwverbs1.txt"
echo "remake cae_verb_filter.txt"
python cae_verb_filter.py ${orig}/cae/cae.txt cae_verb_filter.txt
echo "remake cae_verb_filter_map.txt"
python cae_verb_filter_map.py cae_verb_filter.txt ${mwverbs1} cae_verb_filter_map.txt
echo "remake cae_preverb1.txt"
python preverb1.py slp1 ${orig}/cae/cae.txt cae_verb_filter_map.txt ${mwverbs1} cae_preverb1.txt
echo "remake cae_preverb1_deva.txt"
python preverb1.py deva ${orig}/cae/cae.txt cae_verb_filter_map.txt ${mwverbs1} cae_preverb1_deva.txt
