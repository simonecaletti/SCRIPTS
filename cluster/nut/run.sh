#!/bin/bash

export OMP_NUM_THREADS=1

let i=1
while [ $i -lt 25 ]; do
  nohup NNLOJET -run epemZH2gg.run -iseed $i &
  let i=i+1
done
