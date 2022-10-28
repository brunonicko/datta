from __future__ import absolute_import, division, print_function

import math

import pytest
from datta import Data, attribute, getter


class Vector(Data):
    x = attribute(converter=float)
    y = attribute(converter=float)
    mag = attribute()  # type: float

    @getter(mag, dependencies=(x, y))
    def _(self):
        # type: () -> float
        return math.sqrt(self.x ** 2 + self.y ** 2)


def test_datta():
    vector = Vector(3, 4)
    assert repr(vector) == "Vector(3.0, 4.0, <mag=5.0>)"


if __name__ == "__main__":
    pytest.main()
