#! /usr/bin/env python3
#
# oryxcmd
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

import cmd
import fcntl
import json
import logging
import os
import shutil
import subprocess
import sys
import tarfile
import types
import urllib.request

APP_NAME = "oryxcmd"
VERSION_STRING = "%%VERSION_STRING%%"

log = logging.getLogger()
log.setLevel(logging.DEBUG)

class OryxSysmgr:
    def add_source(self, name, url):
        state = self._lock_and_read_state()
        if "sources" in state:
            if name in state['sources']:
                log.error("Source %s already defined!" % (name))
                return
        else:
            state['sources'] = {}

        state['sources'][name] = url
        self._unlock_and_write_state(state)

    def remove_source(self, name):
        state = self._lock_and_read_state()
        if "sources" not in state:
            log.error("Source %s not defined!" % (name))
            return
        if name not in state['sources']:
            log.error("Source %s not defined!" % (name))
            return

        del state['sources'][name]
        self._unlock_and_write_state(state)

    def list_sources(self):
        state = self._lock_and_read_state()
        if "sources" not in state:
            return

        for name in state['sources']:
            print(name)
        self._unlock_and_write_state(state)

    def show_source(self, name):
        state = self._lock_and_read_state()
        if "sources" not in state:
            log.error("Source %s not defined!" % (name))
            return
        if name not in state['sources']:
            log.error("Source %s not defined!" % (name))
            return

        data = {name: state['sources'][name]}
        print(json.dumps(data, indent=4, sort_keys=True))

        self._unlock_and_write_state(state)

    def add_guest(self, name, image, config):
        state = self._lock_and_read_state()
        if "guests" in state:
            if name in state['guests']:
                log.error("Guest %s already defined!" % (name))
                return
        else:
            state['guests'] = {}

        # For now, image name must be fully qualified as "<source>:<image>". In
        # the future we should support unqualified image names which we will
        # search for in each configured source
        (source_name, image_name) = image.split(":")

        if source_name not in state['sources']:
            log.error("Source %s not defined!" % (name))
            return

        source_url = state['sources'][source_name]
        image_root = os.path.join(source_url, 'guest', image_name)
        image_url = os.path.join(image_root, "image.json")

        image_json = urllib.request.urlopen(image_url).read().decode('utf-8')
        image_config = json.loads(image_json)
        rootfs_url = os.path.join(image_root, image_config['ARCHIVE'])

        local_path = os.path.join("/var/lib/oryx-guests", name)
        rootfs_path = os.path.join(local_path, "rootfs")

        (rootfs_filename, rootfs_headers) = urllib.request.urlretrieve(rootfs_url)
        with tarfile.open(rootfs_filename, mode="r:xz") as tf:
            tf.extractall(rootfs_path)
        urllib.request.urlcleanup()

        guest = {}
        guest['image'] = image_config
        guest['source_name'] = source_name
        guest['source_url'] = source_url
        guest['path'] = local_path
        guest['config'] = config

        state['guests'][name] = guest
        self._unlock_and_write_state(state)

    def remove_guest(self, name):
        state = self._lock_and_read_state()
        if "guests" not in state:
            log.error("Guest %s not defined!" % (name))
            return
        if name not in state['guests']:
            log.error("Guest %s not defined!" % (name))
            return

        shutil.rmtree(state['guests'][name]['path'])
        del state['guests'][name]
        self._unlock_and_write_state(state)

    def reconfigure_guest(self, name, config):
        state = self._lock_and_read_state()
        if "guests" not in state:
            log.error("Guest %s not defined!" % (name))
            return
        if name not in state['guests']:
            log.error("Guest %s not defined!" % (name))
            return

        state['guests'][name]['config'] = config
        self._unlock_and_write_state(state)

    def runc(self, name, runc_args):
        state = self._lock_and_read_state()
        if "guests" not in state:
            log.error("Guest %s not defined!" % (name))
            return
        if name not in state['guests']:
            log.error("Guest %s not defined!" % (name))
            return

        local_path = os.path.join("/var/lib/oryx-guests", name)
        args = ["runc"] + runc_args
        subprocess.run(args, cwd=local_path, check=True)

        self._unlock_and_write_state(state)

    def _lock_and_read_state(self):
        try:
            self.statefile = open('/var/lib/oryx-guests/state', 'r+')
            fcntl.lockf(self.statefile, fcntl.LOCK_EX)
            return json.load(self.statefile)
        except:
            self.statefile = open('/var/lib/oryx-guests/state', 'w')
            fcntl.lockf(self.statefile, fcntl.LOCK_EX)
            return {}

    def _unlock_and_write_state(self, state):
        self.statefile.seek(0)
        self.statefile.truncate()
        json.dump(state, self.statefile)
        self.statefile.close()

class OryxCmd(cmd.Cmd):
    intro = "Welcome to %s (%s)" % (APP_NAME, VERSION_STRING)
    prompt = "oryxcmd> "
    def __init__(self):
        self.sysmgr = OryxSysmgr()
        super().__init__()

    def do_add_source(self, line):
        """
        add_source NAME URL

        Register a new source from which images may be fetched.

        Arguments:

            NAME    An identifier which may be used to reference this source in
                    future commands.

            URL     The root URL under which image archives may be found.

        Example:

            add_source oryx https://downloads.toganlabs.com/oryx/0.2/guests
        """

        args = line.split()
        if len(args) != 2:
            log.error("Incorrect number of args!")
            return
        (name, url) = args
        self.sysmgr.add_source(name, url)

    def do_remove_source(self, line):
        """
        remove_source NAME

        Remove a previously registered source.

        Arguments:

            NAME    The identifier of the source to remove.

        Example:

            remove_source oryx
        """

        args = line.split()
        if len(args) != 1:
            log.error("Incorrect number of args!")
            return
        name = args[0]
        self.sysmgr.remove_source(name)

    def do_list_sources(self, line):
        """
        list_sources

        List all currently registered sources.

        Arguments:

            (none)

        Example:

            list_sources
        """

        args = line.split()
        if len(args) != 0:
            log.error("Incorrect number of args!")
            return
        self.sysmgr.list_sources()

    def do_show_source(self, line):
        """
        show_source NAME

        Show details of a previously registered source in JSON format.

        Arguments:

            NAME    The identifier of the source to show.

        Example:

            show_source oryx
        """

        args = line.split()
        if len(args) != 1:
            log.error("Incorrect number of args!")
            return
        name = args[0]
        self.sysmgr.show_source(name)

    def do_add_guest(self, line):
        """
        add_guest NAME IMAGE CONFIG_PATH

        Create a new guest container from an image.

        Arguments:

            NAME    An identifier which may be used to reference this source in
                    future commands.

            IMAGE   A fully-qualified reference to an image which is available
                    from one of the sources which has been configured. The
                    format of this reference is "<source>:<image name>".

            CONFIG_PATH
                    The path to a configuration file in JSON format which
                    contains any settings to be applied for this guest.

        Example:

            add_guest test oryx:minimal config.json
        """
        args = line.split()
        if len(args) != 3:
            log.error("Incorrect number of args!")
            return
        (name, image, config_path) = args

        with open(config_path, 'r') as fp:
            config = json.load(fp)

        self.sysmgr.add_guest(name, image, config)

    def do_remove_guest(self, line):
        """
        remove_guest NAME

        Delete an existing guest container.

        Arguments:

            NAME    The identifier of the guest container to remove.

        Example:

            remove_guest test
        """
        args = line.split()
        if len(args) != 1:
            log.error("Incorrect number of args!")
            return
        name = args[0]

        self.sysmgr.remove_guest(name)

    def do_reconfigure_guest(self, line):
        """
        reconfigure_guest NAME CONFIG_PATH

        Replace the configuration of an existing guest container.

        Arguments:

            NAME    The identifier of the guest container to reconfigure.

            CONFIG_PATH
                    The path to a configuration file in JSON format which
                    contains any settings to be applied for this guest. The
                    settings in this file will replace all settings previously
                    applied to the guest.

        Example:

            reconfigure_guest test newconfig.json
        """
        args = line.split()
        if len(args) != 2:
            log.error("Incorrect number of args!")
            return
        (name, config_path) = args

        with open(config_path, 'r') as fp:
            config = json.load(fp)

        self.sysmgr.reconfigure_guest(name, config)

    def do_runc(self, line):
        """
        runc NAME ARGS...

        Execute 'runc' for an existing guest container. See the documentation of
        'runc' for further details.

        Arguments:

            NAME    The identifier of the guest container for which 'runc' will
                    be executed.

            ARGS... Command line arguments passed through to the 'runc'
                    application.

        Example:

            runc test spec
        """
        args = line.split()
        if len(args) < 1:
            log.error("Incorrect number of args!")
            return
        name = args[0]
        runc_args = args[1:]

        self.sysmgr.runc(name, runc_args)

    def do_version(self, line):
        """
        version

        Display version information.
        """
        print("%s (%s)" % (APP_NAME, VERSION_STRING))

    def do_exit(self, line):
        """
        exit

        Exit the interactive oryxcmd shell.
        """
        return True

if __name__ == '__main__':
    oryxcmd = OryxCmd()
    if len(sys.argv) > 1:
        # Convert common option-style arguments into commands by stripping the
        # leading '--'
        if sys.argv[1] in ("--help", "--version"):
            sys.argv[1] = sys.argv[1][2:]

        line = ' '.join(sys.argv[1:])
        oryxcmd.onecmd(line)
    else:
        oryxcmd.cmdloop()
