import sys
import unittest
try:
    from teamcity import is_running_under_teamcity
    from teamcity.unittestpy import TeamcityTestRunner
    runner = TeamcityTestRunner() if is_running_under_teamcity() else unittest.TextTestRunner()
except ImportError:
    runner = unittest.TextTestRunner()

from tests import ExampleTest

suite = unittest.TestSuite(tests=(
    unittest.loader.findTestCases(ExampleTest)
))

if __name__ == "__main__":
    from application import application
    application.start_testing()
    sys.exit(not runner.run(suite).wasSuccessful())