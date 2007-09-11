#
# layman/doc/Makefile
#		Simple Makefile to rebuild the documentation from the
#		docbook XML sources
#
# Copyright (c) 1999-2005 Gentoo Foundation
#       Released under v2 of the GNU GPL
#
# Author(s)     Stuart Herbert <stuart@gentoo.org>
#               Renat Lumpau   <rl03@gentoo.org>
#               Gunnar Wrobel  <php@gunnarwrobel.de>
#
# ========================================================================

MAN_PAGES = layman.8
HTML_PAGES = layman.8.html 

TMPFILE=./layman.man

all: man html

html: $(HTML_PAGES)

man: $(MAN_PAGES)

clean:
	rm -f $(MAN_PAGES)
	rm -f $(HTML_PAGES)

%.html: %.xml
	@echo HTML $@
	@xmlto html-nochunks $<

%: %.xml
	@echo MAN $@
	@xmlto man $<
#
# fix up the blank lines that docbook leaves behind
#
	@cat $@ | sed -e 's/$$/.fred/g;' | tr -d '\n' | sed -e 's/.fred.fred\./.fred./g;' | sed -e 's/.fred/\n/g;' > $(TMPFILE)
	@mv $(TMPFILE) $@
