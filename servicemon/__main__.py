import sys
from servicemon.run_utils import Runner

if __name__ == "__main__":
    runner = Runner()
    runner.run_cl(sys.argv[1:])