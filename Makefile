BUILDDIR ?=_build
DOTFILES ?= $(HOME)/.config/dotfiles

HTMLDIR=$(BUILDDIR)/dirhtml
PORT ?= 8000

SPHINX_OPTS ?=

ifneq ($(strip $(INSIDE_EMACS)),)
SPHINX_OPTS += --no-color
endif


default: html

.PHONY: clean
clean:
	-test -d _build/doctrees && rm -r _build/doctrees
	-test -d _build/dirhtml && rm -r _build/dirhtml

# Rebuild everything if any JavaScript is modified
$(HTMLDIR)/_static/js/theme.js: _static/js/theme.js
	$(eval SPHINX_OPTS=-Ea)

.PHONY: html
html:
	$(UV) run sphinx-build -M dirhtml . $(BUILDDIR) $(SPHINX_OPTS)
	mkdir -p $(HTMLDIR)/talks/
	cp -r talks/introducing-esbonio $(HTMLDIR)/talks/introducing-esbonio


.PHONY: dotfiles
dotfiles:
	$(UV) run sphinx-build -b awdur . $(DOTFILES) $(SPHINX_OPTS)


preview:
	python -m http.server -d $(HTMLDIR) $(PORT)


include .devcontainer/tools.mk
