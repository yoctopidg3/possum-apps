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
    def __str__(self):
        return "%s: %s" % (str(sys.argv[0]), self._testMethodName)

class OryxTests(OryxTestCase):
    def test_dummy(self):
        self.assertIsNotNone(1)

if __name__ == '__main__':
    unittest.main(testRunner=OryxTestRunner())
