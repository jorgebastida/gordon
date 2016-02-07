import os
import sys
from gordon.utils_tests import delete_test_stacks


def main(region):
    os.environ['AWS_DEFAULT_REGION'] = region
    delete_test_stacks('')


if __name__ == '__main__':
    main(sys.argv[1])
