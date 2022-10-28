Datta
=====
.. image:: https://github.com/brunonicko/datta/workflows/MyPy/badge.svg
   :target: https://github.com/brunonicko/datta/actions?query=workflow%3AMyPy

.. image:: https://github.com/brunonicko/datta/workflows/Lint/badge.svg
   :target: https://github.com/brunonicko/datta/actions?query=workflow%3ALint

.. image:: https://github.com/brunonicko/datta/workflows/Tests/badge.svg
   :target: https://github.com/brunonicko/datta/actions?query=workflow%3ATests

.. image:: https://readthedocs.org/projects/datta/badge/?version=stable
   :target: https://datta.readthedocs.io/en/stable/

.. image:: https://img.shields.io/github/license/brunonicko/datta?color=light-green
   :target: https://github.com/brunonicko/datta/blob/main/LICENSE

.. image:: https://static.pepy.tech/personalized-badge/datta?period=total&units=international_system&left_color=grey&right_color=brightgreen&left_text=Downloads
   :target: https://pepy.tech/project/datta

.. image:: https://img.shields.io/pypi/pyversions/datta?color=light-green&style=flat
   :target: https://pypi.org/project/datta/

Overview
--------
`Datta` is a simple implementation of Slotted Data Classes compatible with Python 2.7 and 3.7+.

.. code:: python

    >>> from datta import Data, attribute
    >>> class Point(Data):
    ...     x = attribute(types=int)
    ...     y = attribute(types=int)
    ...
    >>> point = Point(3, 4)
