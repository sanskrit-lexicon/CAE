#-*- coding:utf-8 -*-
"""make_error1.py
 
 
"""
from __future__ import print_function
import sys, re,codecs
#from parseheadline import parseheadline
#import transcoder
#transcoder.transcoder_set_dir('transcoder')

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
  self.markcode = None
  self.markline = None

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

def lexflag(line):
 lexpatterns = [
   '¦ {%m.%}',  #masculine
   '¦ {%f.%}',  #feminine
   '¦ {%n.%}',  #neuter
   '¦ {%a.%}',  #adjective
   '¦ {%ind.%}',  # indeclineable
 ]
 for pattern in lexpatterns:
  if pattern in line:
   return True
 return False


class EngError(object):
 def __init__(self,line):
  line = line.rstrip('\r\n');
  self.line = line
  parts = line.split(':')
  assert len(parts) == 3
  self.L = parts[0]
  self.k1 = parts[1]
  self.words = parts[2].split(',') # these are candidate words

def init_errors(filein):
 with codecs.open(filein,"r","utf-8") as f:
  recs = [EngError(x) for x in f if not x.startswith(';')]
 print(len(recs),"records read from",filein)
 return recs

def entry_Cflines(lines):
 ans = []
 found = False
 for idx,line in enumerate(lines):
  # there 700+ lower case 'cf.' 
  # For this analysis, we capitalize
  line = line.replace(' cf.',' Cf.')
  # Similarly, add space 
  line = line.replace('>cf.','> Cf.')
  line = line.replace('>Cf.','> Cf.')
  if ' Cf.' in line:
   found = True
  if found:
   ans.append(line)
 return ans

def hyphenationPage(w,entry):
 ans = []
 if not w.endswith('Page'):
  return (False,'')
 w1 = w[0:-4]+'-'
 lines = entry.datalines
 L = entry.metad['L']
 k1 = entry.metad['k1']
 #if w == 'benePage':print('chk 1 Page:',w,L,k1)
 for idx,line in enumerate(lines):
  line = line.rstrip()
  if line.endswith(w1):
   line1 = lines[idx+1]
   #if w == 'benePage':print('chk 2 Page:',w,L,k1,line1)
   if not line1.startswith('[Page'):
    continue
    #print('hyphenationPage ERROR 1',w,L,k1,line)
    #return (False,'')
   line2 = lines[idx+2]
   if not line2.startswith('<>'):
    print('hyphenationPage ERROR 2',L,k1,line)
    return (False,'')
   m = re.search(r'^([a-z]+)',line2[2:])
   if m == None:
    print('hyphenationPage ERROR 3',L,k1,w,line2)
    return (False,'')
   w2 = m.group(1)
   return (True,w1+w2)
 return (False,'')

def hyphenationPage2(w,entry):
 # second part of a hyphenation, occurring after a Page break
 lines = entry.datalines
 L = entry.metad['L']
 k1 = entry.metad['k1']
 for idx,line in enumerate(lines):
  line = line.rstrip()
  m = re.search(r'([a-z]+)-$',line)
  if m:
   w1 = m.group(1)
   line1 = lines[idx+1]
   if not line1.startswith('[Page'):
    continue
   line2 = lines[idx+2]
   if not line2.startswith('<>'):
    print('hyphenationPage2 ERROR 2',L,k1,line)
    return (False,'')
   if line2.startswith('<>'+w):

    return (True,w1+w)
 return (False,'')

def hyphenation(w,entry):
 w1 = w+'-'
 lines = entry.datalines
 L = entry.metad['L']
 k1 = entry.metad['k1']
 #if w == 'benePage':print('chk 1 Page:',w,L,k1)
 for idx,line in enumerate(lines):
  line = line.rstrip()
  if line.endswith(w1):
   line2 = lines[idx+1]
   if not line2.startswith('<>'):
    print('hyphenation ERROR 2',L,k1,w,line2)
    return (False,'')
   m = re.search(r'^([a-z]+)',line2[2:])
   if m == None:
    print('hyphenation ERROR 3',L,k1,w,line2)
    return (False,'')
   w2 = m.group(1)
   return (True,w1+w2)
 return (False,'')

def hyphenated(w,entry):
 # w is formed by a hyphenated word being joined
 lines = entry.datalines
 L = entry.metad['L']
 k1 = entry.metad['k1']
 for idx,line in enumerate(lines):
  line = line.rstrip() 
  #m = re.search(r'([A-Za-z][a-z]*)-$',line)
  m = re.search(r'([A-Za-z]+)-$',line)
  if not m:
   continue
  w1 = m.group(1)
  line2 = lines[idx+1]
  if not line2.startswith('<>'):
   #print('hyphenated ERROR 2',L,k1,w,line2)
   #return (False,'')
   continue
  m = re.search(r'^([A-Za-zṇŚśṭ‘]+)',line2[2:])
  if m == None:
   print('hyphenated ERROR 3',L,k1,w,line2)
   return (False,'')
  w2 = m.group(1)
  if (w1+w2) == w:
   return (True,w1+'-'+w2)
 return (False,'')

def unused_entry_boldwords(entry):
 # all 'words' 
 words = []
 for idx,line in enumerate(entry.datalines):
  if idx == 0:
   # skip the headword, which is also Bold
   parts =  line.split('¦')
   line = parts[1]
  for m in re.finditer(r'{@(.*?)@}',line):
   bold = m.group(1)
   # remove punctuation
   bold = re.sub(r'[,;.]',' ',bold)
   a = re.split(r' +',bold)
   words = words + a
 return words

def nonboldAtEndofLine(w,entry):
 w1 = w+'-'
 for idx,line in enumerate(entry.datalines):
  if line.endswith(w1):
   return True
 return False

def nonboldAtBegofLine(w,entry):
 # lines start with <div n="lb"/>
 w1 = '<div n="lb"/>' + '-'+w
 for idx,line in enumerate(entry.datalines):
  if line.startswith(w1):
   return True
 return False

def AlternateHeadword(w,entry):
 line = entry.datalines[0]
 parts = line.split('¦')
 head = parts[0]
 return w in head

def analyze(errors,f):
 # mutate records (erec) in errors
 Ldict = Entry.Ldict
 for irec,erec in enumerate(errors):
  L = erec.L
  if L not in Ldict:
   print('analyze: bad L code',erec.line)
   continue
  entry = Ldict[L]
  L = erec.L
  k1 = erec.k1
  #boldwords = entry_words(entry)
  for w in erec.words:
   if re.search(r'^[A-Z]',w):
    f.write('Capitalized :%s %s %s\n'%(L,k1,w))
    erec.non_english.append(w)
    continue
   flag,w2 = hyphenationPage(w,entry)
   if flag:
    f.write('hyphenationPage: %s %s %s -> %s\n'%(L,k1,w,w2))
    erec.non_english.append(w)
    continue
   flag,w2 = hyphenationPage2(w,entry)
   if flag:
    f.write('hyphenationPage2: %s %s %s -> %s\n'%(L,k1,w,w2))
    erec.non_english.append(w)
    continue
   flag,w2 = hyphenation(w,entry)
   if flag:
    f.write('hyphenation: %s %s %s -> %s\n'%(L,k1,w,w2))
    erec.non_english.append(w)
    continue
   flag,w2 = hyphenated(w,entry)
   if flag:
    f.write('hyphenated: %s %s %s -> %s\n'%(L,k1,w,w2))
    erec.non_english.append(w)
    continue
   else:
    erec.maybe_english.append(w)
   """
   if ('-'+w) in boldwords:
    erec.non_english.append(w)
   elif ('-'+w+'-') in boldwords:  # hyphen at end of line
    erec.non_english.append(w)
   elif (w+'-') in boldwords:  # hyphen at end of line
    erec.non_english.append(w)
   elif (w) in boldwords:  # hyphen at end of line
    erec.non_english.append(w)
   elif nonboldAtEndofLine(w,entry):
    print('non-Bold-eol:',erec.L,erec.k1,w)
    erec.non_english.append(w)
   elif nonboldAtBegofLine(w,entry):
    print('non-Bold-bol:',erec.L,erec.k1,w)
    erec.non_english.append(w)
   elif AlternateHeadword(w,entry):
    print('Alternate HW:',erec.L,erec.k1,w)
    erec.non_english.append(w)
   else:
    erec.maybe_english.append(w)
   """
def write(fileout0,errors):
 f0 = codecs.open(fileout0,"w","utf-8")  # xxx_error1
 n0 = 0
 n1 = 0
 n01 = 0
 for erec in errors:
  L = erec.L
  k1 = erec.k1
  words = erec.words
  for w in words:
   out = '%s:%s:%s:' %(L,k1,w)
   f0.write(out+'\n')
   n0 = n0 + 1   
 f0.close()
 print(n0,'lines written to',fileout0)

if __name__=="__main__": 
 filein = sys.argv[1] #  xxx_error.txt
 fileout = sys.argv[2] # xxx_error1.txt

 errors = init_errors(filein)
 write(fileout,errors)
 #write(fileout,fileout1,errors)

