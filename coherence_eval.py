import random
import sys
import numpy as np

from keras.models import Model
from keras.models import load_model
from keras.layers import Dense, Activation, Input
from keras import optimizers
import keras
import tensorflow as tf

def custom_gelu(x):
        return 0.5 * x * (1 + tf.tanh(tf.sqrt(2 / np.pi) * (x + 0.044715 * tf.pow(x, 3))))
keras.utils.get_custom_objects().update({'custom_gelu': Activation(custom_gelu)})


if len(sys.argv) != 5:
    sys.stderr.write("Usage: coherence_eval <test data txt> <bert features npy> <model file prefix> <output file>\n");
    sys.exit(0)

# load test data
X = np.load(sys.argv[2])
y = np.zeros( (X.shape[0],) )
texts = list()
with open(sys.argv[1]) as f:
    pos = 0
    for line in f:
        y[pos] = int(line[0])
        pos += 1
        texts.append(line[2:].strip())

with open(sys.argv[3] + ".json") as json_file:
    model_json = json_file.read()
    
from keras.models import model_from_json
model = model_from_json(model_json)
model.load_weights(sys.argv[3] + '.h5')
model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

print(model.summary())
print(X.shape, y.shape)

yhat = model.predict(X)

tp = 0
tn = 0
fp = 0
fn = 0
with open(sys.argv[4], "w") as out:
    for i, proba in enumerate(yhat):
        predicted = proba > 0.5
        if y[i] == 0:
           if predicted:
               fp += 1
           else:
               tn += 1
        else:
           if predicted:
               tp += 1
           else:
               fn += 1
        out.write("{}\t{}\t{}\t{}\n".format(int(y[i]),1 if predicted else 0, proba, texts[i]))


sys.stderr.write("tp={} fp={}\nfn={} tn={}\n".format(tp,fp,fn,tn))

pre = tp * 1.0 / (tp+fp)
rec = tp * 1.0 / (tp+fn)
f1 = 2 * pre * rec / (pre + rec)

sys.stderr.write("prec={}\nrec={}\nf1={}\n".format(pre,rec,f1))

