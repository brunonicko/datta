from __future__ import absolute_import, division, print_function

import pytest

from datta import Data, Field, Constant


def test_datta():
    class Point(Data):
        x = Field()
        y = Field()

    point = Point(3, 4)
    assert point == Point(3, 4)


def test_fields():
    class A(Data):
        x = Field()

    class B(A):
        y = Field()

    class C(B):
        z = Field()

    assert list(C.__fields__.items()) == [("x", A.__fields__["x"]), ("y", B.__fields__["y"]), ("z", C.__fields__["z"])]

    with pytest.raises(TypeError):

        class D(C):
            x = 0

        assert not D


def test_constants():
    class Circle(Data):
        PI = Constant(3.14)
        radius = Field(float)

        @property
        def circumference(self):
            return 2 * self.PI * self.radius

    circle = Circle(3.0)
    assert circle.circumference == 18.84

    with pytest.raises(AttributeError):
        Circle.PI = 5

    with pytest.raises(AttributeError):
        circle.PI = 5


if __name__ == "__main__":
    pytest.main()
