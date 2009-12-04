.PHONY: www
www:
	cp trunk/layman/doc/layman.8.html www/index.html

.PHONY: release
release:
	rm -rf dist
	cd doc && make
	./setup.py sdist
