#!/bin/bash

ORIG_DIR="../hgg12"


for d in R V RR VV RV; do
  cp ${ORIG_DIR}/$d/epemZH2gg.run $d/
  cp ${ORIG_DIR}/$d/epemZH2gg.warmup.run $d/
  cp ${ORIG_DIR}/$d/submit_* $d/
done

