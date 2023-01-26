#! /usr/bin/env python3
#
# possumcmd tests.
#
# Copyright (C) 2018-2019 Togán Labs
# SPDX-License-Identifier: MIT
#

# Disable a bunch of pylint checks for now
# pylint: disable=missing-docstring,no-self-use,fixme,invalid-name

import json
import os
import shutil
import subprocess
import sys
import unittest

from betatest.amtest import AMTestRunner

def run_common(cmd, capture, combine_capture, kwargs):
    if capture:
        kwargs['stdout'] = subprocess.PIPE
        if combine_capture:
            kwargs['stderr'] = subprocess.STDOUT
        else:
            kwargs['stderr'] = subprocess.PIPE
    kwargs['shell'] = True
    return subprocess.run(cmd, **kwargs)

class PossumTestCase(unittest.TestCase):
    def setUp(self):
        self.app_name = 'possumcmd'
        self.version_string = '%%VERSION_STRING%%'
        try:
            self.source = os.environ['POSSUMCMD_TEST_SOURCE']
        except KeyError:
            raise Exception('Set POSSUMCMD_TEST_SOURCE environment variable and try again.')

    def __str__(self):
        return "%s: %s" % (str(sys.argv[0]), self._testMethodName)

    def assertRunSuccess(self, cmd, capture=False, combine_capture=False, **kwargs):
        """Run a command and assert that it succeeds"""
        rc = run_common(cmd, capture, combine_capture, kwargs)
        self.assertEqual(rc.returncode, 0)
        return rc

    def assertRunFail(self, cmd, capture=False, combine_capture=False, **kwargs):
        """Run a command and assert that it fails"""
        rc = run_common(cmd, capture, combine_capture, kwargs)
        self.assertNotEqual(rc.returncode, 0)
        return rc

class PossumTests(PossumTestCase):
    def test_version(self):
        rc = self.assertRunSuccess('possumcmd version', capture=True)
        possumcmd_output = rc.stdout.decode('utf-8').strip()
        self.assertIn(self.app_name, possumcmd_output)
        self.assertIn(self.version_string, possumcmd_output)

    def test_help(self):
        # Let's just test the command succeeds and output is not empty
        rc = self.assertRunSuccess('possumcmd help', capture=True)
        possumcmd_output = rc.stdout.decode('utf-8').strip()
        self.assertTrue(len(possumcmd_output))

    def test_main(self):
        # For now this is one big sequential test case to keep things simple. We
        # should break it out into separate cases later.

        # We need to reset into a clean state to remove any sources and guests
        # added by preconfiguration.
        self.assertRunSuccess('possumcmd shutdown')
        self.assertRunSuccess('netns rm')
        shutil.rmtree('/var/lib/possum-guests')
        shutil.rmtree('/run/github.com/genuinetools/netns')

        # Check no sources are registered at first
        rc = self.assertRunSuccess('possumcmd list_sources', capture=True)
        possumcmd_output = rc.stdout.decode('utf-8').strip()
        self.assertEqual(len(possumcmd_output), 0)

        # Add a source
        self.assertRunSuccess('possumcmd add_source possum %s' % (self.source))

        # Check we now have one source named 'possum'
        rc = self.assertRunSuccess('possumcmd list_sources', capture=True)
        possumcmd_output = rc.stdout.decode('utf-8').strip()
        self.assertEqual(possumcmd_output, 'possum')

        # Check the source url is correct
        rc = self.assertRunSuccess('possumcmd show_source possum', capture=True)
        possumcmd_output = rc.stdout.decode('utf-8').strip()
        state = json.loads(possumcmd_output)
        self.assertEqual(state['url'], self.source)

        # Check no guests are registered at first
        rc = self.assertRunSuccess('possumcmd list_guests', capture=True)
        possumcmd_output = rc.stdout.decode('utf-8').strip()
        self.assertEqual(len(possumcmd_output), 0)

        # Add a guest
        self.assertRunSuccess('possumcmd add_guest test possum:minimal')

        # Check we now have one guest named 'test'
        rc = self.assertRunSuccess('possumcmd list_guests', capture=True)
        possumcmd_output = rc.stdout.decode('utf-8').strip()
        self.assertEqual(possumcmd_output, 'test')

        # Check the guest details are correct
        rc = self.assertRunSuccess('possumcmd show_guest test', capture=True)
        possumcmd_output = rc.stdout.decode('utf-8').strip()
        state = json.loads(possumcmd_output)
        self.assertEqual(state['source_name'], 'possum')
        self.assertEqual(state['image_name'], 'minimal')
        self.assertEqual(state['autostart_enabled'], 0)

        # Enable autostart for the guest
        self.assertRunSuccess('possumcmd enable_guest test')

        # Check the guest details have been updated
        rc = self.assertRunSuccess('possumcmd show_guest test', capture=True)
        possumcmd_output = rc.stdout.decode('utf-8').strip()
        state = json.loads(possumcmd_output)
        self.assertEqual(state['autostart_enabled'], 1)

        # Disable autostart for the guest
        self.assertRunSuccess('possumcmd disable_guest test')

        # Check the guest details have been updated
        rc = self.assertRunSuccess('possumcmd show_guest test', capture=True)
        possumcmd_output = rc.stdout.decode('utf-8').strip()
        state = json.loads(possumcmd_output)
        self.assertEqual(state['autostart_enabled'], 0)

        # TODO: Test ssh - guest should be inaccessible
        # (https://gitlab.com/possum/possum/issues/43)
        self.assertRunFail('ping -c 3 172.19.0.2')

        # Start the guest
        self.assertRunSuccess('possumcmd start_guest test')

        # TODO: Test ssh - guest should be accessible
        # (https://gitlab.com/possum/possum/issues/43)
        self.assertRunSuccess('ping -c 3 172.19.0.2')

        # Stop the guest
        self.assertRunSuccess('possumcmd stop_guest test')

        # TODO: Test ssh - guest should be inaccessible
        # (https://gitlab.com/possum/possum/issues/43)
        self.assertRunFail('ping -c 3 172.19.0.2')

        # Remove guest
        self.assertRunSuccess('possumcmd remove_guest test')

        # Check no guests are registered now
        rc = self.assertRunSuccess('possumcmd list_guests', capture=True)
        possumcmd_output = rc.stdout.decode('utf-8').strip()
        self.assertEqual(len(possumcmd_output), 0)

        # Remove source
        self.assertRunSuccess('possumcmd remove_source possum')

        # Check no sources are registered now
        rc = self.assertRunSuccess('possumcmd list_sources', capture=True)
        possumcmd_output = rc.stdout.decode('utf-8').strip()
        self.assertEqual(len(possumcmd_output), 0)

if __name__ == '__main__':
    unittest.main(testRunner=AMTestRunner())
