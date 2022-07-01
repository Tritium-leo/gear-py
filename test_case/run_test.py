import os
import unittest
from pathlib import Path

TEST_ROOT = Path(__file__).parent

if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    for add in os.listdir(TEST_ROOT):
        p = TEST_ROOT.joinpath(add)
        if p.is_dir() and not add.startswith("__"):
            discover = unittest.defaultTestLoader.discover(p, "test*.py")
            result = runner.run(discover)
            if len(result.errors) > 0:
                print("FIND ERROR!")
                break
