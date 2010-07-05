#!/usr/bin/python
# !!!! WARNING !!!!
# Test file : It's not safe, can break your system and make your life miserable, you've been warned.
# !!!! WARNING !!!!

from portage import *

ret = pkgcmp(pkgsplit(sys.argv[1]), pkgsplit(sys.argv[2]))

if ret == 0 :
	print "same"
elif ret == -1:
	print "less"
else:
	print "more"
