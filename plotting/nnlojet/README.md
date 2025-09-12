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

Update 12.09.2025
- makeplot5.py is deprecated. We use makeplot6.py now. 
- gallery.py can be used to visualize all the produced plot in the browser -> make gallery
- added config_scripts folder with bash scripts to modify config files
- Makefile now includes: make convert, make move and make rebin
- Added recsale_dat_file.py to compute c quark distribution from b quark ones
- Added sum_dat_files.py to compute total distribution summing over b, c and g ones
- Added rebinning_selected_obs.py to rebin distribution for selected observables

The general strategy is always to compute new distribution and print in the NNLOJET output format. 
Then we can use makeplot6.py to plot them.
All the workflow is described in the Makefile.

TO DO: 
- write compute_jet_rates.py script to compute jet rates from yij distributions