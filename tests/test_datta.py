from __future__ import absolute_import, division, print_function

import pytest

from datta import Data, Field


def test_datta():
    class Point(Data):
        x = Field()
        y = Field()

    point = Point(3, 4)
    assert point == Point(3, 4)


if __name__ == "__main__":
    pytest.main()
