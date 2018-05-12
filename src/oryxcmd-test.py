#! /usr/bin/env python3
#
# oryxcmd tests.
#
# Copyright (C) 2018 Togán Labs
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

import json
import subprocess
import sys
import unittest

class OryxTestResult(unittest.TestResult):
    def __init__(self, runner):
        super(OryxTestResult, self).__init__()
        self.runner = runner

    def addError(self, test, err):
        super(OryxTestResult, self).addError(test, err)
        self.runner.write("ERROR: %s: %s\n" % (str(test), str(err[1])))
        import traceback
        traceback.print_tb(err[2])

    def addSuccess(self, test):
        super(OryxTestResult, self).addSuccess(test)
        self.runner.write("PASS: %s\n" % str(test))

    def addFailure(self, test, err):
        super(OryxTestResult, self).addFailure(test, err)
        self.runner.write("FAIL: %s: %s\n" % (str(test), str(err[1])))

    def addSkip(self, test, reason):
        super(OryxTestResult, self).addSkip(test, reason)
        self.runner.write("SKIP: %s: %s\n" % (str(test), str(reason)))

    def addExpectedFailure(self, test, err):
        super(OryxTestResult, self).addExpectedFailure(test, err)
        self.runner.write("XFAIL: %s\n" % (str(test)))

    def addUnexpectedSuccess(self, test):
        super(OryxTestResult, self).addUnexpectedSuccess(test)
        self.runner.write("XPASS: %s\n" % str(test))

class OryxTestRunner:
    def __init__(self, stream=sys.stderr):
        self.stream = stream

    def write(self, message):
        self.stream.write(message)

    def run(self, test):
        result = OryxTestResult(self)
        test(result)
        return result

class OryxTestCase(unittest.TestCase):
    def setUp(self):
        self.app_name = 'oryxcmd'
        self.version_string = '%%VERSION_STRING%%'

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

        # Start the guest
        self.assertRunSuccess('oryxcmd start_guest test')

        # TODO: Test ssh - guest should be accessible

        # Stop the guest
        self.assertRunSuccess('oryxcmd stop_guest test')

        # TODO: Test ssh - guest should be inaccessible

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
    unittest.main(testRunner=OryxTestRunner())
