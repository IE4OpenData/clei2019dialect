#!/bin/bash

# usage: split.sh indir (e.g. data/text/ar) outdir  (e.g., data/sentences/ar) > key.txt
INDIR=$1
OUTDIR=$2

C=1
for f in $INDIR/*
do
    echo $C $f
    cat $f | python sentence_splitter.py > $OUTDIR/$C.txt
    C=$(( $C + 1 ))
done
