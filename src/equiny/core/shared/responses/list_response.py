from equiny.core.shared.domain.decorators.response import response


@response
class ListResponse[Item]:
    items: list[Item]
