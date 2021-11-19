from main import *

import unittest


class can_exit_testCase(unittest.TestCase):
    def test1(self):
        self.assertEqual(can_exit_no_visual([
  [0, 1, 1, 1, 1, 1, 1],
  [0, 0, 1, 1, 0, 1, 1],
  [1, 0, 0, 0, 0, 1, 1],
  [1, 1, 1, 1, 0, 0, 1],
  [1, 1, 1, 1, 1, 0, 0]
]), True)


if __name__ == '__main__':
    try:
        unittest.main()
    except:
        pass