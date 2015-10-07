import sys
import unittest
try:
    from teamcity import is_running_under_teamcity
    from teamcity.unittestpy import TeamcityTestRunner
    runner = TeamcityTestRunner() if is_running_under_teamcity() else unittest.TextTestRunner()
except ImportError:
    runner = unittest.TextTestRunner()

from tests import ExampleTest


tests = {
    "ExampleTest": ExampleTest
}

if __name__ == "__main__":
    from application import application
    application.start_testing()
    test_name = sys.argv[1] if len(sys.argv) > 1 else None
    tests = tuple(
        [
            unittest.loader.findTestCases(tests[test_suit_name])
            for test_suit_name in tests
            if test_suit_name == test_name or not test_name
        ]
    )
    sys.exit(not runner.run(unittest.TestSuite(tests=tests)).wasSuccessful())
