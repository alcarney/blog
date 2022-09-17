.PHONY: html preview

ABLOG_ARGS=
BUILDDIR=_build/html
PORT=8000

ifeq ($(CI),true)
	TAILWIND=./node_modules/.bin/tailwindcss
else
	TAILWIND=tailwindcss
endif

default: html

# Rebuild everything if any JavaScript is modified
$(BUILDDIR)/_static/js/theme.js: _static/js/theme.js
	$(eval ABLOG_ARGS=-a)

# Run tailwind if any styles are changed.
_static/css/styles.css: styles.css tailwind.config.js $(wildcard _templates/*.html)
	$(TAILWIND) -i styles.css -o _static/css/styles.css
	$(eval ABLOG_ARGS=-a)

html: _static/css/styles.css $(BUILDDIR)/_static/js/theme.js
	ablog build $(ABLOG_ARGS) -w $(BUILDDIR) -d _build/doctrees
	mkdir -p $(BUILDDIR)/talks/
	cp -r talks/introducing-esbonio $(BUILDDIR)/talks/introducing-esbonio
	patch -N -p1 < searchtools.patch

preview:
	python -m http.server -d $(BUILDDIR) $(PORT)
