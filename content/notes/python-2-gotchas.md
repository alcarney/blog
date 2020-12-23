+++
description = "Differences that trip me up as I'm used to Python 3.x"
tags = ["python"]
title = "Python 2.x Gotchas"
+++

While at the time of writing (May 2019) the death of Python 2 is just around the
corner since I'm working in an enterprise environment I'm sure I will be dealing
with Python 2.x code for some time to come. To that end here are some gotchas to
keep in mind.


## Missing Features {#missing-features}

In the 10+ years since Python 3's release it's not surprising that it has
accumlated a large list of features that simply don't exist in Python 2.x


### No enum module {#no-enum-module}

The `enum` module was added in Python 3.4. In order to make use of this module
in versions of Python older than this we can install the [enum34](https://pypi.org/project/enum34/) package from
PyPi.

{{< highlight sh >}}
$ pip install enum34
{{< /highlight >}}

Code that uses the standard `enum` module should now work as is.

**Note:** It would seem that this package is not actively maintained with the most
 recent change being in 2016 at the time of writing.


### No pathlib module {#no-pathlib-module}

The `pathlib` module was added in Python 3.4. In order to make use of this
module in older versions of Python we can install the [pathlib2](https://pypi.org/project/pathlib2/) package on PyPi

{{< highlight sh >}}
$ pip install pathlib2
{{< /highlight >}}

Then code written for the standard `pathlib` module should work as expected.


### No FileNotFoundErrors {#no-filenotfounderrors}

Not sure when these were added. If you simply want to be able to throw one it's
easy enough to backport one yourself

{{< highlight python >}}
class FileNotFoundError(OSError):
    pass
{{< /highlight >}}


## Moved / Changed Features {#moved-changed-features}

There are a number of features that did exist in Python 2.x but were
renamed/moved or tweaked in someway in Python 3.x so that they are not directly
compatible with older interpreters anymore


### configparser is ConfigParser {#configparser-is-configparser}

Before Python 3 the `configparser` module was called `ConfigParser`, I'm
struggling to see if there are any functional differences between the two
versions but there is a actively maintained [configparser](https://pypi.org/project/configparser/) package available which
has apparently backported a number of changes to older versions of Python

{{< highlight sh >}}
$ pip install configparser
{{< /highlight >}}

In theory code using the standard `configparser` module will "just work".


## Best Practice {#best-practice}

Here is a miscellaneous collection things to do when writing code that will run
under Python 2.x that should hopefully minimise the amount of surprises!


### Use new style classes {#use-new-style-classes}

In Python 2.x new style classes are an explicit opt-in

{{< highlight python >}}
class MyClass(object):
    ...
{{< /highlight >}}


### Define both `__eq__` and `__ne__` {#define-both-eq-and-ne}

When creating a class that you wish to define equality for you need to ensure
that you define both the `__eq__` and `__ne__` special methods for your class to
have the behavior you would expect it to.

In Python 2.x the default implementation of `__ne__` is something like the
following.

{{< highlight python >}}
def __ne__(self, other):
    return not (self is other)
{{< /highlight >}}

For your class to behave as expected you will need to define it as follows

{{< highlight python >}}
class MyClass(object):
    ...

    def __eq__(self, other):
        ...

    def __ne__(self, other):
        return not self.__eq__(other)
{{< /highlight >}}


### str != str {#str-str}

In Python 3 the string related datatypes were overhauled to include built-in
support for unicode character encodings. This means that the `str` type in
Python 2.x is **not** equivalent to the `str` type in Python 3.x

So if you want to check that some value is an instance of the type `str` the
best way is to make use the `six` compatibility package

{{< highlight sh >}}
$ pip install six
{{< /highlight >}}

And to use the following code

{{< highlight python >}}
import six

if isinstance(value, six.string_types):
    ...
{{< /highlight >}}