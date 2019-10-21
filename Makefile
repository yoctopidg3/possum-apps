# oryx-apps Makefile
#
# Copyright (C) 2017-2018 Togán Labs
# SPDX-License-Identifier: MIT
#

PACKAGE_NAME := oryx-apps
PACKAGE_VERSION := 0.3.0

PREFIX := /usr/local
sbindir := $(PREFIX)/sbin
sysconfdir := /etc
syslibdir := /lib

APPS := bin/oryxcmd bin/oryxcmd-test

all: $(APPS)

bin/%: src/%.py Makefile
	mkdir -p bin
	sed -e "s/%%VERSION_STRING%%/$(PACKAGE_NAME) v$(PACKAGE_VERSION)/" $< > $@
	chmod a+x $@

install: $(APPS)
	install -d "$(DESTDIR)$(sbindir)"
	install -m 755 $(APPS) "$(DESTDIR)$(sbindir)"
	install -d "$(DESTDIR)$(syslibdir)/systemd/system"
	install -m 644 src/oryx-guests.service "$(DESTDIR)$(syslibdir)/systemd/system/oryx-guests.service"

clean:
	rm -rf bin

version:
	@echo $(PACKAGE_VERSION)
