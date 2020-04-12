#-*- coding:utf-8 -*-
"""preverb1.py
 
 
"""
from __future__ import print_function
import sys, re,codecs
from parseheadline import parseheadline
import transcoder
transcoder.transcoder_set_dir('transcoder')

class Entry(object):
 Ldict = {}
 def __init__(self,lines,linenum1,linenum2):
  # linenum1,2 are int
  self.metaline = lines[0]
  self.lend = lines[-1]  # the <LEND> line
  self.datalines = lines[1:-1]  # the non-meta lines
  # parse the meta line into a dictionary
  #self.meta = Hwmeta(self.metaline)
  self.metad = parseheadline(self.metaline)
  self.linenum1 = linenum1
  self.linenum2 = linenum2
  #L = self.meta.L
  L = self.metad['L']
  if L in self.Ldict:
   print("Entry init error: duplicate L",L,linenum1)
   exit(1)
  self.Ldict[L] = self
  #  extra attributes
  self.marked = False # from a filter of markup associated with verbs
  self.marks = []  # verb markup markers, in order found, if any
  
def init_entries(filein):
 # slurp lines
 with codecs.open(filein,encoding='utf-8',mode='r') as f:
  lines = [line.rstrip('\r\n') for line in f]
 recs=[]  # list of Entry objects
 inentry = False  
 idx1 = None
 idx2 = None
 for idx,line in enumerate(lines):
  if inentry:
   if line.startswith('<LEND>'):
    idx2 = idx
    entrylines = lines[idx1:idx2+1]
    linenum1 = idx1 + 1
    linenum2 = idx2 + 1
    entry = Entry(entrylines,linenum1,linenum2)
    recs.append(entry)
    # prepare for next entry
    idx1 = None
    idx2 = None
    inentry = False
   elif line.startswith('<L>'):  # error
    print('init_entries Error 1. Not expecting <L>')
    print("line # ",idx+1)
    print(line.encode('utf-8'))
    exit(1)
   else: 
    # keep looking for <LEND>
    continue
  else:
   # inentry = False. Looking for '<L>'
   if line.startswith('<L>'):
    idx1 = idx
    inentry = True
   elif line.startswith('<LEND>'): # error
    print('init_entries Error 2. Not expecting <LEND>')
    print("line # ",idx+1)
    print(line.encode('utf-8'))
    exit(1)
   else: 
    # keep looking for <L>
    continue
 # when all lines are read, we should have inentry = False
 if inentry:
  print('init_entries Error 3. Last entry not closed')
  print('Open entry starts at line',idx1+1)
  exit(1)

 print(len(lines),"lines read from",filein)
 print(len(recs),"entries found")
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
 recs = [r for r in recs if r.cat == 'preverb']
 print(len(recs),"verbs returned from mwverbs")
 d = {}
 for rec in recs:
  k1 = rec.k1
  if k1 in d:
   print('init_mwverbs: Unexpected duplicate',k1)
  d[k1] = rec
 return recs,d


def unused_mark_entries_verb(entries,pwnonverbsd):
 for entry in entries:
  # first exclude known non-verbs
  k1 = entry.metad['k1']
  #if k1 in pwnonverbsd:
  # continue
  # might be a verb. look for upasarga pattern
  marks = []
  for iline,line in enumerate(entry.datalines):
   for m in re.finditer(u'<div n="p">—? *{#(.*?)#}',line):
    if entry.metad['L'] == '14791':print('check',m.group(0))
    upasarga = m.group(1)
    # add upasarga to the list of marks
    marks.append(upasarga)
    
  if len(marks) == 0:
   continue
  continue  # skip thi
  # remove cases where ONLY Desid.|Intens.|Caus. is present in marks
  marks = [x for x in marks if x not in ['Desid.','Intens.','Caus.']]
  if len(marks) > 0:
   """ Consider cases like 
     {#*marImfja#}¦ <lex>Adj.</lex> vom <ab>Intens.</ab> von {#marj#}.
    which should NOT be marked as verb
   """
   isverb = True  # tentatively
   line = entry.datalines[0]
   if re.search(r'¦ *<lex>',line):
    print(entry.metad['k1'],entry.metad['L'],' NOT A VERB')
    isverb = False #  No, mistaken identity!
   if isverb:
    entry.marked = True
    entry.marks = marks

def merge_marked_entries(entries):
 d = {}
 keys = []
 for entry in entries:
  if not entry.marked:
   continue
  k1 = entry.metad['k1']
  if k1 not in d:
   d[k1] = []
   keys.append(k1)
  d[k1].append(entry)
 entrylists = []
 for k1 in keys:
  entrylists.append(d[k1])
 return entrylists

def unused_find_upasarga_lines(entry):
 lines = entry.datalines
 outlines = []  # returned
 for iline,line in enumerate(lines):
  m = re.search(r'^<HI>[^ ]+ +[+] ',line)
  if m:
   outlines.append(line)
   lines[iline] = '*' + line
 return outlines

def unused_transcode_line(x,tranin,tranout):
 """ 
 """
 if re.search(r'^\[Page.*?\]$',x):
  return x
 parts = re.split(r'(<[^>]*>)',x)
 newparts = []
 for part in parts:
  if part.startswith('<'):
   newparts.append(part)
  else:
   newpart = transcoder.transcoder_processString(part,tranin,tranout)
   newparts.append(newpart)
 y = ''.join(newparts)
 return y

def yesno(flag):
 if flag:
  return 'yes'
 else:
  return 'no'

def write(fileout,recs,tranout):
 tranin = 'slp1'
 def transcode(x):
  return transcoder.transcoder_processString(x,tranin,tranout)
 n = 0
 nyes = 0
 nno = 0
 with codecs.open(fileout,"w","utf-8") as f:
  for irec,rec in enumerate(recs):
   entry = rec.entry
   upasargas = rec.upasargas
   preverbs = rec.preverbs
   mwpreverbs = rec.mwpreverbs
   mwpreverbs_found = rec.mwpreverbs_found
   mwpreverbs_parse = rec.mwpreverbs_parse
   k1 = entry.metad['k1']  
   L =  entry.metad['L']
   k2 = entry.metad['k2']
   code = rec.code
   if rec.mw== '?': #None:
    mw = '?'
   elif rec.mw== k1:
    mw = transcode(rec.mw)+ ' (same)'
   else:
    mw = transcode(rec.mw)+ ' (diff)'
   
   out1 = ';; Case %04d: L=%s, k1=%s, k2=%s, code=%s, #upasargas=%s, mw=%s' %(
    irec+1,L,transcode(k1),transcode(k2),code,len(upasargas),mw)
   if len(upasargas) == 0:
    f.write(out1+'\n')
    continue
   #add 1 more field to first line
   iyes = len([mwfound for mwfound in mwpreverbs_found if mwfound])
   ino  = len([mwfound for mwfound in mwpreverbs_found if not mwfound])
   out1 = ';; Case %04d: L=%s, k1=%s, k2=%s, code=%s, #upasargas=%s (%s/%s), mw=%s' %(
      irec+1,L,transcode(k1),transcode(k2),code,len(upasargas),iyes,ino,mw)
   outarr = []
   outarr.append(out1)
   # one line for each upasarga
   for iupa,upa in enumerate(upasargas):
    icase = iupa + 1
    preverb = preverbs[iupa]
    mwpreverb = mwpreverbs[iupa]
    mwfound = mwpreverbs_found[iupa]
    if mwfound:
     nyes = nyes + 1
     parse = mwpreverbs_parse[iupa]
    else:
     nno = nno + 1
     parse = ''
    outarr.append('%02d %10s %10s %20s %20s %s %s'%(
      icase,transcode(upa),transcode(k1),transcode(preverb),transcode(mwpreverb),yesno(mwfound),transcode(parse)))
   outarr.append(';')
   for out in outarr:
    f.write(out + '\n')
   n = n + 1
 print(n,"records written to",fileout)
 print(nyes,"mwpreverb spellings found")
 print(nno,"mwpreverb spellings NOT found")

class Pwgverb(object):
 def __init__(self,line):
  line = line.rstrip()
  self.line = line
  m = re.search(r'L=([^,]*), k1=([^,]*), k2=([^,]*), code=(.*), mw=(.*)$',line)
  self.L,self.k1,self.k2,self.code,self.mw = m.group(1),m.group(2),m.group(3),m.group(4),m.group(5)
  self.upasargas = []
  self.entry = None
  self.preverbs = []
  self.mwpreverbs = []
  self.mwpreverbs_found = []
  self.mwpreverbs_parse = []

def init_pwgverbs(filein):
 with codecs.open(filein,"r","utf-8") as f:
  recs = [Pwgverb(x) for x in f if x.startswith(';; Case')]
 print(len(recs),"records read from",filein)
 return recs

def find_entries(recs,entries):
 # dictionary for entries
 d = {}
 for entry in entries:
  d[entry.metad['L']]= entry
 # 
 for irec,rec in enumerate(recs):
  L = rec.L
  try:
   entry = d[L]
   rec.entry = entry
   entry.marked = True
  except:
   print('find_entries. bad L=',rec.L)
   print('record # ',irec+1)
   print('  line = ',rec.line)
   exit(1)

L_upasargas = {
 '5090':['pra', 'upapra', 'prati', 'sam', 'prasam'], 
 '5099':['aBi', 'pari', 'pra'], 
 '5160':['anu', 'aBi', 'ava', 'A', 'pari', 'pra', 'saMpra', 'vi', 'sam'], 
 '5436':['anu', 'aBi', 'ni', 'vi', 'sam'], 
 '7412':['anu', 'aBi', 'A', 'pratyA', 'samA', 'pra', 'prati'], 
 '8616':['ati', 'aByati', 'vyati', 'samati', 'aDi', 'anu', 'apa', 'aBi', 'samaBi', 'ava', 'A', 'aDyA', 'samA', 'ud', 
           'vyud', 'upa', 'samupa', 'ni', 'nis', 'aBinis', 'upanis', 'vinis', 'parA', 'pari', 'pra', 'saMpra', 
           'prati', 'anuprati', 'vi', 'anuvi', 'nirvi', 'sam', 'anusam', 'upasam'], 
 '8901':['ava', 'pra', 'vi', 'sam'], 
 '9285':['acCa', 'acCA', 'ati', 'aDi', 'samaDi', 'anu', 'samanu', 'antar', 'apa', 'vyapa', 'api', 'aBi', 'ava', 'A', 'aDyA', 
           'anvA', 'aByA', 'upA', 'samupA', 'nyA', 'paryA', 'pratyA', 'samA', 'ud', 'apod', 'aByud', 'pratyud', 
           'upa', 'aByupa', 'samupa', 'ni', 'upani', 'saMni', 'nis', 'vinis', 'parA', 'pari', 'pra', 'prati', 
           'vi', 'sam', 'aBisam', 'upasam'], 
 '9562':['ava', 'samava', 'A', 'pari'], 
 '9884':['A', 'upa', 'pari', 'pra', 'sam'], 
 '10043':['ava', 'A', 'pari', 'vi'], 
 '11331':['apa', 'aBi', 'ava', 'A', 'ud', 'nis', 'vinis', 'parA', 'pari', 'pra', 'prati', 'vi', 'sam'], 
 '12003':['A', 'ud', 'sam', 'pra'], 
 '13112':['nis', 'pari', 'vi', 'sam'], 
 '13485':['ava', 'nis', 'samava', 'A', 'vi', 'sam'], 
 '15138':['acCa', 'anu', 'aBi', 'pra', 'sam'], 
 '15471':['ava', 'A', 'upa', 'pra'], 
 '17237':['apa', 'vyapa', 'apA', 'vyapA', 'nis', 'parA', 'pra', 'prati', 'vi', 'sam', 'upasam'], 
 '19029':['anu', 'aBi', 'pari', 'pra', 'prati', 'sam'], 
 '23218':['ava', 'pari', 'sam'], 
 '25156':['upa', 'ni', 'pra', 'vi'], 
 '25227':['ni', 'pra', 'vi', 'sam'], 
 '25507':['pari', 'pra', 'vi'], 
 '25828':['upa', 'ni', 'sam'], 
 '25934':['acCa', 'ati', 'anu', 'apa', 'pratyapa', 'vyapa', 'aBi', 'ava', 'A', 'atyA', 'aByA', 'upA', 
            'aByupA', 'samupA', 'pratyA', 'samA', 'ud', 'pratyud', 'upa', 'aByupa', 'pratyupa', 'samupa', 'ni', 'nis', 'aBinis', 
            'vinis', 'pari', 'pra', 'anupra', 'aBipra', 'pratipra', 'saMpra', 'prati', 'vi', 'sam', 'anusam', 'aBisam', 'pratisam'], 
 '27335':['aBi', 'A', 'upA', 'samA', 'upa', 'samupa', 'vi', 'sam'], 
 '27515':['aBi', 'samaBi', 'A', 'pari'], 
 '27595':['anu', 'ava', 'A', 'upa', 'ni', 'pra', 'vi', 'sam'], 
 '27606':['ava', 'A', 'ud', 'upa', 'nis', 'pari', 'vi', 'sam', 'parisam'], 
 '27632':['ud', 'pari', 'pra', 'vi'], 
 '27650':['anu', 'aBi', 'A', 'upa', 'pari', 'pra', 'vipra', 'saMpra', 'prati', 'sam'], 
 '27658':['ava', 'A', 'nyA', 'vyA', 'nis', 'pari', 'pra', 'vipra', 'vi'], 
 '28319':['anu', 'samanu', 'aBi', 'vyA', 'upa', 'nis', 'vinis', 'sam'], 
 '28495':['aDi', 'anu', 'aBi', 'ni', 'pari', 'pra', 'prati', 'vi', 'sam'], 
 '28730':['aBi', 'samaBi', 'sam', 'aBisam'], 
 '30627':['anu', 'aBi', 'A', 'ud', 'upa', 'pari', 'sam'], 
 '30826':['aBi', 'ava', 'A', 'pra', 'prati', 'vi', 'sam'], 
 '31034':['ud', 'vi', 'sam'], 
 '31259':['pra', 'saMpra', 'vi', 'sam'], 
 '31832':['anu', 'aBi', 'pari', 'sam'], 
 '31846':['anuni', 'samanuni', 'aBini', 'upani', 'praRi', 'vini', 'saMni'], 
 '32819':['pari', 'vi', 'sam'], 
 '32838':['ati', 'aBi', 'samaBi', 'upa', 'pari', 'prati', 'vi', 'sam'], 
 '33554':['aBi', 'A', 'paryA', 'pratyA', 'samA', 'ud', 'proda', 'samud', 'ni', 'vini', 'nis', 'vinis', 'pra', 
            'aBipra', 'vi', 'ativi', 'aBivi', 'parivi'], 
 '33562':['ud', 'pra', 'vi', 'sam'], 
 '36593':['aBi', 'upa', 'pari'], 
 '37852':['aBi', 'A', 'upa', 'pra', 'sam'], 
 '37886':['aBi', 'ni', 'vini', 'saMni'], 
 '37977':['ati', 'anu', 'api', 'aBi', 'ava', 'aByava', 'upAva', 'vyava', 'samava', 'A', 'samA', 'ud', 
            'samud', 'upa', 'nis', 'pra', 'prati', 'vi', 'anuvi', 'aBivi', 'prativi', 'sam'], 
 '37987':['ati', 'aDi', 'samaDi', 'anu', 'samanu', 'apa', 'vyapa', 'aBi', 'ava', 'anvava', 'upAva', 'paryAva', 
            'pratyava', 'vyava', 'A', 'upodA', 'ud', 'upod', 'vyud', 'samud', 'upa', 'samupa', 'nis', 'vinis', 
            'pari', 'pra', 'prati', 'vi', 'sam', 'anusam', 'upasam'], 
 '38277':['aBi', 'nis', 'pra'], 
 '38313':['ava', 'paryava', 'samava', 'ud', 'upa', 'prati', 'vi', 'sam', 'aBisam', 'parisam', 'pratisam'], 
 '38352':['aBi', 'ava', 'samava', 'A', 'samA', 'upa', 'ni', 'pari', 'pra', 'vi', 'sam'], 
 '38618':['A', 'pari', 'pra', 'vi', 'sam'], 
 '38648':['aDi', 'pra', 'prati', 'vi', 'sam'], 
 '38851':['aBi', 'pari', 'aBipari', 'saMpari', 'vi', 'sam', 'aBisam'], 
 '39840':['ati', 'vyati', 'aDi', 'anu', 'apa', 'aBi', 'ava', 'aByava', 'vyava', 'A', 'anvA', 'aByA', 
            'udA', 'aByudA', 'praByudA', 'samudA', 'upA', 'samupA', 'upanyA', 'paryA', 'pratyA', 'vyA', 'anuvyA', 'aBivyA', 
            'pravyA', 'samA', 'anusamA', 'ud', 'aByud', 'samaByud', 'prod', 'pratyud', 'upa', 'samud', 'nis', 'vinis', 
            'pari', 'vipari', 'pra', 'anupra', 'saMpra', 'prati', 'vi', 'sam', 'upasam', 'pratisam'], 

 '9355':['ni', 'vi'],
 '15730':['ud'],
}

def find_upasargas(recs):
 nrec = 0
 nupa = 0
 for rec in recs:
  entry = rec.entry
  upasargas = []
  L=entry.metad['L']
  if L in L_upasargas:
   upasargas = L_upasargas[L]
  else:
   lines = entry.datalines
   for iline,line in enumerate(lines):
    for m in re.finditer(u'<div n="p">—? *{#(.*?)#}',line):
     upasarga = m.group(1)
     upasarga = upasarga.replace('/','') # remove accent. see 'car' a/cCa
     upasargas.append(upasarga)
  rec.upasargas = upasargas
  if len(upasargas) > 0:
   nrec = nrec + 1
   nupa = nupa + len(upasargas)
   # temporary logic to identify commas in upasargas
   if False:
    a = [u for u in upasargas if ',' in u]
    if len(a) > 0:
     print(entry.metaline)
     for line in lines:
      print(line)
     L=entry.metad['L']
     a = []
     for u in upasargas:
      if ',' in u:
       b = u.split(',')
       for v in b:
        v = v.strip()
        a.append(v)
      else:
       a.append(u)
      #b = ["'%s'"%u for u in a]
      b = a
      print("xx '%s':%s, " %(L,b))
     print()

 print(nupa,"upasargas found in",nrec,"entries")

def non_verb_upasargas(entries):
 nrec = 0
 nupa = 0
 ans = []
 for entry in entries:
  if entry.marked:  # skip verb entries
   continue
  upasargas = []
  lines = entry.datalines
  for iline,line in enumerate(lines):
   m = re.search(u'<div n="p">— {#([a-zA-Z]+)#}',line)
   if m:
    upasarga = m.group(1)
    upasargas.append(upasarga)
  #rec.upasargas = upasargas
  if len(upasargas) > 0:
   nrec = nrec + 1
   nupa = nupa + len(upasargas)
   entry.upasargas = upasargas
   ans.append(entry)

 print(nupa,"upasargas found in",nrec,"non-verb entries")
 fileout = 'preverb1_tempupa.txt'
 with codecs.open(fileout,'w','utf-8') as f:
  for ientry,entry in enumerate(ans):
   L = entry.metad['L']
   k1 = entry.metad['k1']
   upasargas = entry.upasargas
   out = ';; Case %04d: L=%s, k1=%s, #upasargas=%s' %(ientry+1,L,k1,len(upasargas))
   f.write(out+'\n')
  print(len(ans),"records written to",fileout)

sandhimap = {
 ('i','a'):'ya',
 ('i','A'):'yA',
 ('i','i'):'I',
 ('i','I'):'I',
 ('i','u'):'yu',
 ('i','U'):'yU',
 ('i','f'):'yf',
 ('i','F'):'yF',
 ('i','e'):'ye',
 ('i','E'):'yE',
 ('i','o'):'yo',
 ('i','O'):'yO',

 ('u','a'):'va',
 ('u','A'):'vA',
 ('u','i'):'vi',
 ('u','I'):'vI',
 ('u','u'):'U',
 ('u','U'):'U',
 ('u','f'):'vf',
 ('u','F'):'vF',
 ('u','e'):'ve',
 ('u','E'):'vE',
 ('u','o'):'vo',
 ('u','O'):'vO',

 ('a','a'):'A',
 ('a','A'):'A',
 ('A','a'):'A',
 ('A','A'):'A',
 
 ('a','i'):'e',
 ('A','i'):'e',
 ('a','I'):'e',
 ('A','I'):'e',
 
 ('a','u'):'o',
 ('A','u'):'o',
 ('a','U'):'o',
 ('A','U'):'o',
 
 ('a','f'):'Ar',
 ('A','f'):'Ar',
 ('a','e'):'e',
 ('d','s'):'ts',
 ('a','C'):'acC', # pra+Cad = pracCad
 ('A','C'):'AcC', # A + Cid = AcCid
 ('i','C'):'icC',
 ('d','q'):'qq',  # ud + qI
 ('d','k'):'tk',
 ('d','K'):'tK',
 ('d','c'):'tc',
 ('d','C'):'tC',
 ('d','w'):'tw',
 ('d','W'):'tW',
 ('d','t'):'tt',
 ('d','T'):'tT',
 ('d','p'):'tp',
 ('d','P'):'tP',
 ('d','s'):'ts',
 ('d','n'):'nn',

 ('i','st'):'izw',
 ('s','h'):'rh', # nis + han -> nirhan
 ('m','s'):'Ms', # sam + saYj -> saMsaYj
 ('m','S'):'MS',
 ('m','k'):'Mk',
 ('m','K'):'MK',
 ('m','c'):'Mc',
 ('m','C'):'MC',
 ('m','j'):'Mj',
 ('m','J'):'MJ',

 ('m','w'):'Mw',
 ('m','W'):'MW',
 ('m','t'):'Mt',
 ('m','T'):'MT',
 ('m','p'):'Mp',
 ('m','P'):'MP',

 ('m','v'):'Mv',
 ('m','l'):'Ml',
 ('m','r'):'Mr',
 ('m','y'):'My',
 ('m','n'):'Mn',
 
 ('s','k'):'zk', # nis + kf -> nizkf
 ('s','g'):'rg',
 ('s','G'):'rG',
 ('s','c'):'Sc',
 ('s','j'):'rj',
 ('s','q'):'rq',
 ('s','d'):'rd',
 ('s','D'):'rD',
 ('s','b'):'rb',
 ('s','B'):'rB',
 ('s','m'):'rm',
 ('s','n'):'rn',
 ('s','y'):'ry',
 ('s','r'):'rr',
 ('s','l'):'rl',
 ('s','v'):'rv',

 ('r','c'):'Sc',
 ('r','C'):'SC',
 ('d','l'):'ll',
 ('d','h'):'dD',
 ('d','S'):'cC',
 ('d','m'):'nm',

}
def join_prefix_verb(pfx,root):
 if pfx.endswith('ud') and (root == 'sTA'):
  return pfx[0:-2] + 'ut' + 'TA'  # ud + sTA = utTA
 if (pfx == 'saMpra') and (root in ['nad','nam','naS']):
  pfx = 'sampra'
  root = 'R' + root[1:]
  return pfx + root
 if (pfx == 'pra') and (root == 'nakz'):
  return 'pranakz' # odd, since mw has aBipraRakz
 pfx1,pfx2 = (pfx[0:-1],pfx[-1])
 root1,root2 = (root[0],root[1:])
 if (pfx2,root1) in sandhimap:
  return pfx1 + sandhimap[(pfx2,root1)] + root2
 if len(root) > 1:
  root1,root2 = (root[0:2],root[2:])
  if (pfx2,root1) in sandhimap:
   return pfx1 + sandhimap[(pfx2,root1)] + root2
 if root == 'i':
  if pfx == 'dus':
   return 'duri'
  if pfx == 'nis':
   return 'niri'
 if 'saMpra' in pfx:
  pfx = pfx.replace('saMpra','sampra')
  return pfx + root
 if  pfx.endswith(('pari','pra')) and root.startswith('n'):
  return pfx + 'R' + root[1:]  # pra + nad -> praRad
 if pfx.endswith('nis') and root.startswith(('a','I','u','U')):
  pfx = pfx.replace('nis','nir')
  return pfx + root
 ans = pfx + root
 d = {'duscar':'duScar'}
  
 if ans in d:
  ans = d[ans]
 return ans
mwpreverb_adjustments = {}

def adjust_mwpreverb(preverb,mwdict):
 #if preverb == 'sampranI':print('adjust_mwpreverb 1',preverb)
 if preverb in mwpreverb_adjustments:
  x = mwpreverb_adjustments[preverb]
  if x in mwdict:
   return x
 #if preverb == 'aByasUy':print('adjust_mwpreverb 2',preverb)
 if preverb in mwdict:
  return preverb # no adjustment needed
 if re.search(r'sa[mM]p',preverb):
  x = preverb.replace('saMp','samp')
  if x in mwdict:
   return x
  x = preverb.replace('samp','saMp')
  if x in mwdict:
   return x
  #return preverb
 if re.search(r'.*r.*n$',preverb):  #parAn -> paraR, etc
  x = preverb[0:-1]+'R'
  if x in mwdict:
   return x
 if re.search(r'r.R',preverb):
  x = re.sub(r'r(.)R',r'r\1n',preverb)
  if x in mwdict:
   return x

 if 'samh' in preverb:
  x = preverb.replace('samh','saMh')
  if x in mwdict:
   return x
 if 'utc' in preverb:
  x = preverb.replace('utc','ucc')
  if x in mwdict:
   return x
 if 'utC' in preverb:
  x = preverb.replace('utC','ucC')
  if x in mwdict:
   return x
 if 'udj' in preverb:
  x = preverb.replace('udj','ujj')
  if x in mwdict:
   return x
 if preverb.endswith('isad'):
  x = re.sub(r'isad$','izad',preverb)
  if x in mwdict:
   return x
 if re.search(r'is',preverb):
  x = re.sub(r'is',r'iz',preverb)
  if x in mwdict:
   return x
 if re.search(r'isT',preverb):
  x = re.sub(r'isT',r'izW',preverb)
  if x in mwdict:
   return x
 if re.search(r'us',preverb):
  x = re.sub(r'us',r'uz',preverb)
  if x in mwdict:
   return x
 if re.search(r'usT',preverb):
  x = re.sub(r'usT',r'uzW',preverb)
  if x in mwdict:
   return x
 if re.search(r'niss',preverb):
  x = re.sub(r'niss',r'niHs',preverb)
  if x in mwdict:
   return x
 if re.search(r'nisS',preverb):
  x = re.sub(r'nisS',r'niHS',preverb)
  if x in mwdict:
   return x
 if re.search(r'niszW',preverb):
  x = re.sub(r'niszW',r'niHzW',preverb)
  if x in mwdict:
   return x
 if re.search(r'nisv',preverb):
  x = re.sub(r'nisv',r'nirv',preverb)
  if x in mwdict:
   return x
 if re.search(r'udm',preverb):
  x = re.sub(r'udm',r'unm',preverb)
  if x in mwdict:
   return x
 if re.search(r'udh',preverb):
  x = re.sub(r'udh',r'udD',preverb)
  if x in mwdict:
   return x
 if re.search(r'sam[gGjJdDbByrlvSzs]',preverb):
  x = re.sub(r'sam([gGjJdDbByrlvSzs])',r'saM\1',preverb)
  if x in mwdict:
   return x
 if re.search(r'antar',preverb):
  x = re.sub(r'antar',r'antaH',preverb)
  if x in mwdict:
   return x
 if re.search(r'ra[rs]',preverb):
  x = re.sub(r'ra[rs]',r'ro',preverb)
  if x in mwdict:
   return x
 if re.search(r'acCa',preverb):
  x = re.sub(r'acCa',r'acCA',preverb)
  if x in mwdict:
   return x
 if re.search(r'paryAn',preverb):
  x = re.sub(r'paryAn',r'paryAR',preverb)
  if x in mwdict:
   return x
 if re.search(r'nirn',preverb):
  x = re.sub(r'nirn',r'nirR',preverb)
  if x in mwdict:
   return x
 if re.search(r'parAn',preverb):
  x = re.sub(r'parAn',r'parAR',preverb)
  if x in mwdict:
   return x
 if re.search(r'pran',preverb):
  x = re.sub(r'pran',r'praR',preverb)
  print('chk:',preverb,x)
  if x in mwdict:
   return x
 if re.search(r'st',preverb):
  x = re.sub(r'st',r'zw',preverb)
  if x in mwdict:
   return x
 if re.search(r'sT',preverb):
  x = re.sub(r'sT',r'zW',preverb)
  if x in mwdict:
   return x
 if re.search(r'zw',preverb):
  x = re.sub(r'zw',r'st',preverb)
  if x in mwdict:
   return x
 if re.search(r'zW',preverb):
  x = re.sub(r'zW',r'sT',preverb)
  if x in mwdict:
   return x
 if re.search(r'tst',preverb):
  x = re.sub(r'tst',r'tt',preverb)
  if x in mwdict:
   return x
 if re.search(r'tsT',preverb):
  x = re.sub(r'tsT',r'tT',preverb)
  if x in mwdict:
   return x
 if preverb == 'nissTA':
  x = 'niHzWA'
  if x in mwdict:
   return x
 if preverb == 'nisnA':
  x = 'nizRA'
  if x in mwdict:
   return x
 if preverb == 'saMparisvaYj':
  x = 'samparizvaYj'
  if x in mwdict:
   return x
 if preverb.endswith(('kf','df','pf')):
  x = preverb[0:-1]+'F'
  if x in mwdict:
   return x
 
 return preverb

def join_upasargas(recs,mwpreverbs_dict):
 for rec in recs:
  upasargas = rec.upasargas
  if len(upasargas) == 0:
   continue
  if rec.mw == '?':
   print(len(upasargas),'upasargas, but no mw root',rec.line)
   continue
  
  #mwrec = rec.mwrec
  k1 = rec.k1
  kmw = rec.mw
  rec.mwpreverbs = []
  rec.preverbs = []
  rec.mwpreverbs_found = []
  rec.mwpreverbs_parse = []
  for u in upasargas:
   pwg_preverb = join_prefix_verb(u,k1)
   if False and (k1 == 'asUy'):
    print('pwg',u,k1,pwg_preverb)
   rec.preverbs.append(pwg_preverb)
   mw_preverb0 = join_prefix_verb(u,kmw)
   mw_preverb = adjust_mwpreverb(mw_preverb0,mwpreverbs_dict)
   if False and (k1 == 'asUy'):
    print('mw',u,kmw,mw_preverb0,mw_preverb)
   rec.mwpreverbs.append(mw_preverb)
   if mw_preverb in mwpreverbs_dict:
    mwprerec = mwpreverbs_dict[mw_preverb]
    mwprerec.used = True
    rec.mwpreverbs_found.append(True)
    rec.mwpreverbs_parse.append(mwprerec.parse)
   else:
    rec.mwpreverbs_found.append(False)
    rec.mwpreverbs_parse.append(None)

def skipmw_unused(rec):
 if rec.line.endswith(('+kf','+BU')):
  return True
 if rec.k1 == rec.parse.replace('+',''):
  return True
 return False
def write_mw_unused(mwrecs):
 fileout = 'preverb1_temp_mw_unused.txt'
 n = 0
 with codecs.open(fileout,'w','utf-8') as f:
  for rec in mwrecs:
   if not rec.used:
    out = rec.line
    if skipmw_unused(rec):
     continue
    n = n + 1
    f.write(out+'\n')
 print(n,"records written to",fileout)

if __name__=="__main__": 
 tranout = sys.argv[1] # deva or slp1
 filein = sys.argv[2] #  xxx.txt (path to digitization of xxx
 filein1 = sys.argv[3] # pwg_verb_filter_map.txt
 filein2 = sys.argv[4] # mwverbs1
 fileout = sys.argv[5] # 
 entries = init_entries(filein)
 dhatus = init_pwgverbs(filein1)
 mwrecs,mwdict = init_mwverbs(filein2)  # mw preverbs
 find_entries(dhatus,entries)  # assign entry to each pwg verb record
 find_upasargas(dhatus)  # get list of upasargas
 non_verb_upasargas(entries)  # debug logic
 join_upasargas(dhatus,mwdict)
 write(fileout,dhatus,tranout)
 write_mw_unused(mwrecs)
