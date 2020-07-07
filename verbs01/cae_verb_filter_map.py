#-*- coding:utf-8 -*-
"""cae_verb_filter_map.py
"""
from __future__ import print_function
import sys, re,codecs

class Caeverb(object):
 def __init__(self,line):
  line = line.rstrip()
  self.line = line
  m = re.search(r'L=([^,]*), k1=([^,]*), k2=([^,]*), code=(.*)$',line)
  self.L,self.k1,self.k2,self.code = m.group(1),m.group(2),m.group(3),m.group(4)
  self.pw=None
  self.mw = None
 
def init_caeverb(filein):
 with codecs.open(filein,"r","utf-8") as f:
  recs = [Caeverb(x) for x in f if x.startswith(';; Case')]
 print(len(recs),"records read from",filein)
 return recs

class Pwmw(object):
 def __init__(self,line):
  line = line.rstrip()
  self.line = line
  self.pw,self.mw = line.split(':')
 
def init_pw_mw(filein):
 with codecs.open(filein,"r","utf-8") as f:
  recs = [Pwmw(x) for x in f if not x.startswith(';')]
 print(len(recs),"records read from",filein)
 return recs

class MWVerb(object):
 def __init__(self,line):
  line = line.rstrip()
  self.line = line
  self.k1,self.L,self.cat,self.cps,self.parse = line.split(':')
  self.used = False

def init_mwverbs(filein):
 with codecs.open(filein,"r","utf-8") as f:
  recs = [MWVerb(x) for x in f]
 print(len(recs),"mwverbs read from",filein)
 #recs = [r for r in recs if r.cat == 'verb']
 #recs = [r for r in recs if r.cat in ['root','genuineroot']]
 #recs = [r for r in recs if r.cat == 'verb']
 print(len(recs),"verbs returned from mwverbs")
 d = {}
 for rec in recs:
  k1 = rec.k1
  if k1 in d:
   print('init_mwverbs: Unexpected duplicate',k1)
  d[k1] = rec
 return recs,d

map2mw_special = {

 'aNkay':'aNk',  # 
 'aNKay':'aNK',  # 
 'arTay':'arT',  # 
 'avataMsay':'avataMs',  # prev
 'avaDIray':'avaDIr',  # prev
 'iD':'inD',  # 
 'Ips':'Ap',  # desid.
 'Ilay':'Il',  # 
 'utkaRW':'utkaRWa',  # 
 'utsukay':'utsukAya',  # 
 'unmUl':'unmUla',  # 
 'Urjay':'Urj',  # 
 'ftIy':'ft',  # 
 'fd':'ard',  # 
 'kaTay':'kaT',  # 
 #'kAkAy':'kAkAy',  # not in mw
 'kIrtay':'kIrt',  # 
 'kutsay':'kuts',  # 
 'kurukurAy':'KuruKurAya',  #  k/K
 'kzA':'kzE',  # 
 'KaRqay':'KaRq',  # 
 'gaRay':'gaR',  # 
 'gantave':'gam',  # dat. inf.
 'gUrDay':'gUrD',  # 
 'gfBay':'gfBAya',  # 
 'graB':'grah',  # 
 'glA':'glE',  # 
 'culukay':'culukay',  # not mw. similar to culukIkf
 'cUrRay':'cUrR',  # 
 'Calay':'Cal',  # 
 'CA':'Co',  # 
 'jar':'jf',  # 
 'jiGAMs':'han',  # han desid.
 'jugups':'gup',  # desid. gup
 'jYIps':'jYA',  # desid. jYA
 'waNkay':'waNk',  # 
 'tandrAy':'tandr',  # 
 'taraMg':'taraMga',  # 
 'tf':'tF',  # 
 'trA':'trE',  # 
 'dIDi':'dIDI',  # 
 'dyutay':'dyut',  # 
 'drAGay':'drAG',  # 
 'DyA':'DyE',  # 
 'DrAj':'Draj',  # 
 'nigaqay':'nigaqaya',  # 
 'patay':'pat',  # causal
 #'patnIy':'patnIy',  # not mw. from patnI
 #'paty':'paty',  # not mw. from pati ?
 'pAlay':'pAl',  # 
 'piRqay':'piRq',  # 
 'pUray':'pF',  # 
 'pyA':'pyE',  # 
 'prakASay':'prakAS',  # preverb
 'prIRay':'prI',  # causal
 'bIBats':'bAD',  # desid. ?
 'Bfjj':'Brajj',  # 
 #'BogAy':'BogAy',  # not mw. prob. denom. from Boga (snake)
 'mantray':'mantr',  # 
 'miSray':'miSr',  # 
 'mfgay':'mfg',  # 
 'mfgy':'mfg',  # 
 'mokzay':'mokz',  # 
 'mlA':'mlE',  # 
 'mlecC':'mleC',  # 
 'rucay':'ruc',  # 
 'rUkzay':'rUkz',  # 
 'rUpay':'rUp',  # 
 'lakzay':'lakz',  # 
 'vanuz':'vanuzya',  # 
 'varRay':'varR',  # 
 'vasAy':'vas',  # ? causal
 'vAsay':'vas',  # causal
 'virUpay':'virUpay',  # causal of virUp (not in mw)
 'vIray':'vIrAya',  # 
 'vfzaRy':'vfzAya',  # by sense and similarity
 'vyA':'vye',  # 
 'vraRay':'vraR',  # 
 'Sat':'Sad',  # 
 'Sabday':'Sabd',  # 
 'SabdApay':'Sabd',  # 
 'SarD':'SfD',  # 
 'SA':'So',  # 
 'SIlay':'SIl',  # 
 'SuBay':'SuB',  # 
 'Sf':'SF',  # 
 'SyA':'SyE',  # 
 'Sruz':'Sru',  # ? vd. ?
 'SvA':'Svi',  # 
 'saBAjay':'saBAj',  # 
 'sA':'si',  # 
 'sAntvay':'sAntv',  # 
 'suKay':'suK',  # 
 'sUcay':'sUc',  # 
 'sUtray':'sUtr',  # 
 'skaBAy':'skaB',  # 
 'stenay':'sten',  # 
 'styA':'styE',  # 
 'sPuway':'sPuw',  # 
 'svargAy':'svargaya',  # 
 'hAr':'hAra',  # 
 #'hAs':'hAs',  #  ?
 ##'hel':'hel',  # 
 #'homay':'homay',  # not mw
  'gf':'gF', 
 'syad':'syand',  # mw prefixed forms use syand
 'spfD':'sparD',  # ditto
 'svar':'svf',  # ditto
 'raj':'raYj',  # ditto
 'dIDi':'DI',
 'ri':'rI',
 'svaj':'svaYj',
}


def map2mw(d,k1):
 if k1 in map2mw_special:
  return map2mw_special[k1]
 if k1 in d:
  return k1

 if k1.endswith('y'):
  k = k1 + 'a'
  if k in d:
   return k
 
 return '?'


def caemap(recs,mwd):
 for rec in recs:
  rec.mw = map2mw(mwd,rec.k1)

def write(fileout,recs):
 n = 0
 nomw = 0
 with codecs.open(fileout,"w","utf-8") as f:
  for rec in recs:
   n = n + 1
   line = rec.line
   # add mw
   out = '%s, mw=%s' %(line,rec.mw)
   if rec.mw == '?':
    nomw = nomw + 1
   f.write(out + '\n')
 print(n,"records written to",fileout)
 print(nomw,"records not yet mapped to mw")


if __name__=="__main__": 
 filein = sys.argv[1] #  cae_verb_filter.txt
 filein1 = sys.argv[2] # mwverbs1
 fileout = sys.argv[3]

 recs = init_caeverb(filein)
 mwverbrecs,mwverbsd= init_mwverbs(filein1)
 caemap(recs,mwverbsd)
 write(fileout,recs)
