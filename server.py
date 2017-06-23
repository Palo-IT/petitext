# coding: utf-8
import pprint, json, time
from MonCoreNLP_13 import CoreNLP


pp = pprint.PrettyPrinter(indent=4)

full_annotator_list = ["tokenize", "cleanxml", "ssplit", "pos", "lemma", "ner", "regexner", "truecase", "parse",
                       "depparse", "dcoref", "relation", "natlog", "quote"]

full_annotator_list = ["ner", "pos", "lemma",  "depparse",  "relation"]

language ="fr"

cf = CoreNLP(url='http://localhost:9009',
             language = language,
             annotator_list=full_annotator_list,
             isPrint = False )
