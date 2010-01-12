.PHONY: www
www:
	cp doc/layman.8.html www/index.html

.PHONY: release
release:
	rm -rf dist MANIFEST
	$(MAKE) -C doc
	./setup.py sdist
