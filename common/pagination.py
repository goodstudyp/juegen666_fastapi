from typing import TypeVar, Generic, List, Optional, Dict, Any, Callable, Union
from tortoise.models import Model
from tortoise.queryset import QuerySet
from tortoise.expressions import Q
from pydantic import BaseModel
from math import ceil
from fastapi import Query

T = TypeVar('T')
M = TypeVar('M', bound=Model)
S = TypeVar('S', bound=BaseModel)


class PageInfo(BaseModel):
    total: Optional[int] = None
    page: int = 1
    page_size: int = 10
    total_pages: Optional[int] = None


class PaginationResponse(BaseModel, Generic[T]):
    items: List[T]
    page_info: PageInfo

    class Config:
        from_attributes = True


def build_tortoise_filters(filters: Dict[str, Any]) -> Optional[Q]:
    if not filters:
        return None
    q_filters = Q()
    for key, value in filters.items():
        if value is None and not key.endswith('__isnull'):
            continue
        q_filters &= Q(**{key: value})
    return q_filters


async def paginate_tortoise(
    query_set: QuerySet[M],
    page: int = 1,
    page_size: int = 10,
    schema_model: Optional[type[S]] = None,
    transform_func: Optional[Callable[[M], Any]] = None,
    filters: Optional[Dict[str, Any]] = None,
    select_related: Optional[List[str]] = None,
    prefetch_related: Optional[List[str]] = None
) -> PaginationResponse:
    if select_related:
        query_set = query_set.select_related(*select_related)
    if prefetch_related:
        query_set = query_set.prefetch_related(*prefetch_related)

    if filters:
        filter_conditions = build_tortoise_filters(filters)
        if filter_conditions:
            query_set = query_set.filter(filter_conditions)

    total = await query_set.count()
    total_pages = ceil(total / page_size) if total > 0 else 1

    page = max(1, min(page, total_pages))

    offset = (page - 1) * page_size
    query_set = query_set.offset(offset).limit(page_size)

    db_items = await query_set

    if transform_func:
        items = [transform_func(item) for item in db_items]
    elif schema_model:
        items = [schema_model.model_validate(item, from_attributes=True) for item in db_items]
    else:
        items = db_items

    page_info = PageInfo(
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )

    return PaginationResponse(items=items, page_info=page_info)


async def get_paginated_response(
    query_set: QuerySet[M],
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页记录数"),
    schema_model: Optional[type[S]] = None,
    transform_func: Optional[Callable[[M], Any]] = None,
    filters: Optional[Dict[str, Any]] = None,
    select_related: Optional[List[str]] = None,
    prefetch_related: Optional[List[str]] = None
) -> PaginationResponse:
    return await paginate_tortoise(
        query_set=query_set,
        page=page,
        page_size=page_size,
        schema_model=schema_model,
        transform_func=transform_func,
        filters=filters,
        select_related=select_related,
        prefetch_related=prefetch_related
    )
