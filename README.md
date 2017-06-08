Introduction
============

This is a collection of applications used in Oryx Embedded Linux.

Commands
========

oryxcmd
-------

This is a tool for managing guest containers within an Oryx host system. For
more details, see the built-in help for this command by running:

    oryxcmd help

oryx-guest-init
---------------

This is a simple replacement init system for use in guest containers. It starts
exactly one payload application and cleans up any zombie processes whilst this
main payload application executes. Once the payload application exits, the guest
container is shutdown.

Contributing
============

For code contributions please open a merge request on the main repository at
<https://gitlab.com/oryx/oryx-apps>.

Support
=======

Oryx Embedded Linux is developed and supported by Togán Labs Ltd.

For support requests, bug reports or other feedback please open an issue in the
Togán Labs bug tracker at <https://bugs.toganlabs.com/> or contact us via email
to <support@toganlabs.com>.
