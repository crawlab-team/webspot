import sys


def is_running_unit_tests():
    return 'unittest' in sys.modules or 'pytest' in sys.modules
