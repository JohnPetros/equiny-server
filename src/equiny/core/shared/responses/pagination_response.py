from collections.abc import Callable
from typing import TypeVar
from equiny.core.shared.domain.decorators import response

Item = TypeVar('Item')
Out = TypeVar('Out')


@response
class PaginationResponse[Item]:
    items: list[Item]
    next_cursor: str | None
    has_more: bool

    def map_items(self, mapper: Callable[[Item], Out]) -> 'PaginationResponse[Out]':
        return PaginationResponse[Out](
            items=[mapper(item) for item in self.items],
            next_cursor=self.next_cursor,
            has_more=self.has_more,
        )
