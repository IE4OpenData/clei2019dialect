import sys
import pickle
import os

from collections import defaultdict, Counter
from operator import itemgetter

import numpy as np
import spacy

# usage:

# python extract_domain_terms bg_sentences fg_sentences prefix

# https://www.gakhov.com/articles/automatic-terms-extraction-for-domain-specific-corpora.html

def main():
    prefix = sys.argv[3]
    print("prefix:", prefix)
    
    nlp = spacy.load('es_core_news_sm')

    # background model
    uni_bg = dict()
    bi_bg = dict()

    if os.path.isfile("bg.pickle"):
        uni_bg, bi_bg = pickle.load(open("bg.pickle", "rb"))
    else:
        print("BG:", sys.argv[1])
        with open(sys.argv[1], "r") as bg:
            for line in bg:
                line = line.strip()
                line = line[1:]
                first, second = line.split("|||")
                for current in [ first, second ]:
                    doc = nlp(current)
                    for sent in doc.sents:
                        prev = [('filler', 'FILLER', 'NONE'), ('filler', 'FILLER', 'NONE'),]
                        for tok in sent:
                            uni = (tok.text, tok.lemma_.lower(), tok.tag_)
                            bi = ("~".join([ prev[-1][0], uni[0] ]), "~".join([ prev[-1][1], uni[1] ]), "~".join([ prev[-1][2], uni[2] ]))
                            uni_bg[ uni ] = uni_bg.get(uni, 0) + 1
                            bi_bg[ bi ] = bi_bg.get(bi, 0) + 1
                            prev.append(uni)
        with open("bg.pickle", "wb") as pf:
            pickle.dump([ uni_bg, bi_bg ], pf )

    # foreground model
    uni_fg = dict()
    bi_fg = dict()

    if os.path.isfile(prefix + "fg.pickle"):
        uni_fg, bi_fg = pickle.load(open(prefix + "fg.pickle", "rb"))
    else:
        print("FG:", sys.argv[2])
        with open(sys.argv[2], "r") as fg:
            for line in fg:
                line = line.strip()
                line = line[1:]
                first, second = line.split("|||")
                for current in [ first, second ]:
                    doc = nlp(current)
                    for sent in doc.sents:
                        prev = [('filler', 'FILLER', 'NONE'), ('filler', 'FILLER', 'NONE'),]
                        for tok in sent:
                            uni = (tok.text, tok.lemma_.lower(), tok.tag_)
                            bi = ("~".join([ prev[-1][0], uni[0] ]), "~".join([ prev[-1][1], uni[1] ]), "~".join([ prev[-1][2], uni[2] ]))
                            uni_fg[ uni ] = uni_fg.get(uni, 0) + 1
                            bi_fg[ bi ] = bi_fg.get(bi, 0) + 1
                            prev.append(uni)
        with open(prefix + "fg.pickle", "wb") as pf:
            pickle.dump([ uni_fg, bi_fg ], pf )

    # clean full forms on patterns
    uni_lemma_fg = dict()
    uni_lemma_bg = dict()
    bi_lemma_fg = dict()
    bi_lemma_bg = dict()

    lemma_exs = dict()
    lemmas_exs = dict()

    for lemma_table, uni_table in [ (uni_lemma_fg, uni_fg), (uni_lemma_bg, uni_bg) ]:
        for key, count in uni_table.items():
            word, lemma, pos = key
            if len(lemma) > 3 and pos.startswith("NOUN"):
                lemma_table[lemma] = lemma_table.get(lemma, 0) + count
                if lemma not in lemma_exs:
                    lemma_exs[lemma] = set()
                lemma_exs[lemma].add(word)

    all_uni = set(uni_lemma_fg.keys())
    all_uni.update(uni_lemma_bg.keys())
    print("Found {:,} unigrams\n".format(len(all_uni)))
                
    uni_specificity = list()
    for lemma in all_uni:
        score = uni_lemma_fg.get(lemma, 1) * 1.0 / uni_lemma_bg.get(lemma, 1)
        if lemma == 'patronal' or lemma == 'zapatilla':
            print(lemma, score)
        uni_specificity.append( (score, lemma) )
    uni_specificity = sorted(uni_specificity, reverse=True)
    for idx, entry in enumerate(uni_specificity):
        if entry[1] == 'patronal':
            print(entry, idx)
    uni_specificity = uni_specificity[:10000]
    good_lemmas = set(map(lambda x:x[1], uni_specificity))
    
                
    for lemma_table, bi_table in [ (bi_lemma_fg, bi_fg), (bi_lemma_bg, bi_bg) ]:
        for key, count in bi_table.items():
            words, lemmas, poss = key
            lemmass = lemmas.split('~')
            pos = poss.split('~')
            if (((pos[0].startswith("NOUN") and pos[1].startswith("NOUN")) or
                (pos[0].startswith("ADJ") and pos[1].startswith("NOUN")) or
                (pos[0].startswith("NOUN") and pos[1].startswith("ADJ"))) and
                (lemmass[0] in good_lemmas or lemmass[1] in good_lemmas)):
                lemma_table[lemmas] = lemma_table.get(lemmas, 0) + count
                if lemmas not in lemmas_exs:
                    lemmas_exs[lemmas] = set()
                lemmas_exs[lemmas].add(words)
                
    bi_specificity = list()

    all_bi = set(bi_lemma_fg.keys())
    all_bi.update(bi_lemma_bg.keys())

    print("Found {:,} FG unigrams\nFound {:,} FG bigrams\n".format(len(uni_lemma_fg), len(bi_lemma_fg)))
    print("Found {:,} BG unigrams\nFound {:,} BG bigrams\n".format(len(uni_lemma_bg), len(bi_lemma_bg)))
    print("Found {:,} bigrams\n".format(len(all_bi)))

    for lemmas in all_bi:        
        bi_specificity.append( (bi_lemma_fg.get(lemmas, 1) * 1.0 / bi_lemma_bg.get(lemmas, 1), lemmas) )

    bi_specificity = sorted(bi_specificity, reverse=True)
    bi_specificity = bi_specificity[:10000]

    with open(prefix + "uni_scores.txt", "w") as unif:
        for score, lemma in uni_specificity:
            if score < 3.0:
                break
            unif.write("{}\t{}\t{}\n".format(score, lemma, lemma_exs[lemma]))
    with open(prefix + "bi_scores.txt", "w") as bif:
        for score, lemmas in bi_specificity:
            if score < 3.0:
                break
            bif.write("{}\t{}\t{}\n".format(score, lemmas, lemmas_exs[lemmas]))
                

if __name__ == '__main__':
    main()
