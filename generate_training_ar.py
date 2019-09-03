import sys
import random
from os import listdir
from os.path import isfile, join

# a list of sentence lists, where each sentence in the list contiguous
# all elements in the sentence are transcribed speech
utterances = list()

def segment_delimiter(sent):
    sent = sent.strip()
    if len(sent) < 200 or sent[0] == '<' or sent[:2] == '--' or sent[:3] == 'sr.' or sent[:4] == 'sra.':
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
    started = False
    count = 0
    if fname.endswith(".txt"):
        current = list()
        with open(sys.argv[1] + "/" + fname) as f:
            for sent in f:
                sent = sent.strip()
                if started:
                    if segment_delimiter(sent) or count > 10:
                        if len(current) > 0:
                            utterances.append(current)
                            current = list()
                        count = 0
                        started = False
                    else:
                        current.append(sent)
                        count += 1
                        total_sents += 1
                if not started:
                    if len(sent) > 200 and (sent[:3] == 'sr.' or sent[:4] == 'sra.'):
                        if ".-" in sent:
                            sent = sent[sent.index('.-') + 3:]
                        else:
                            if sent[-2:] == '..':
                                sent = ''
                        if sent:
                            current.append(sent)
                            count = 1
                            total_sents += 1
                        started = True
            if len(current) > 0:
                utterances.append(current)

with open("/tmp/ar_all.txt", "w") as f:
    for utt in utterances:
        f.write("\n".join(utt) + "\n\n")

sys.stderr.write("read {} segments with {} sents\n".format(len(utterances), total_sents))

show = random.randint(0, len(utterances))
for idx in range(50):
    sys.stderr.write("\n\n*********\n" + "\n".join(utterances[show + idx]))
sys.stderr.write('\n\n')

total = int(sys.argv[2])
rand = random.Random(42)

generated = 0
repeated = 0
seen = set()
while generated < total:
    generated += 1
    is_next = rand.random() < 0.5
    
    first_utt_idx = rand.randint(0, len(utterances) - 1)
    while len(utterances[first_utt_idx]) == 1:
        first_utt_idx = rand.randint(0, len(utterances) - 1)
    first_utt = utterances[first_utt_idx]
    first_sent = rand.randint(0, len(first_utt) - 2)
    first_id = "{} {}".format(first_utt_idx, first_sent)
    if first_id in seen:
        repeated += 1
    else:
        seen.add(first_id)
    
    if is_next:
        print("1 ", first_utt[first_sent], "|||", first_utt[first_sent + 1])
        second_id = "{} {}".format(first_utt_idx, first_sent + 1)
    else:
        second_utt_idx = rand.randint(0, len(utterances) - 1)
        while first_utt_idx == second_utt_idx:
            second_utt_idx = rand.randint(0, len(utterances) - 1)
        second_utt = utterances[second_utt_idx]
        second_sent = rand.randint(0, len(second_utt) - 1)
        print("0 ", first_utt[first_sent], "|||", second_utt[second_sent])
        second_id = "{} {}".format(second_utt_idx, second_sent)
        
    if second_id in seen:
        repeated += 1
    else:
        seen.add(second_id)
        
sys.stderr.write("repeated {} sents out of {}\n".format(repeated, total_sents))

                        
