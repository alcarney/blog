.PHONY: html

ABLOG_ARGS=

ifeq ($(CI),true)
	NPM_SCRIPT=build
else
	NPM_SCRIPT=dev
endif


# Rebuild everything if any JavaScript is modified
_build/html/_static/js/theme.js: _static/js/theme.js
	$(eval ABLOG_ARGS=-a)

# Run tailwind if any styles are changed.
_static/css/styles.css: styles.css tailwind.config.js
	npm run $(NPM_SCRIPT)
	$(eval ABLOG_ARGS=-a)

html: _static/css/styles.css _build/html/_static/js/theme.js
	ablog build $(ABLOG_ARGS) -w _build/html -d _build/doctrees
	patch -N -p1 < searchtools.patch
	