# coding: utf-8
#!/usr/bin/env python

from nltk.stem.snowball import FrenchStemmer

class Mot:

    def __init__(self, label = "", role = "", ner = ""):
        self.label = label
        self.role = role
        self.ner = ner
        ##print(repr(label))
        stemmer = FrenchStemmer()
        self.lemma = stemmer.stem(label)
        
        
    
    def __str__(self):
        return "label = " + self.label + " role = " + self.role + " ner " + self.ner +"\n"

    def show_label(self):
        print(self.label)
    def show_role(self):
        print(self.role)
    def show_ner(self):
        print(self.ner)

if __name__ == "__main__" :
    #chaque personne est un homme ou une femme
    m1 = Mot (u"parents", "det", "0")
    #print(m1.lemma)
    m2 = Mot (u"parent", "nc", "0")
    #print(m2.lemma)
       
