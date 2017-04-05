#!/usr/bin/env python

import unittest

from Cheetah import SettingsManager
from Cheetah.Version import convertVersionStringToTuple


class SettingsManagerTests(unittest.TestCase):

    def test_mergeDictionaries(self):
        left = {'foo' : 'bar', 'abc' : {'a' : 1, 'b' : 2, 'c' : (3,)}}
        right = {'xyz' : (10, 9)}
        expect = {'xyz': (10, 9), 'foo': 'bar', 'abc': {'a': 1, 'c': (3,), 'b': 2}}

        result = SettingsManager.mergeNestedDictionaries(left, right)
        self.assertEqual(result, expect)


class VersionTests(unittest.TestCase):

    def test_convertVersionStringToTuple(self):
        c = convertVersionStringToTuple

        assert c('2.0a1') == (2, 0, 0, 'alpha', 1)
        assert c('2.0b1') == (2, 0, 0, 'beta', 1)
        assert c('2.0rc1') == (2, 0, 0, 'candidate', 1)
        assert c('2.0') == (2, 0, 0, 'final', 0)
        assert c('2.0.2') == (2, 0, 2, 'final', 0)

        assert c('0.9.19b1') < c('0.9.19')
        assert c('0.9b1') < c('0.9.19')

        assert c('2.0a2') > c('2.0a1')
        assert c('2.0b1') > c('2.0a2')
        assert c('2.0b2') > c('2.0b1')
        assert c('2.0b2') == c('2.0b2')

        assert c('2.0rc1') > c('2.0b1')
        assert c('2.0rc2') > c('2.0rc1')
        assert c('2.0rc2') > c('2.0b1')

        assert c('2.0') > c('2.0a1')
        assert c('2.0') > c('2.0b1')
        assert c('2.0') > c('2.0rc1')
        assert c('2.0.1') > c('2.0')
        assert c('2.0rc1') > c('2.0b1')


if __name__ == '__main__':
    unittest.main()
