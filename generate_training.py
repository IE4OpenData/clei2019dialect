import sys
import random
from os import listdir
from os.path import isfile, join

docs = list()

def segment_delimiter(sent):
    sent = sent.strip()
    if len(sent) < 200 or sent[0] == '<' or sent[:2] == '--' or sent[:2] == 'sr.' or sent[:3] == 'sra.':
        return True
    digit = 0
    for ch in sent:
        if ch >= '0' and ch <= '9':
            digit += 1
    if digit > 0.5 * len(sent):
        return True
    return False

total_sents = 0
for fname in listdir(sys.argv[1]):
    if fname.endswith(".txt"):
        current = list()
        with open(sys.argv[1] + "/" + fname) as f:
            for sent in f:
                sent = sent.strip()
                if segment_delimiter(sent):
                    if len(current) > 0:
                        docs.append(current)
                        current = list()
                else:
                    current.append(sent)
                    total_sents += 1
            if len(current) > 0:
                docs.append(current)

sys.stderr.write("read {} segments with {} sents\n".format(len(docs), total_sents))

show = random.randint(0, len(docs))
for idx in range(20):
    sys.stderr.write("\n\n*********\n" + "\n".join(docs[show + idx]))
sys.stderr.write('\n\n')

total = int(sys.argv[2])
rand = random.Random(42)

generated = 0
repeated = 0
seen = set()
while generated < total:
    generated += 1
    is_next = rand.random() < 0.5
    
    first_doc_idx = rand.randint(0, len(docs) - 1)
    while len(docs[first_doc_idx]) == 1:
        first_doc_idx = rand.randint(0, len(docs) - 1)
    first_doc = docs[first_doc_idx]
    first_sent = rand.randint(0, len(first_doc) - 2)
    first_id = "{} {}".format(first_doc_idx, first_sent)
    if first_id in seen:
        repeated += 1
    else:
        seen.add(first_id)
    
    if is_next:
        print("1 ", first_doc[first_sent], "|||", first_doc[first_sent + 1])
        second_id = "{} {}".format(first_doc_idx, first_sent + 1)
    else:
        second_doc_idx = rand.randint(0, len(docs) - 1)
        while first_doc_idx == second_doc_idx:
            second_doc_idx = rand.randint(0, len(docs) - 1)
        second_doc = docs[second_doc_idx]
        second_sent = rand.randint(0, len(second_doc) - 1)
        print("0 ", first_doc[first_sent], "|||", second_doc[second_sent])
        second_id = "{} {}".format(second_doc_idx, second_sent)
        
    if second_id in seen:
        repeated += 1
    else:
        seen.add(second_id)
        
sys.stderr.write("repeated {} sents out of {}\n".format(repeated, total_sents))

                        
