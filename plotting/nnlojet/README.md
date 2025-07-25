Plotting scipts for NNLOJET standard data files.
Standard use
>>> make <obs> ORDER=LO, NLO, NNLO (default NNLO)
or just
>>> make all
Observables with "_log" in the name are automatically plotted
with a log scale on the x axis. 

Alternatively, use bash scripts in the bash/ folder.

Note: config/ folder is required by the makeplot5 scripts.

>>> nnlojet-combine.py 
to combine different run/contribs. 
Declare folder structure in combine.ini.


