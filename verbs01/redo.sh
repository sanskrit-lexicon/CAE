echo "remake mwverbs"
python mwverb.py mw ../../mw/mw.txt mwverbs.txt
echo "remake mwverbs1"
python mwverbs1.py mwverbs.txt mwverbs1.txt
echo "remake cae_verb_filter.txt"
python cae_verb_filter.py ../cae.txt cae_verb_filter.txt
echo "remake cae_verb_filter_map.txt"
python cae_verb_filter_map.py cae_verb_filter.txt mwverbs1.txt cae_verb_filter_map.txt
echo "remake cae_preverb1.txt"
python preverb1.py slp1 ../cae.txt cae_verb_filter_map.txt mwverbs1.txt cae_preverb1.txt
echo "remake cae_preverb1_deva.txt"
python preverb1.py deva ../cae.txt cae_verb_filter_map.txt mwverbs1.txt cae_preverb1_deva.txt
