.PHONY: www
www:
	cp trunk/layman/doc/layman.8.html www/index.html
	rsync -rlvz --del www/ luciferc,layman@web.sourceforge.net:htdocs/

.PHONY: release
release:
	rm -rf dist
	cd doc && make
	./setup.py sdist
	rsync -auP dist/*.tar.gz luciferc@frs.sourceforge.net:uploads/
