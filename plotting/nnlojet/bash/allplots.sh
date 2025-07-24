#!/bin/bash

python3 makeplot5.py --path combined/Final --input LO.mH.dat NLO.mH.dat NNLO.mH.dat --output mH.pdf --enable-ratio --denominator NNLO --add-logo
python3 makeplot5.py --path combined/Final --input LO.m12.dat NLO.m12.dat NNLO.m12.dat --output m12.pdf --enable-ratio --denominator NNLO --add-logo
python3 makeplot5.py --path combined/Final --input LO.m12low.dat NLO.m12low.dat NNLO.m12low.dat --output m12low.pdf --enable-ratio --denominator NNLO --add-logo
python3 makeplot5.py --path combined/Final --input LO.mZ.dat NLO.mZ.dat NNLO.mZ.dat --output mZ.pdf --enable-ratio --denominator NNLO --add-logo
python3 makeplot5.py --path combined/Final --input LO.ej1.dat NLO.ej1.dat NNLO.ej1.dat --output ej1.pdf --add-logo
python3 makeplot5.py --path combined/Final --input LO.ej2.dat NLO.ej2.dat NNLO.ej2.dat --output ej2.pdf --add-logo
