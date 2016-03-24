import sys
import numpy as np
from collections import namedtuple

def scrapemmision(filename):
    emmision = {}
    Element = namedtuple("Element", ["tag", "word"])
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if len(line) != 0:
                lsplit = line.split(" ")
                if lsplit[1] == "WORDTAG":
                    if Countword.has_key(lsplit[3]):
                        Countword[lsplit[3]] = Countword[lsplit[3]] + int(lsplit[0])
                    else:
                        Countword[lsplit[3]] = int(lsplit[0])
                        
                    if Counttag.has_key(lsplit[2]):
                        Counttag[lsplit[2]] = Counttag[lsplit[2]] + int(lsplit[0])
                    else:
                        Counttag[lsplit[2]] = int(lsplit[0])
                    

    Countword['_RARE_'] = 0
    for word in Countword:
        if Countword[word] < 5 and word != '_RARE_':
            Countword['_RARE_'] = Countword['_RARE_'] + Countword[word];
            Countword[word] = 0;
                        
    with open(filename, 'r') as g:
        for line in g:
            line = line.strip()
            if len(line) != 0:
                lsplit = line.split(" ")
                if lsplit[1] == "WORDTAG":
                    if Countword[lsplit[3]] < 5:
                        lsplit[3] = "_RARE_"
                    if emmision.has_key(Element(lsplit[2],lsplit[3])):
                        emmision[Element(lsplit[2],lsplit[3])] = emmision[Element(lsplit[2],lsplit[3])] + (float(lsplit[0])/Counttag[lsplit[2]])
                    else:
                        emmision[Element(lsplit[2],lsplit[3])] = (float(lsplit[0])/Counttag[lsplit[2]])

    return emmision

def scrape3gram(filename):
    threegram = {}
    threegramElement = namedtuple("threegramElement", ["first", "second", "third"])
    twogramElement = namedtuple("twogramElement", ["first", "second"])
    Countgram = {}
    with open(filename, 'r') as f:
        for line in f:
            #raw_input('Enter your input:')
            line = line.strip()
            if len(line) != 0:
                lsplit = line.split(" ")
                if lsplit[1] == "3-GRAM":
                    if Countgram.has_key(twogramElement(lsplit[2],lsplit[3])):
                        Countgram[twogramElement(lsplit[2],lsplit[3])] = Countgram[twogramElement(lsplit[2],lsplit[3])] + int(lsplit[0])
                    else:
                        Countgram[twogramElement(lsplit[2],lsplit[3])] = int(lsplit[0])
    
    with open(filename, 'r') as g:
        for line in g:
            line = line.strip()
            if len(line) != 0:
                lsplit = line.split(" ")
                if lsplit[1] == "3-GRAM":
                    threegram[threegramElement(lsplit[2],lsplit[3],lsplit[4])] = (float(lsplit[0])/Countgram[twogramElement(lsplit[2],lsplit[3])])
    return threegram

  
def viterbi(words):
    lensen = len(words)
    word = [words[x] for x in range(len(words))]
    for i in range(len(words)):
        if Countword.has_key(words[i]):
            if Countword[words[i]] < 5:
                word[i] = "_RARE_"
        else:
            word[i] = "_RARE_"
    pimatrix = [[[0 for x in range(numtags)] for x in range(numtags)]for x in range(lensen + 1)]
    bp = [[[0 for x in range(numtags)] for x in range(numtags)]for x in range(lensen + 1)]
    for i in range(numtags):
        for j in range(numtags):
            pimatrix[0][i][j] = 0
    pimatrix[0][numtags-2][numtags-2] = 1

    y = [0 for x in range (lensen+1)]

    for k in range(1,lensen+1):
        for u in range(numtags):
            for v in range(numtags):
                pimatrix[k][u][v] = 0
                arg = 0
                for w in range(numtags):
                    temp = 0
                    if threegram.has_key(threegramElement(tags[w],tags[u],tags[v])) and emmision.has_key(Element(tags[v],word[k-1])):
                        temp = pimatrix[k-1][w][u]*threegram[threegramElement(tags[w],tags[u],tags[v])]*emmision[Element(tags[v],word[k-1])]
                        if(temp > pimatrix[k][u][v]):
                            bp[k][u][v] = w
                            pimatrix[k][u][v] = temp

    curr = 0
    for u in range(numtags):
        for v in range(numtags):
            if threegram.has_key(threegramElement(tags[u],tags[v],'STOP')):
                temp = pimatrix[lensen][u][v]*threegram[threegramElement(tags[u],tags[v],'STOP')]
                if(temp > curr):
                    curr = temp
                    y[lensen-1] = u
                    y[lensen] = v
                    
    for k in list(reversed(range(1,lensen-1))):
        y[k] = bp[k+2][y[k+1]][y[k+2]]
    
    return y 
    

Element = namedtuple("Element", ["tag", "word"])
Countword = {}
Counttag = {}   

Element = namedtuple("Element", ["tag", "word"])
threegramElement = namedtuple("threegramElement", ["first", "second", "third"]) 
emmision = scrapemmision("train.counts")
threegram = scrape3gram("train.counts")

tags = ["PROPN","NUM","ADJ","NOUN","VERB","ADV","X","INTJ","SYM","AUX","ADP","CONJ","PART","PUNCT","SCONJ","PRON","DET","*","STOP"]
numtags = len(tags)

filetestname = "test.words"
fo = open("output.tags", 'w')
tokens = []
with open(filetestname, 'r') as f:
    for line in f:
        line = line.strip()

        if len(line) != 0:
            tokens.append(line)
        else:
            z = viterbi(tokens)
            for i in range(1,len(z)):
                fo.write(  tokens[i-1] + " " + tags[z[i]] + "\n")
            fo.write("\n")
            tokens = []
