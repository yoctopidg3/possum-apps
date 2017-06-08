PACKAGE_NAME := oryx-apps
PACKAGE_VERSION := 0.1.0

PREFIX := /usr/local
bindir := $(PREFIX)/bin

APPS := bin/oryxcmd bin/oryx-guest-init

all: $(APPS)

bin/%: src/%.py Makefile
	mkdir -p bin
	sed -e "s/%%VERSION_STRING%%/$(PACKAGE_NAME) v$(PACKAGE_VERSION)/" $< > $@
	chmod a+x $@

install: $(APPS)
	install -d "$(bindir)"
	install -m 755 $(APPS) "$(bindir)"
