#! /usr/bin/env python3
#
# oryxcmd tests.
#
# Copyright (C) 2018-2019 Togán Labs
# SPDX-License-Identifier: MIT
#

import json
import os
import subprocess
import sys
import unittest

from betatest.amtest import AMTestRunner

class OryxTestCase(unittest.TestCase):
    def setUp(self):
        self.app_name = 'oryxcmd'
        self.version_string = '%%VERSION_STRING%%'
        try:
            self.source = os.environ['ORYXCMD_TEST_SOURCE']
        except KeyError:
            raise Exception('Set ORYXCMD_TEST_SOURCE environment variable and try again.')

    def __str__(self):
        return "%s: %s" % (str(sys.argv[0]), self._testMethodName)

    def _run_common(self, cmd, capture, combine_capture, kwargs):
        if capture:
            kwargs['stdout'] = subprocess.PIPE
            if combine_capture:
                kwargs['stderr'] = subprocess.STDOUT
            else:
                kwargs['stderr'] = subprocess.PIPE
        kwargs['shell'] = True
        return subprocess.run(cmd, **kwargs)

    def assertRunSuccess(self, cmd, capture=False, combine_capture=False, **kwargs):
        """Run a command and assert that it succeeds"""
        rc = self._run_common(cmd, capture, combine_capture, kwargs)
        self.assertEqual(rc.returncode, 0)
        return rc

    def assertRunFail(self, cmd, capture=False, combine_capture=False, **kwargs):
        """Run a command and assert that it fails"""
        rc = self._run_common(cmd, capture, combine_capture, kwargs)
        self.assertNotEqual(rc.returncode, 0)
        return rc

class OryxTests(OryxTestCase):
    def test_version(self):
        rc = self.assertRunSuccess('oryxcmd version', capture=True)
        oryxcmd_output = rc.stdout.decode('utf-8').strip()
        self.assertIn(self.app_name, oryxcmd_output)
        self.assertIn(self.version_string, oryxcmd_output)

    def test_help(self):
        # Let's just test the command succeeds and output is not empty
        rc = self.assertRunSuccess('oryxcmd help', capture=True)
        oryxcmd_output = rc.stdout.decode('utf-8').strip()
        self.assertTrue(len(oryxcmd_output))

    def test_main(self):
        # For now this is one big sequential test case to keep things simple. We
        # should break it out into separate cases later.

        # Check no sources are registered at first
        rc = self.assertRunSuccess('oryxcmd list_sources', capture=True)
        oryxcmd_output = rc.stdout.decode('utf-8').strip()
        self.assertEqual(len(oryxcmd_output), 0)

        # Add a source
        self.assertRunSuccess('oryxcmd add_source oryx %s' % (self.source))

        # Check we now have one source named 'oryx'
        rc = self.assertRunSuccess('oryxcmd list_sources', capture=True)
        oryxcmd_output = rc.stdout.decode('utf-8').strip()
        self.assertEqual(oryxcmd_output, 'oryx')

        # Check the source url is correct
        rc = self.assertRunSuccess('oryxcmd show_source oryx', capture=True)
        oryxcmd_output = rc.stdout.decode('utf-8').strip()
        state = json.loads(oryxcmd_output)
        self.assertEqual(state['url'], self.source)

        # Check no guests are registered at first
        rc = self.assertRunSuccess('oryxcmd list_guests', capture=True)
        oryxcmd_output = rc.stdout.decode('utf-8').strip()
        self.assertEqual(len(oryxcmd_output), 0)

        # Add a guest
        self.assertRunSuccess('oryxcmd add_guest test oryx:minimal')

        # Check we now have one guest named 'test'
        rc = self.assertRunSuccess('oryxcmd list_guests', capture=True)
        oryxcmd_output = rc.stdout.decode('utf-8').strip()
        self.assertEqual(oryxcmd_output, 'test')

        # Check the guest details are correct
        rc = self.assertRunSuccess('oryxcmd show_guest test', capture=True)
        oryxcmd_output = rc.stdout.decode('utf-8').strip()
        state = json.loads(oryxcmd_output)
        self.assertEqual(state['source_name'], 'oryx')
        self.assertEqual(state['image_name'], 'minimal')
        self.assertEqual(state['autostart_enabled'], 0)

        # Enable autostart for the guest
        self.assertRunSuccess('oryxcmd enable_guest test')

        # Check the guest details have been updated
        rc = self.assertRunSuccess('oryxcmd show_guest test', capture=True)
        oryxcmd_output = rc.stdout.decode('utf-8').strip()
        state = json.loads(oryxcmd_output)
        self.assertEqual(state['autostart_enabled'], 1)

        # Disable autostart for the guest
        self.assertRunSuccess('oryxcmd disable_guest test')

        # Check the guest details have been updated
        rc = self.assertRunSuccess('oryxcmd show_guest test', capture=True)
        oryxcmd_output = rc.stdout.decode('utf-8').strip()
        state = json.loads(oryxcmd_output)
        self.assertEqual(state['autostart_enabled'], 0)

        # TODO: Test ssh - guest should be inaccessible
        self.assertRunFail('ping -c 3 172.19.0.2')

        # Start the guest
        self.assertRunSuccess('oryxcmd start_guest test')

        # TODO: Test ssh - guest should be accessible
        self.assertRunSuccess('ping -c 3 172.19.0.2')

        # Stop the guest
        self.assertRunSuccess('oryxcmd stop_guest test')

        # TODO: Test ssh - guest should be inaccessible
        self.assertRunFail('ping -c 3 172.19.0.2')

        # Remove guest
        self.assertRunSuccess('oryxcmd remove_guest test')

        # Check no guests are registered now
        rc = self.assertRunSuccess('oryxcmd list_guests', capture=True)
        oryxcmd_output = rc.stdout.decode('utf-8').strip()
        self.assertEqual(len(oryxcmd_output), 0)

        # Remove source
        self.assertRunSuccess('oryxcmd remove_source oryx')

        # Check no sources are registered now
        rc = self.assertRunSuccess('oryxcmd list_sources', capture=True)
        oryxcmd_output = rc.stdout.decode('utf-8').strip()
        self.assertEqual(len(oryxcmd_output), 0)

if __name__ == '__main__':
    unittest.main(testRunner=AMTestRunner())
