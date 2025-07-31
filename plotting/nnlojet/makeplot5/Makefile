# Makefile with flexible input files depending on ORDER

PYTHON = python3
DATADIR = combined/Final
OUTDIR = plots

NAMES = \
  mZ dR_l12 mH_all mH_12 dR_j12 ej1 ej1_excl1  ej2 ej2_excl2 min_dR_lpj min_dR_lmj min_dR_lpj_excl2 min_dR_lmj_excl2 \
  y12_log y23_log y34_log

  .PHONY: all clean $(NAMES)

# Observable-specific options
mZ_OPTS = "--add-logo"
dR_l12_OPTS = "--histogram --add-logo"
mH_all_OPTS = "--add-logo"
mH_12_OPTS = "--add-logo"
dR_j12_OPTS = "--histogram --add-logo"
ej1_OPTS = "--histogram --add-logo --place-text 5"
ej1_excl1_OPTS = "--histogram --add-logo"
ej2_OPTS = "--histogram --add-logo --place-text 5"
ej2_excl2_OPTS = "--histogram --add-logo --place-text 5"
min_dR_lpj_OPTS = "--histogram --add-logo --place-text 6"
min_dR_lmj_OPTS = "--histogram --add-logo --place-text 6"
min_dR_lpj_excl2_OPTS = "--histogram --add-logo --place-text 6"
min_dR_lmj_excl2_OPTS = "--histogram --add-logo --place-text 6"
y12_log_OPTS = "--histogram --add-logo --logscale"
y23_log_OPTS = "--histogram --add-logo --logscale"
y34_log_OPTS = "--histogram --add-logo --logscale"

  # Default is ORDER=NNLO
  all: $(NAMES)

  $(NAMES):
	@mkdir -p $(OUTDIR)
	@order=$${ORDER:-NNLO}; \
	  prefix=$$(echo $$order | tr '[:upper:]' '[:lower:]'); \
	  script=makeplot5$${prefix}.py; \
	  obs=$@; \
	  inputs=""; \
	  if [ "$$order" = "LO" ]; then \
	    inputs="LO.$$obs.dat"; \
	  elif [ "$$order" = "NLO" ]; then \
	    inputs="LO.$$obs.dat NLO.$$obs.dat"; \
	  elif [ "$$order" = "NNLO" ]; then \
	    inputs="LO.$$obs.dat NLO.$$obs.dat NNLO.$$obs.dat"; \
	  else \
	    echo "Unknown ORDER='$$order' (expected LO, NLO, NNLO)"; exit 1; \
	  fi; \
	  for f in $$inputs; do \
	    [ -f "$(DATADIR)/$$f" ] || { echo "Missing input: $(DATADIR)/$$f"; exit 2; }; \
	  done; \
	  outfile=$$obs.pdf; \
	  echo "$$order.$$obs.dat → [$$script] → $$outfile"; \
	  opts=$($@_OPTS); \
  $(PYTHON) $$script --path $(DATADIR) --input $$inputs --output $$outfile $$opts

  clean:
	rm -f $(OUTDIR)/*.pdf
