#!/usr/bin/perl -w

use strict;

open(A,"data/ar_uni_scores.txt");
my%top_a = ();
my%a = ();
while(<A>){
    chomp;
    my@b=split(/\t/,$_);
    if(scalar(%a) < 1000){
        $top_a{$b[-2]} = 1;
    }
    $a{$b[-2]} = $b[0]."=".$b[-1];
}
close(A);

open(C,"data/cr_uni_scores.txt");
my%top_c = ();
my%c = ();
while(<C>){
    chomp;
    my@b=split(/\t/,$_);
    if(scalar(%c) < 1000){
        $top_c{$b[-2]} = 1;
    }
    $c{$b[-2]} = $b[0]."=".$b[-1];
}
close(C);

foreach my$k(keys %top_a) {
    my$s = $a{$k};
    $s =~ s/\=.*//;
    print ("$s\tAR\t$k\t".$a{$k}."\n") unless $c{$k};
    if ($c{$k}){
        my$ss = $c{$k};
        $ss =~ s/\=.*//;
        if($s > 10 * $ss){
            print ("$s\tAR\t$k\t".$a{$k}."\t".$c{$k}."\n");
        }elsif($ss > 10 * $s){
            print ("$ss\tCR\t$k\t".$a{$k}."\t".$c{$k}."\n");
        }else{
            $s = ($s + $ss) / 2.0;        
            print ("$s\tBOTH\t$k\t".$a{$k}."\t".$c{$k}."\n");
        }
    }
}

foreach my$k(keys %top_c){
    my$s = $c{$k};
    $s =~ s/\=.*//;
    print ("$s\tCR\t$k\t".$c{$k}."\n") unless $a{$k};
    if ($a{$k} && !$top_a{$k}){
        my$ss = $a{$k};
        $ss =~ s/\=.*//;
        if($s > 10 * $ss){
            print ("$s\tCR\t$k\t".$c{$k}."\t".$a{$k}."\n");
        }else{
            $s = ($s + $ss) / 2.0;
            print ("$s\tBOTH\t$k\t".$a{$k}."\t".$c{$k}."\n");
        }
    }
}
