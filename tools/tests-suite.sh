#!/bin/bash

for t in 1 4
do
  for m in 1 5 25 50
  do
    for r in 1 2 3 4 5
    do
      rm -rf ./strpe-testing
      /usr/bin/env python test_strpe.py -n 100 -t $t -m $m -s
      /usr/bin/env python parse_test_strpe.py -n 100 -m $m > ./results/n100t${t}m${m}-${r}.txt
    done
  done
done
