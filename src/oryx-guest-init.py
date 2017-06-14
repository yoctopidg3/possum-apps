#! /usr/bin/env python3
#
# oryx-guest-init
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

import logging
import os
import sys

APP_NAME = "oryx-guest-init"
VERSION_STRING = "%%VERSION_STRING%%"

# oryx-gues-init is a system service so make log messages explicit
logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s oryx-guest-init[%(process)d]: %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S %z")
logging.info("Booting (%s)..." % (VERSION_STRING))

# For now we just spawn a login prompt
args = ("sh", )
main_pid = os.spawnvp(os.P_NOWAIT, args[0], args)

# Wait for our main command to finish whilst cleaning up other zombie
# processes
while True:
    (pid, status) = os.wait()
    exit_code = status >> 8
    coredump = (status & 0x80) >> 7
    signal = status & 0x7F
    if pid == main_pid:
        logging.info("Exiting...")
        sys.exit(exit_code)
    else:
        logging.debug("Reaped pid=%d, exit_code=%d, coredump=%d, signal=%d" %
                      (pid, exit_code, coredump, signal))
