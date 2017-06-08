PREFIX := /usr/local
bindir := $(PREFIX)/bin

APPS := oryxcmd oryx-guest-init

install:
	install -d "$(bindir)"
	install -m 755 $(APPS) "$(bindir)"
