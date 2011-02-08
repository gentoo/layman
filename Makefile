.PHONY: doc
doc:
	$(MAKE) -C doc

.PHONY: dist
dist: doc
	rm -rf dist MANIFEST
	./setup.py sdist
