# Makefile with flexible input files depending on ORDER

PYTHON = python3
DATADIR = combined/Final
OUTDIR = plots

NAMES = \
  mH m12 m12low mZ ej1 ej2 dR_l12 dR_j12 min_dR_lmj min_dR_lpj

.PHONY: all clean $(NAMES)

# Default to NNLO if ORDER is not set
all: $(NAMES)

$(NAMES):
	@mkdir -p $(OUTDIR)
	@order=$${ORDER:-NNLO}; \
	  prefix=$$(echo $$order | tr '[:upper:]' '[:lower:]'); \
	  script=makeplot5$${prefix}.py; \
	  obs=$@; \
	  files=""; \
	  if [ "$$order" = "LO" ]; then \
	    files="LO.$$obs.dat"; \
	  elif [ "$$order" = "NLO" ]; then \
	    files="LO.$$obs.dat NLO.$$obs.dat"; \
	  elif [ "$$order" = "NNLO" ]; then \
	    files="LO.$$obs.dat NLO.$$obs.dat NNLO.$$obs.dat"; \
	  else \
	    echo "Unknown ORDER='$$order' (expected LO, NLO, NNLO)"; exit 1; \
	  fi; \
	  outfile=$$obs.pdf; \
	  echo "$$order.$$obs.dat → [$$script] → $$outfile"; \
	  $(PYTHON) $$script --path $(DATADIR) --input $$files --output $$outfile --add-logo

clean:
	rm -f $(OUTDIR)/*.pdf
