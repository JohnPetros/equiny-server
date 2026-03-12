from typing import Any


def __getattr__(name: str) -> Any:
    if name == 'Sqlalchemy':
        from .sqlalchemy import Sqlalchemy

        return Sqlalchemy

    message = f'module {__name__!r} has no attribute {name!r}'
    raise AttributeError(message)
