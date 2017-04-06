"""\
Provides helpers for Template.webInput(), a method for importing web
transaction variables in bulk.  See the docstring of webInput for full details.
"""

from .Misc import useOrRaise


class NonNumericInputError(ValueError):
    pass


##################################################
## PRIVATE FUNCTIONS AND CLASSES

class _Converter(object):
    """\
    A container object for info about type converters.
    .name, string, name of this converter (for error messages).
    .func, function, factory function.
    .default, value to use or raise if the real value is missing.
    .error, value to use or raise if .func() raises an exception.
    """

    def __init__(self, name, func, default, error):
        self.name = name
        self.func = func
        self.default = default
        self.error = error


def _lookup(name, func, multi, converters):
    """\
    Look up a Webware field/cookie/value/session value.  Return
    '(realName, value)' where 'realName' is like 'name' but with any
    conversion suffix strips off.  Applies numeric conversion and
    single vs multi values according to the comments in the source.
    """

    # Step 1 -- split off the conversion suffix from 'name'; e.g. "height:int".
    # If there's no colon, the suffix is "".  'longName' is the name with the
    # suffix, 'shortName' is without.
    # XXX This implementation assumes "height:" means "height".
    longName = name
    shortName, _, ext = name.partition(':')

    # Step 2 -- look up the values by calling 'func'.
    if longName != shortName:
        values = func(longName, None) or func(shortName, None)
    else:
        values = func(shortName, None)
    # 'values' is a list of strings, a string or None.

    # Step 3 -- Coerce 'values' to a list of zero, one or more strings.
    if values is None:
        values = []
    elif isinstance(values, str):
        values = [values]

    # Step 4 -- Find a _Converter object or raise TypeError.
    try:
        converter = converters[ext]
    except KeyError:
        raise TypeError("'%s' is not a valid converter "
                        "name in '%s'" % (ext, longName))

    # Step 5 -- if there's a converter func, run it on each element.
    # If the converter raises an exception, use or raise 'converter.error'.
    if converter.func is not None:
        tmp = values[:]
        values = []
        for elem in tmp:
            try:
                elem = converter.func(elem)
            except (TypeError, ValueError):
                errmsg = "%s '%s' contains invalid characters" % (converter.name, elem)
                elem = useOrRaise(converter.error, errmsg)
            values.append(elem)
    # 'values' is now a list of strings, ints or floats.

    # Step 6 -- If we're supposed to return a multi value, return the list
    # as is.  If we're supposed to return a single value and the list is
    # empty, return or raise 'converter.default'.  Otherwise, return the
    # first element in the list and ignore any additional values.
    if multi:
        return shortName, values
    if len(values) == 0:
        return shortName, useOrRaise(converter.default)
    else:
        return shortName, values[0]
