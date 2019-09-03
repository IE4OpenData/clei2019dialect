# clei2019dialect

Source code for "Impact of Spanish Dialect in Deep Learning Next
Sentence Predictors", CLEI Panama, Duboue (2019).

Preprint: http://duboue.net/papers/CLEI2019dialect.pdf


Generating the models is a three step process:

1. Extract the pairs of contiguous and non-contiguous utterances.
2. Obtain batch BERT embeddings for the [CLS] token are obtained by
   running the pairs from the first step.
3. Train a FC network using the labels from the first step and the
   embeddings from the second step
   
From there, it is possible to cross-evlauate the models and extract
dialect specific terminology.



## Setup

This code assumes a Linux, bash and python 3. Perl is also needed for
the terminology extraction. The provided requirements.txt contains a
superset of the needed Python packages. The data files make heavy use
of symlinks, so you will need a file system that supports them (or a
version of tar that resolves them on extraction).

Download the data files from
http://duboue.net/download/clei2019dialect.tar.bz2 (330Mb) and extract
them in the current folder.

Alternatively, it is possible to download
http://duboue.net/download/clei2019dialect-full.tar.bz2 (992Mb) which
contains the source files and the trained models.

On a fresh copy of https://github.com/google-research/bert (tested on
commit 0fce551b55caabcfba52c61e18f34b541aef186a), copy
extract_features2.py in this folder into that folder.

Fetch multi_cased_L-12_H-768_A-12.zip, uncompress it in a folder of
your choosing and set BERT_MODEL_DIR to that folder. For example /tmp/bert_model:

```
export BERT_MODEL_DIR=/tmp/bert_model
```

The training data contains sentence-split (using spaCy) versions the
AR and CR documents. See at the bottom of these README if you want to
re-generate those files.



## Extract the pairs of contiguous and non-continguous utterances

```
python generate_training_ar.py data/sentences/train/ar 100000 > data/ar_100k.txt
python generate_training_ar.py data/sentences/test/ar 1000 > data/ar_test_10k.txt
python generate_training_cr.py data/sentences/train/cr 100000 > data/cr_100k.txt
python generate_training_cr.py data/sentences/test/cr 1000 > data/cr_test_10k.txt
python generate_training.py data/wiki_sample 100000 > data/wiki_100k.txt
```


## Generating embeddings

Obtaining batch BERT embeddings for the [CLS] token are obtained by
running the pairs from the first step.

Remember to copy extract_features2.py on a fresh copy of
https://github.com/google-research/bert (tested on commit
0fce551b55caabcfba52c61e18f34b541aef186a).

The following commands are executed in the BERT folder:

Set folders appropriately:

```
export BERT_MODEL_DIR=/path/to/multi_cased_L-12_H-768_A-12
export DATA_DIR=/path/to/data
```

```
python extract_features2.py  --input_file=$DATA_DIR/cr_train_100k.txt   --output_file=$DATA_DIR/cr_100k.npy   --vocab_file=$BERT_MODEL_DIR/vocab.txt   --bert_config_file=$BERT_MODEL_DIR/bert_config.json   --init_checkpoint=$BERT_MODEL_DIR/bert_model.ckpt   --layers=-1,-2,-3,-4   --max_seq_length=128   --batch_size=8 --do_lower_case=False
python extract_features2.py  --input_file=$DATA_DIR/ar_train_100k.txt   --output_file=$DATA_DIR/ar_100k.npy   --vocab_file=$BERT_MODEL_DIR/vocab.txt   --bert_config_file=$BERT_MODEL_DIR/bert_config.json   --init_checkpoint=$BERT_MODEL_DIR/bert_model.ckpt   --layers=-1,-2,-3,-4   --max_seq_length=128   --batch_size=8 --do_lower_case=False
python extract_features2.py  --input_file=$DATA_DIR/wiki_100k.txt   --output_file=$DATA_DIR/wiki_100k.npy   --vocab_file=$BERT_MODEL_DIR/vocab.txt   --bert_config_file=$BERT_MODEL_DIR/bert_config.json   --init_checkpoint=$BERT_MODEL_DIR/bert_model.ckpt   --layers=-1,-2,-3,-4   --max_seq_length=128   --batch_size=8 --do_lower_case=False
python extract_features2.py  --input_file=/path/to/cr_test_10k.txt   --output_file=$DATA_DIR/cr_test_10k.npy   --vocab_file=$BERT_MODEL_DIR/vocab.txt   --bert_config_file=$BERT_MODEL_DIR/bert_config.json   --init_checkpoint=$BERT_MODEL_DIR/bert_model.ckpt   --layers=-1,-2,-3,-4   --max_seq_length=128   --batch_size=8 --do_lower_case=False
python extract_features2.py  --input_file=$DATA_DIR/ar_test_10k.txt   --output_file=$DATA_DIR//ar_test_10k.npy   --vocab_file=$BERT_MODEL_DIR/vocab.txt   --bert_config_file=$BERT_MODEL_DIR/bert_config.json   --init_checkpoint=$BERT_MODEL_DIR/bert_model.ckpt   --layers=-1,-2,-3,-4   --max_seq_length=128   --batch_size=8 --do_lower_case=False
```

This will produce large serialized numpy arrays with the [CLS] embedding (about 2Gb in size each).




## Training the models

Using the labels from the first step and the embeddings from the second step


```
python coherence_classifier3.py data/ar_100k.txt data/ar_100k.npy model/ar_model
python coherence_classifier3.py data/cr_100k.txt data/cr_100k.npy model/cr_model
python coherence_classifier3.py data/wiki_100k.txt data/wiki_100k.npy model/wiki_model
```

This produces model_prefix.h5 and model_prefix.json as usual with keras.



## Cross evaluate

```
python coherence_eval.py data/cr_test_10k.txt data/cr_test_10k.npy model/wiki_model results/wiki_on_cr_test.tsv
python coherence_eval.py data/cr_test_10k.txt data/ar_test_10k.npy model/wiki_model results/wiki_on_ar_test.tsv
python coherence_eval.py data/ar_test_10k.txt data/ar_test_10k.npy model/cr_model results/cr_on_ar_test.tsv
python coherence_eval.py data/cr_test_10k.txt data/cr_test_10k.npy model/cr_model results/cr_on_cr_test.tsv
python coherence_eval.py data/cr_test_10k.txt data/cr_test_10k.npy model/ar_model results/ar_on_cr_test.tsv
python coherence_eval.py data/ar_test_10k.txt data/ar_test_10k.npy model/ar_model results/ar_on_ar_test.tsv
```

Note that the models are unstable. See below for code to evaluate five variations.



## Terminology extraction

```
python extract_domain_terms.py data/wiki_100k.txt data/ar_100k.txt data/ar_
python extract_domain_terms.py data/wiki_100k.txt data/cr_100k.txt data/cr_
./joint_terms.pl |grep -c AR
./joint_terms.pl |grep -c CR
./joint_terms.pl |grep -c BOTH
./joint_terms.pl |grep BOTH
```


## Stability

The training of the coherence model can be repeated five times:

```
for r in `seq 5`; do python coherence_classifier3.py data/ar_100k.txt data/ar_100k.npy model/ar_model$r; done
for r in `seq 5`; do python coherence_eval.py data/cr_test_10k.txt data/cr_test_10k.npy mode/wiki_model$r /tmp/deleteme.tsv 2>&1 |perl -ne 'print if m/^(p?rec|f1)/'; done|perl -e '%k=();while(<STDIN>){chomp;($m,$v)=split(/=/,$_);$v=int($v*10000+0.5)/100;push@{$k{$m}},$v;};print"metric\tmean\tboun\tmax\tmin\t".join("\t",(1..5))."\n";foreach$k(keys %k){@v=@{$k{$k}};$max=$v[0];$min=$max;$avg=0;foreach$v(@v){$avg+=$v/@v;if($max<$v){$max=$v};if($min>$v){$min=$v}};$bound = $avg - $min; if($max - $avg > $bound){$bound = $max-$avg}; $bound = int($bound*100+0.5)/100;print "$k\t$avg\t$bound\t$max\t$min\t".join("\t",@v)."\n"}' > results/wiki_on_cr5.tsv
```

(the other variations ommitted for clarity.)




## Appendix: Regenerating the sentence-separated files.

Download the source files from
http://duboue.net/download/clei2019dialect-full.tar.bz2 .

Install spaCy and the model es_core_news_sm.

```
rm -rf data/sentences
mkdir data/sentences
mkdir data/sentences/{ar,cr}
./split.sh data/text/ar data/sentences/ar > data/ar_key.txt
./split.sh data/text/cr data/sentences/cr > data/cr_key.txt
```

Split into training and test

```
mkdir data/sentences/{train,test}
mkdir data/sentences/{train,test}/{ar,cr}
cd data/sentences
cd ar
ls > ../../ar_splitted.ids
cd ..
cd cr
ls > ../../ar_splitted.ids
cd ../..
cd data
sort -R ar_splitted.ids > ar_splitted.ids,shuffled
sort -R cr_splitted.ids > cr_splitted.ids,shuffled
split --lines=341 ar_splitted.ids,shuffled ar_splitted.ids.
mv ar_splitted.ids.{aa,train}
mv ar_splitted.ids.{ab,test}
split --lines=2423 cr_splitted.ids,shuffled cr_splitted.ids.
cr_splitted.ids.{aa,train}
cr_splitted.ids.{ab,test}
cd sentences/train/ar
for f in `cat ../../../ar_splitted.ids.train`; do ln -s ../../ar/$f .; done
cd ../cr
for f in `cat ../../../cr_splitted.ids.train`; do ln -s ../../cr/$f .; done
cd ../../test
cd ar
for f in `cat ../../../ar_splitted.ids.test`; do ln -s ../../ar/$f .; done
cd ../cr
for f in `cat ../../../cr_splitted.ids.test`; do ln -s ../../cr/$f .; done
```

The wiki_sample is the output of part of the Spanish wikipedia as run
through https://github.com/bwbaugh/wikipedia-extractor, then split
using the same sentence splitter code.



## Citing

If you find this code and data useful, please cite:

```
@inproceedings{ duboue2019dialect,
  title     = {Impact of Spanish Dialect in Deep Learning Next Sentence Predictors},
  author    = {Duboue, Pablo Ariel},
  booktitle = {Conferencia Latinoamericana de Informatica (CLEI)},
  address   = {Panama City, Panama},
  year      = {2019}
}
```
