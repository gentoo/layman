# Copyright 1999-2007 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo-x86/app-portage/layman/layman-1.0.10.ebuild,v 1.1 2007/01/09 18:01:15 wrobel Exp $

inherit eutils distutils

DESCRIPTION="A python script for retrieving gentoo overlays."
HOMEPAGE="http://projects.gunnarwrobel.de/scripts"
SRC_URI="http://build.pardus.de/downloads/${PF}.tar.gz"

LICENSE="GPL-2"
SLOT="0"
KEYWORDS="~alpha ~amd64 ~ppc ~ppc64 ~sparc ~x86 ~x86-fbsd"
IUSE=""
S=${WORKDIR}/${PF}

DEPEND=""
RDEPEND=""

pkg_setup() {
	if has_version dev-util/subversion && built_with_use dev-util/subversion nowebdav; then
		eerror "You must rebuild your subversion without the nowebdav USE flag"
		die "You must rebuild your subversion without the nowebdav USE flag"
	fi
}

src_install() {

	distutils_src_install

	dodir /etc/layman
	cp etc/* ${D}/etc/layman/

	doman doc/layman.8
	dohtml doc/layman.8.html

}

src_test() {
	cd ${S}
	einfo "Running layman doctests..."
	echo
	if ! PYTHONPATH="." ${python} layman/tests/dtest.py; then
		eerror "DocTests failed - please submit a bug report"
		die "DocTesting failed!"
	fi
}

pkg_postinst() {
	einfo "You are now ready to add overlays into your system."
	einfo
	einfo "layman -L"
	einfo
	einfo "will display a list of available overlays."
	einfo
	ewarn "Use the -k switch to also list overlays that are"
	ewarn "considered less secure."
	einfo
	elog  "Select an overlay and add it using"
	einfo
	elog  "layman -a overlay-name"
	einfo
	elog  "If this is the very first overlay you add with layman,"
	elog  "you need to append the following statement to your"
	elog  "/etc/make.conf file:"
	elog
	elog  "source /usr/portage/local/layman/make.conf"
	elog
	elog  "If you modify the 'storage' parameter in the layman"
	elog  "configuration file (/etc/layman/layman.cfg) you will"
	elog  "need to adapt the path given above to the new storage"
	elog  "directory."
	einfo
	ewarn "Please add the 'source' statement to make.conf only AFTER "
	ewarn "you added your first overlay. Otherwise portage will fail."
	epause 5
}
