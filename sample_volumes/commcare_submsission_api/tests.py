#!/usr/bin/env python3
import doctest
import unittest
import submit_data


class DocTests(unittest.TestCase):

    def test_doctests(self):
        results = doctest.testmod(submit_data)
        self.assertEqual(results.failed, 0)


if __name__ == '__main__':
    unittest.main()
