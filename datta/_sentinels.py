from __future__ import absolute_import, division, print_function

from enum import Enum

from tippo import final

__all__ = ["MissingType", "MISSING", "DeleteType", "DELETE"]


@final
class MissingType(Enum):
    MISSING = "MISSING"


MISSING = MissingType.MISSING


@final
class DeleteType(Enum):
    DELETE = "DELETE"


DELETE = DeleteType.DELETE
