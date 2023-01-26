# possum-apps Makefile
#
# Copyright (C) 2017-2023 Togán Labs
# SPDX-License-Identifier: MIT
#

PACKAGE_NAME := possum-apps
PACKAGE_VERSION := 0.3.0

PREFIX := /usr/local
sbindir := $(PREFIX)/sbin
sysconfdir := /etc
syslibdir := /lib

APPS := bin/possumcmd bin/possumcmd-test

all: $(APPS)

bin/%: src/%.py Makefile
	mkdir -p bin
	sed -e "s/%%VERSION_STRING%%/$(PACKAGE_NAME) v$(PACKAGE_VERSION)/" $< > $@
	chmod a+x $@

install: $(APPS)
	install -d "$(DESTDIR)$(sbindir)"
	install -m 755 $(APPS) "$(DESTDIR)$(sbindir)"
	install -d "$(DESTDIR)$(syslibdir)/systemd/system"
	install -m 644 src/possum-guests.service "$(DESTDIR)$(syslibdir)/systemd/system/possum-guests.service"

clean:
	rm -rf bin

version:
	@echo $(PACKAGE_VERSION)
