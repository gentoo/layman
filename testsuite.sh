#!/usr/bin/env bash
# Copyright (C) 2010  Sebastian Pipping <sebastian@pipping.org>
# Licensed under GPLv2

ret=0
for script in  layman/tests/*.py  ; do
	echo "# PYTHONPATH=\"${PWD}\" python \"${script}\""
	PYTHONPATH="${PWD}" python "${script}" \
		|| ret=1
done

[[ ${ret} != 0 ]] && echo '!!! FAIL'
exit ${ret}
