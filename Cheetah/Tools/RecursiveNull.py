"""
Nothing, but in a friendly way.  Good for filling in for objects you want to
hide.  If $form.f1 is a RecursiveNull object, then
$form.f1.anything["you"].might("use") will resolve to the empty string.

This module was contributed by Ian Bicking.
"""

import sys
PY2 = sys.version_info[0] < 3
del sys


class RecursiveNull(object):

    def __getattr__(self, attr):
        return self

    def __getitem__(self, item):
        return self

    def __call__(self, *args, **kwargs):
        return self

    def __str__(self):
        return ""

    def __repr__(self):
        return ""

    if PY2:
        def __nonzero__(self):
            return False
    else:
        def __bool__(self):
            return False

    def __eq__(self, x):
        if x:
            return False
        else:
            return True

    def __ne__(self, x):
        if x:
            return True
        else:
            return False


del PY2
