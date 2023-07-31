from math import ceil
from typing import Any, Generic, TypeVar
from collections.abc import Sequence
from fastapi_pagination import Params, Page
from fastapi_pagination.bases import AbstractPage, AbstractParams
from pydantic import Field
from pydantic.generics import GenericModel

DataType = TypeVar("DataType")
T = TypeVar("T")

class IPaginatedResponse(Page[T], Generic[T]):
    previous_page: int | None = Field(
        None, description="Page number of the previous page"
    )
    next_page: int | None = Field(None, description="Page number of the next page")

    __params_type__ = Params  # Set params related to Page

    @classmethod
    def create(
        cls,
        items: Sequence[T],
        total: int,
        params: AbstractParams,
    ) -> "IPaginatedResponse":
        if params.size is not None and total is not None and params.size != 0:
            pages = ceil(total / params.size)
        else:
            pages = 0

        return cls(
                items=items,
                page=params.page,
                size=params.size,
                total=total,
                pages=pages,
                next_page=params.page + 1 if params.page < pages else None,
                previous_page=params.page - 1 if params.page > 1 else None,
        )
