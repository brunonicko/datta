from __future__ import absolute_import, division, print_function

import pytest

from datta import DataKwargs, Data, Field, Constant, evolve


def test_force_slots():
    class NonSlotted(object):
        pass

    class Derived(NonSlotted):
        __slots__ = ()

    class Point(Data):
        x = Field()
        y = Field()

    with pytest.raises(TypeError):

        class Vector(Point, Derived):
            pass

        assert not Vector


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
        __kwargs__ = DataKwargs(mutable=True)

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


def test_mutable():
    class Point(Data):
        x = Field()
        y = Field()

    point = Point(3, 4)
    with pytest.raises(AttributeError):
        point.x = 30

    new_point = evolve(point, x=30)
    assert isinstance(new_point, Point)
    assert new_point.x == 30
    assert point.x == 3

    class MutablePoint(Point):
        __kwargs__ = DataKwargs(mutable=True)
        x = Field()
        y = Field()

    mutable_point = MutablePoint(3, 4)
    mutable_point.x = 30
    assert mutable_point.x == 30


def test_type_checking():
    class Point(Data):
        x = Field(int)
        y = Field(int)

    point = Point(3, 4)

    with pytest.raises(TypeError):
        evolve(point, x=3.0)


if __name__ == "__main__":
    pytest.main()
