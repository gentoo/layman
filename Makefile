.PHONY: doc
doc:
	$(MAKE) -C doc

.PHONY: www
www:
	cp doc/layman.8.html www/index.html

.PHONY: dist
dist: doc
	rm -rf dist MANIFEST
	./setup.py sdist
