.PHONY: doc
doc:
	$(MAKE) -C doc

.PHONY: dist
dist: doc
	rm -rf dist MANIFEST
	./setup.py sdist

.PHONY: website
website: doc
	# Upload HTML version of the man page to http://layman.sf.net/
	# Please run this for each release
	# https://sourceforge.net/apps/trac/sourceforge/wiki/Project%20web#ConnectionSettings
	scp  doc/docbook-xsl.css doc/layman.8.html  dol-sen,layman@web.sourceforge.net:/home/groups/l/la/layman/htdocs/
