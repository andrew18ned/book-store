import unittest

from store.logic import operation


class LogicTestCase(unittest.TestCase):
    def test_plus(self):
        result = operation(6, 13, '+')
        self.assertEqual(19, result)

    def test_minux(self):
        result = operation(6, 13, '-')
        self.assertEqual(-7, result)

    def test_multiply(self):
        result = operation(6, 13, '*')
        self.assertEqual(78, result)

