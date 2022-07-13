from ._constant import Constant
from ._data import Data


class Base(object):
    pass


class Derived(Base):
    pass


class Point(Data):
    x = Constant(Base)


class X(Point):
    x = Constant(Derived)
