include .devcontainer/tools.mk


ABLOG_ARGS=
BUILDDIR=_build/html
PORT=8000

default: html

node_modules/.installed: package.json package-lock.json $(NPM)
	$(NPM) ci
	touch $@

.PHONY: tailwind
tailwind: node_modules/.installed

# Rebuild everything if any JavaScript is modified
$(BUILDDIR)/_static/js/theme.js: _static/js/theme.js
	$(eval ABLOG_ARGS=-a)

# Run tailwind if any styles are changed.
_static/css/styles.css: styles.css tailwind.config.js $(wildcard _templates/*.html) _static/js/theme.js tailwind
	$(NPX) tailwindcss -i styles.css -o _static/css/styles.css
	$(eval ABLOG_ARGS=-a)

html: _static/css/styles.css $(BUILDDIR)/_static/js/theme.js
	$(HATCH) run 'blog:build'
	mkdir -p $(BUILDDIR)/talks/
	cp -r talks/introducing-esbonio $(BUILDDIR)/talks/introducing-esbonio
	patch -N -p1 < searchtools.patch

preview:
	python -m http.server -d $(BUILDDIR) $(PORT)
