import random
import sys
import numpy as np

from keras.models import Model
from keras.models import load_model
from keras.layers import Dense, Activation, Input, Dropout
from keras import optimizers
import keras
import tensorflow as tf

if len(sys.argv) != 4:
    sys.stderr.write("Usage: coherence_classifier3 <train data txt> <bert features npy> <output file prefix>\n");
    sys.exit(0)

# load training data
X = np.load(sys.argv[2])
y = np.zeros( (X.shape[0],) )
with open(sys.argv[1]) as f:
    pos = 0
    for line in f:
        y[pos] = int(line[0])
        pos += 1

rand = random.Random(42)
is_train = np.zeros( (X.shape[0],) )
train_size = 0
for i in range(X.shape[0]):
    this_is_train = rand.random() > 0.2
    is_train[i] = 1 if this_is_train else 0
    if this_is_train:
        train_size += 1

X_train = np.zeros( (train_size, X.shape[1]) )
y_train = np.zeros( (train_size,) )

X_test = np.zeros( (X.shape[0] - train_size, X.shape[1]) )
y_test = np.zeros( (X.shape[0] - train_size, ) )

tr_idx = 0
te_idx = 0
for i in range(X.shape[0]):
    if is_train[i]:
        X_train[tr_idx,:] = X[i, :]
        y_train[tr_idx] = y[i]
        tr_idx += 1
    else:
        X_test[te_idx,:] = X[i, :]
        y_test[te_idx] = y[i]
        te_idx += 1

def custom_gelu(x):
        return 0.5 * x * (1 + tf.tanh(tf.sqrt(2 / np.pi) * (x + 0.044715 * tf.pow(x, 3))))
keras.utils.get_custom_objects().update({'custom_gelu': Activation(custom_gelu)})

bert = Input(shape=(3072,), name='bert_feats')
dense1 = Dense(64, activation=custom_gelu, name='dense1')(bert)
dense1 = Dropout(0.75)(dense1)
coherent = Dense(1, activation='sigmoid', name='coherent')(dense1)
model = Model(inputs=bert, outputs=coherent)
model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

print(model.summary())
print(X_train.shape, X_test.shape)
model.fit(X_train, y_train,
          validation_data=(X_test, y_test), epochs=30, batch_size=32)

#
# serialize model to JSON
#
model_json = model.to_json()
with open(sys.argv[3] + ".json", "w") as json_file:
    json_file.write(model_json)
# serialize weights to HDF5
model.save_weights(sys.argv[3] + ".h5")
print("Saved model to disk")
