BUILDDIR ?=_build
DOTFILES ?= $(HOME)/.config/dotfiles
PROJECTS ?= $(HOME)/Projects

HTMLDIR=$(BUILDDIR)/dirhtml
PORT ?= 8000

SPHINX_OPTS ?=

ifneq ($(strip $(INSIDE_EMACS)),)
SPHINX_OPTS += --no-color
endif


default: html

.PHONY: clean
clean:
	-test -d $(BUILDDIR) && rm -r $(BUILDDIR)

.PHONY: html
html: | $(UV)
	$(UV) run esbonio sphinx build --build-args '-M dirhtml . $(BUILDDIR) $(SPHINX_OPTS)'
	mkdir -p $(HTMLDIR)/talks/
	cp -r talks/introducing-esbonio $(HTMLDIR)/talks/introducing-esbonio


.PHONY: pages
pages: $(BUILDDIR)/blog.tar.gz

$(BUILDDIR)/blog.tar.gz: html
	tar --directory $(HTMLDIR)/ -cvf $@ .
	ls -lh $@

.PHONY: dotfiles
dotfiles: | $(UV)
	$(UV) run sphinx-build -Ea -b awdur . $(DOTFILES) $(SPHINX_OPTS)


preview:
	python -m http.server -d $(HTMLDIR) $(PORT)


mal: dotfiles
	-rm $(PROJECTS)/kanaka/mal/master/impls/py/*
	cp $(DOTFILES)/mal-py/* $(PROJECTS)/kanaka/mal/master/impls/py/
	make -C $(PROJECTS)/kanaka/mal/master/ test^py^step8

include .devcontainer/tools.mk
