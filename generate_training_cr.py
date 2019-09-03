import sys
import random
from os import listdir
from os.path import isfile, join

# a list of sentence lists, where each sentence in the list contiguous
# all elements in the sentence are transcribed speech
utterances = list()

def segment_start(sent):
    if (sent[:14] == ' EL PRESIDENTE' or sent[:14] == ' LA PRESIDENTA' or sent[:10] == ' DIPUTADO ' or sent[:10] == ' DIPUTADA ') and (sent[-2] == ':'):
        return True
    return False

def segment_delimiter(sent):
    sent = sent.strip()
    if len(sent) < 200 or sent[0] == '<' or sent[:2] == '--' or sent[:14] == ' EL PRESIDENTE' \
       or sent[:14] == ' LA PRESIDENTA' or sent[:10] == ' DIPUTADO ' or sent[:10] == ' DIPUTADA ':
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
        started = False
        with open(sys.argv[1] + "/" + fname) as f:
            for sent in f:
                if started:
                    if segment_delimiter(sent) or count > 10:
                        if len(current) > 0:
                            utterances.append(current)
                            current = list()
                        count = 0
                        started = False
                    else:
                        current.append(sent.strip())
                        count += 1
                        total_sents += 1
                if not started:
                    if segment_start(sent):
                        started = True
            if len(current) > 0:
                utterances.append(current)

sys.stderr.write("read {} segments with {} sents\n".format(len(utterances), total_sents))

show = random.randint(0, len(utterances))
with open("/tmp/cr_all.txt", "w") as f:
    for utt in utterances:
        f.write("\n".join(utt) + "\n\n")

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

                        
