from __future__ import absolute_import, division, print_function

import math

import pytest
from datta import DataClass, data_attribute, data_relationship


class Vector(DataClass):
    x = data_attribute(relationship=data_relationship(float))
    y = data_attribute(relationship=data_relationship(float))
    mag = data_attribute()  # type: data_attribute[float]

    @mag.getter(x, y)
    def mag(self):
        # type: () -> float
        return math.sqrt(self.x ** 2 + self.y ** 2)


def test_datta():
    vector = Vector(3, 4)
    assert repr(vector) == "Vector(3.0, 4.0, <mag=5.0>)"


if __name__ == "__main__":
    pytest.main()
