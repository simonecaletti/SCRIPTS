# Makefile with flexible input files depending on ORDER

PYTHON = python3
DATADIR = combined/Final
OUTDIR = plots

NAMES = \
  mZ mZ_excl2 dR_l12 dR_l12_excl2 mH_all mH_all_excl2 mH_12 mH_12_excl2 dR_j12 dR_j12_excl2 ej1 ej1_excl2 \
  ej2 ej2_excl2 min_dR_lpj min_dR_lmj min_dR_lpj_excl2 min_dR_lmj_excl2 \
  y12 y12_log y23_log y34_log

# Total cross section full inclusive
bbLO=3.6828205
bbNLO=4.43100509
bbNNLO=4.56900509


  .PHONY: all clean $(NAMES)

  # Observable-specific options
  mZ_OPTS = "--histogram --add-logo --enable-ratio --denominator NLO.mZ.dat --normalize $(bbLO) $(bbNLO) $(bbNNLO)"
  mZ_excl2_OPTS = "--histogram --add-logo --enable-ratio --denominator NLO.mZ_excl2.dat --normalize $(bbLO) $(bbNLO) $(bbNNLO)"
  dR_l12_OPTS = "--histogram --add-logo --enable-ratio --denominator NLO.dR_l12.dat --normalize $(bbLO) $(bbNLO) $(bbNNLO)"
  dR_l12_excl2_OPTS = "--histogram --add-logo --enable-ratio --denominator NLO.dR_l12_excl2.dat --normalize $(bbLO) $(bbNLO) $(bbNNLO)"
  mH_all_OPTS = "--add-logo --enable-ratio --denominator NLO.mH_all.dat --normalize $(bbLO) $(bbNLO) $(bbNNLO)"
  mH_all_excl2_OPTS = "--add-logo --enable-ratio --denominator NLO.mH_all_excl2.dat --normalize $(bbLO) $(bbNLO) $(bbNNLO)"
  mH_12_OPTS = "--add-logo --enable-ratio --denominator NLO.mH_12.dat --normalize $(bbLO) $(bbNLO) $(bbNNLO)"
  mH_12_excl2_OPTS = "--add-logo --enable-ratio --denominator NLO.mH_12_excl2.dat --normalize $(bbLO) $(bbNLO) $(bbNNLO)"
  dR_j12_OPTS = "--histogram --add-logo --place-text 4 --enable-ratio --denominator NLO.dR_j12.dat --normalize $(bbLO) $(bbNLO) $(bbNNLO)"
  dR_j12_excl2_OPTS = "--histogram --add-logo --place-text 4 --enable-ratio --denominator NLO.dR_j12_excl2.dat --normalize $(bbLO) $(bbNLO) $(bbNNLO)"
  ej1_OPTS = "--histogram --add-logo --place-text 3 --enable-ratio --denominator NLO.ej1.dat --normalize $(bbLO) $(bbNLO) $(bbNNLO) --rescale 125.09"
  ej1_excl2_OPTS = "--histogram --add-logo --place-text 3 --enable-ratio --denominator NLO.ej1_excl2.dat --normalize $(bbLO) $(bbNLO) $(bbNNLO) --rescale 125.09"
  ej2_OPTS = "--histogram --add-logo --place-text 5 --enable-ratio --denominator NLO.ej2.dat --normalize $(bbLO) $(bbNLO) $(bbNNLO) --rescale 125.09"
  ej2_excl2_OPTS = "--histogram --add-logo --place-text 5 --enable-ratio --denominator NLO.ej2_excl2.dat --normalize $(bbLO) $(bbNLO) $(bbNNLO) --rescale 125.09"
  min_dR_lpj_OPTS = "--add-logo --place-text 6 --enable-ratio --denominator NLO.min_dR_lpj.dat --normalize $(bbLO) $(bbNLO) $(bbNNLO)"
  min_dR_lmj_OPTS = "--histogram --add-logo --place-text 6 --enable-ratio --denominator NLO.min_dR_lmj.dat --normalize $(bbLO) $(bbNLO) $(bbNNLO)"
  min_dR_lpj_excl2_OPTS = "--add-logo --place-text 6 --enable-ratio --denominator NLO.min_dR_lpj_excl2.dat --normalize $(bbLO) $(bbNLO) $(bbNNLO)"
  min_dR_lmj_excl2_OPTS = "--histogram --add-logo --place-text 6 --enable-ratio --denominator NLO.min_dR_lmj_excl2.dat --normalize $(bbLO) $(bbNLO) $(bbNNLO)"
  y12_OPTS = "--histogram --add-logo --place-text 6 --enable-ratio --denominator NLO.y12.dat --normalize $(bbLO) $(bbNLO) $(bbNNLO)"
  y12_log_OPTS = "--histogram --add-logo --logscale --place-text 4 --enable-ratio --denominator NLO.y12_log.dat --normalize $(bbLO) $(bbNLO) $(bbNNLO)"
  y23_log_OPTS = "--histogram --add-logo --logscale --enable-ratio --denominator NLO.y23_log.dat --normalize $(bbLO) $(bbNLO) $(bbNNLO)"
  y34_log_OPTS = "--histogram --add-logo --logscale --enable-ratio --denominator NLO.y34_log.dat --normalize $(bbLO) $(bbNLO) $(bbNNLO)"


  # Default is ORDER=NNLO
  all: $(NAMES)

  $(NAMES):
	@mkdir -p $(OUTDIR)
	@script=makeplot6.py; \
	  obs=$@; \
	  inputs="LO.$$obs.dat NLO.$$obs.dat NNLO.$$obs.dat"; \
	  for f in $$inputs; do \
	    [ -f "$(DATADIR)/$$f" ] || { echo "Missing input: $(DATADIR)/$$f"; exit 2; }; \
	  done; \
	  outfile=$(OUTDIR)/$$obs.pdf; \
	  opts=$($@_OPTS); \
	  echo "makeplot6.py << [$$inputs] → $$outfile"; \
	  $(PYTHON) $$script --path $(DATADIR) --input $$inputs --output $$outfile $$opts


  clean:
	rm -f $(OUTDIR)/*.pdf
