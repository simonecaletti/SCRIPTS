# Makefile with flexible input files

PYTHON = python3
DATADIR = combined/Final

# Output directories
FO_OUTDIR = plots_fo
INEX_OUTDIR = plots_inex
# Config files
CONFIG_FO= config/FO/
CONFIG_INEX=config/INEX/

INCL = \
  mZ dR_l12 mH_all mH_12 dR_j12 ej1\
  ej2 min_dR_lpj min_dR_lmj
RATES = y12 y12_log y23_log y34_log
EXCL := $(foreach incl,$(INCL),$(incl)_excl2)
NAMES := $(INCL) $(EXCL) $(RATES)

# Total cross section full inclusive
bbLO=3.6828205
bbNLO=4.43100509
bbNNLO=4.56900509

# =========================================================================
# CODE START HERE

TYPE ?= FO
OUTDIR ?= $(FO_OUTDIR)

  .PHONY: all clean gallery $(NAMES) fo inex

  # Auto-generate *_FO_INPUTS and *_INEX_INPUTS
  $(foreach obs,$(INCL),\
    $(eval $(obs)_FO_INPUTS := LO.$(obs).dat NLO.$(obs).dat NNLO.$(obs).dat) \
    $(eval $(obs)_INEX_INPUTS := NNLO.$(obs).dat NNLO.$(obs)_excl2.dat) \
  )

  $(foreach obs,$(EXCL) $(RATES),\
    $(eval $(obs)_FO_INPUTS := LO.$(obs).dat NLO.$(obs).dat NNLO.$(obs).dat) \
  )

  # Observable-specific options for FO
  mZ_FO_OPTS = "--histogram --add-logo --enable-ratio --denominator NLO.mZ.dat --normalize $(bbLO) $(bbNLO) $(bbNNLO) --config-path $(CONFIG_FO)"
  mZ_excl2_FO_OPTS = "--histogram --add-logo --enable-ratio --denominator NLO.mZ_excl2.dat --normalize $(bbLO) $(bbNLO) $(bbNNLO) --config-path $(CONFIG_FO)"
  dR_l12_FO_OPTS = "--histogram --add-logo --enable-ratio --denominator NLO.dR_l12.dat --normalize $(bbLO) $(bbNLO) $(bbNNLO) --config-path $(CONFIG_FO)"
  dR_l12_excl2_FO_OPTS = "--histogram --add-logo --enable-ratio --denominator NLO.dR_l12_excl2.dat --normalize $(bbLO) $(bbNLO) $(bbNNLO) --config-path $(CONFIG_FO)"
  mH_all_FO_OPTS = "--add-logo --enable-ratio --denominator NLO.mH_all.dat --normalize $(bbLO) $(bbNLO) $(bbNNLO) --config-path $(CONFIG_FO)"
  mH_all_excl2_FO_OPTS = "--add-logo --enable-ratio --denominator NLO.mH_all_excl2.dat --normalize $(bbLO) $(bbNLO) $(bbNNLO) --config-path $(CONFIG_FO)"
  mH_12_FO_OPTS = "--add-logo --enable-ratio --denominator NLO.mH_12.dat --normalize $(bbLO) $(bbNLO) $(bbNNLO) --config-path $(CONFIG_FO)"
  mH_12_excl2_FO_OPTS = "--add-logo --enable-ratio --denominator NLO.mH_12_excl2.dat --normalize $(bbLO) $(bbNLO) $(bbNNLO) --config-path $(CONFIG_FO)"
  dR_j12_FO_OPTS = "--histogram --add-logo --place-text 4 --enable-ratio --denominator NLO.dR_j12.dat --normalize $(bbLO) $(bbNLO) $(bbNNLO) --config-path $(CONFIG_FO)"
  dR_j12_excl2_FO_OPTS = "--histogram --add-logo --place-text 4 --enable-ratio --denominator NLO.dR_j12_excl2.dat --normalize $(bbLO) $(bbNLO) $(bbNNLO) --config-path $(CONFIG_FO)"
  ej1_FO_OPTS = "--histogram --add-logo --place-text 3 --enable-ratio --denominator NLO.ej1.dat --normalize $(bbLO) $(bbNLO) $(bbNNLO) --rescale 125.09 --config-path $(CONFIG_FO)"
  ej1_excl2_FO_OPTS = "--histogram --add-logo --place-text 3 --enable-ratio --denominator NLO.ej1_excl2.dat --normalize $(bbLO) $(bbNLO) $(bbNNLO) --rescale 125.09 --config-path $(CONFIG_FO)"
  ej2_FO_OPTS = "--histogram --add-logo --place-text 5 --enable-ratio --denominator NLO.ej2.dat --normalize $(bbLO) $(bbNLO) $(bbNNLO) --rescale 125.09 --config-path $(CONFIG_FO)"
  ej2_excl2_FO_OPTS = "--histogram --add-logo --place-text 5 --enable-ratio --denominator NLO.ej2_excl2.dat --normalize $(bbLO) $(bbNLO) $(bbNNLO) --rescale 125.09 --config-path $(CONFIG_FO)"
  min_dR_lpj_FO_OPTS = "--histogram --add-logo --place-text 6 --enable-ratio --denominator NLO.min_dR_lpj.dat --normalize $(bbLO) $(bbNLO) $(bbNNLO) --config-path $(CONFIG_FO)"
  min_dR_lmj_FO_OPTS = "--histogram --add-logo --place-text 6 --enable-ratio --denominator NLO.min_dR_lmj.dat --normalize $(bbLO) $(bbNLO) $(bbNNLO) --config-path $(CONFIG_FO)"
  min_dR_lpj_excl2_FO_OPTS = "--histogram --add-logo --place-text 6 --enable-ratio --denominator NLO.min_dR_lpj_excl2.dat --normalize $(bbLO) $(bbNLO) $(bbNNLO) --config-path $(CONFIG_FO)"
  min_dR_lmj_excl2_FO_OPTS = "--histogram --add-logo --place-text 6 --enable-ratio --denominator NLO.min_dR_lmj_excl2.dat --normalize $(bbLO) $(bbNLO) $(bbNNLO) --config-path $(CONFIG_FO)"
  y12_FO_OPTS = "--histogram --add-logo --place-text 6 --enable-ratio --denominator NLO.y12.dat --normalize $(bbLO) $(bbNLO) $(bbNNLO) --config-path $(CONFIG_FO)"
  y12_log_FO_OPTS = "--histogram --add-logo --logscale --place-text 4 --enable-ratio --denominator NLO.y12_log.dat --normalize $(bbLO) $(bbNLO) $(bbNNLO) --config-path $(CONFIG_FO)"
  y23_log_FO_OPTS = "--histogram --add-logo --logscale --enable-ratio --denominator NLO.y23_log.dat --normalize $(bbLO) $(bbNLO) $(bbNNLO) --config-path $(CONFIG_FO)"
  y34_log_FO_OPTS = "--histogram --add-logo --logscale --enable-ratio --denominator NLO.y34_log.dat --normalize $(bbLO) $(bbNLO) $(bbNNLO) --config-path $(CONFIG_FO)"

  # Observable-specific options for INEX
  mZ_INEX_OPTS = "--histogram --add-logo --enable-ratio --normalize $(bbNNLO) $(bbNNLO) --config-path $(CONFIG_INEX)"
  dR_l12_INEX_OPTS = "--histogram --add-logo --enable-ratio --normalize $(bbNNLO) $(bbNNLO) --config-path $(CONFIG_INEX)"
  mH_all_INEX_OPTS = "--add-logo --enable-ratio --normalize $(bbNNLO) $(bbNNLO) --config-path $(CONFIG_INEX)"
  mH_12_INEX_OPTS = "--add-logo --enable-ratio --normalize $(bbNNLO) $(bbNNLO) --config-path $(CONFIG_INEX)"
  dR_j12_INEX_OPTS = "--histogram --add-logo --place-text 4 --enable-ratio --normalize $(bbNNLO) $(bbNNLO) --config-path $(CONFIG_INEX)"
  ej1_INEX_OPTS = "--histogram --add-logo --place-text 3 --enable-ratio --normalize $(bbNNLO) $(bbNNLO) --rescale 125.09 --config-path $(CONFIG_INEX)"
  ej2_INEX_OPTS = "--histogram --add-logo --place-text 5 --enable-ratio --normalize $(bbNNLO) $(bbNNLO) --rescale 125.09 --config-path $(CONFIG_INEX)"
  min_dR_lpj_INEX_OPTS = "--histogram --add-logo --place-text 6 --enable-ratio --normalize $(bbNNLO) $(bbNNLO) --config-path $(CONFIG_INEX)"
  min_dR_lmj_INEX_OPTS = "--histogram --add-logo --place-text 6 --enable-ratio --normalize $(bbNNLO) $(bbNNLO) --config-path $(CONFIG_INEX)"

  all: fo inex

  #All LO + NLO + NNLO plots
  fo:
	@$(MAKE) TYPE=FO OUTDIR=$(FO_OUTDIR) $(NAMES)

  #All INCL vs EXCL plots
  inex:
	@$(MAKE) TYPE=INEX OUTDIR=$(INEX_OUTDIR) $(INCL)


  $(NAMES):
	$(eval TYPE ?= FO)
	$(eval OPT_VAR := $@_$(TYPE)_OPTS)
	$(eval INPUT_VAR := $@_$(TYPE)_INPUTS)
	$(eval OPTS := $($(OPT_VAR)))
	$(eval INPUTS := $($(INPUT_VAR)))
	@mkdir -p $(OUTDIR)
	@script=./makeplot6.py; \
	  obs=$@; \
	  inputs="$(INPUTS)"; \
	  for f in $$inputs; do \
	    [ -f "$(DATADIR)/$$f" ] || { echo "Missing input: $(DATADIR)/$$f"; exit 2; }; \
	  done; \
	  outfile=$(OUTDIR)/$$obs.pdf; \
	  echo "[$$inputs] → makeplot6.py → $$outfile"; \
	  opts=$(OPTS); \
	  $(PYTHON) $$script --path $(DATADIR) --input $$inputs --output $$outfile $$opts

  gallery:
	@python3 gallery.py --input $(FO_OUTDIR) $(INEX_OUTDIR)
	@firefox 'gallery.html?nocache='$(shell date +%s)


 clean:
	rm -f $(FO_OUTDIR)/*.pdf
	rm -f $(INEX_OUTDIR)/*.pdf
	rm gallery.html
