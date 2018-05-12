# oryx-apps Makefile
#
# Copyright (C) 2017 Togán Labs
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
#

PACKAGE_NAME := oryx-apps
PACKAGE_VERSION := 0.2.2

PREFIX := /usr/local
sbindir := $(PREFIX)/sbin
sysconfdir := /etc

APPS := bin/oryxcmd bin/oryxcmd-test

all: $(APPS)

bin/%: src/%.py Makefile
	mkdir -p bin
	sed -e "s/%%VERSION_STRING%%/$(PACKAGE_NAME) v$(PACKAGE_VERSION)/" $< > $@
	chmod a+x $@

install: $(APPS)
	install -d "$(DESTDIR)$(sbindir)"
	install -m 755 $(APPS) "$(DESTDIR)$(sbindir)"
	install -d "$(DESTDIR)$(sysconfdir)/init.d"
	install -m 755 src/oryx-guests-initscript "$(DESTDIR)$(sysconfdir)/init.d/oryx-guests"

clean:
	rm -rf bin

version:
	@echo $(PACKAGE_VERSION)
