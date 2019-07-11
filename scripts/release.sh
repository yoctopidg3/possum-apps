#! /bin/bash
#
# Copyright (C) 2017 Togán Labs
# SPDX-License-Identifier: MIT
#

set -e
set -o pipefail

if [[ $# != 1 ]]; then
    echo "Usage: $0 VERSION" >&2
    exit 1
fi
VERSION=$1

OUTDIR=release/${VERSION}
mkdir -p ${OUTDIR}

# Ensure release is tagged
TAGNAME=v$VERSION
if [[ `git tag -l $TAGNAME` != "$TAGNAME" ]]; then
    echo "ERROR! Release must be correctly tagged!"
    exit 1
fi

do_checksums() {
    pushd $1 &> /dev/null
    md5sum *.xz > MD5SUMS
    sha1sum *.xz > SHA1SUMS
    sha256sum *.xz > SHA256SUMS
    popd &> /dev/null
}

do_src() {
    git archive --format=tar --prefix=oryx-apps-$VERSION/ $TAGNAME \
        | xz > ${OUTDIR}/oryx-apps-$VERSION.tar.xz

    do_checksums ${OUTDIR}
}

do_src
