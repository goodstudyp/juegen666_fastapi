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
    """
    分页信息类
    
    Attributes:
        total: 总记录数
        page: 当前页码
        page_size: 每页记录数
        total_pages: 总页数
    """
    total: Optional[int] = None
    page: int = 1
    page_size: int = 10
    total_pages: Optional[int] = None


class PaginationResponse(BaseModel, Generic[T]):
    """
    分页响应类
    
    Attributes:
        items: 分页数据列表
        page_info: 分页信息对象
    """
    items: List[T]
    page_info: PageInfo
    
    class Config:
        from_attributes = True


async def paginate_tortoise(
    query_set: QuerySet[M],
    page: int = 1,
    page_size: int = 10,
    schema_model: Optional[type[S]] = None,
    transform_func: Optional[Callable[[M], Any]] = None,
    filters: Optional[Dict[str, Any]] = None
) -> PaginationResponse:
    """
    对Tortoise ORM的查询集进行分页处理
    
    Args:
        query_set: Tortoise ORM查询集
        page: 页码, 默认为1
        page_size: 每页记录数, 默认为10
        schema_model: 用于转换数据的Pydantic模型
        transform_func: 自定义的数据转换函数
        filters: 过滤条件字典
        
    Returns:
        PaginationResponse: 包含分页数据和分页信息的响应对象
    """
    # 应用过滤条件
    if filters:
        filter_conditions = build_tortoise_filters(filters)
        if filter_conditions:
            query_set = query_set.filter(filter_conditions)
    
    # 计算总记录数
    total = await query_set.count()
    total_pages = ceil(total / page_size) if total > 0 else 1
    
    # 纠正页码
    if page < 1:
        page = 1
    if page > total_pages and total > 0:
        page = total_pages
    
    # 应用分页
    offset = (page - 1) * page_size
    query_set = query_set.offset(offset).limit(page_size)
    
    # 获取数据
    db_items = await query_set
    
    # 转换数据
    if transform_func:
        items = [transform_func(item) for item in db_items]
    elif schema_model:
        items = [schema_model.model_validate(item, from_attributes=True) for item in db_items]
    else:
        items = db_items
    
    # 创建分页信息
    page_info = PageInfo(
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )
    
    # 返回分页响应
    return PaginationResponse(items=items, page_info=page_info)


async def get_paginated_response(
    query_set: QuerySet[M],
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页记录数"),
    schema_model: Optional[type[S]] = None,
    transform_func: Optional[Callable[[M], Any]] = None,
    filters: Optional[Dict[str, Any]] = None
) -> PaginationResponse:
    """
    获取分页响应的便捷函数，可直接在路由处理器中使用
    
    Args:
        query_set: Tortoise ORM查询集
        page: 页码，默认为1
        page_size: 每页记录数，默认为10
        schema_model: 用于转换数据的Pydantic模型
        transform_func: 自定义的数据转换函数
        filters: 过滤条件字典
        
    Returns:
        PaginationResponse: 包含分页数据和分页信息的响应对象
    """
    return await paginate_tortoise(
        query_set=query_set,
        page=page,
        page_size=page_size,
        schema_model=schema_model,
        transform_func=transform_func,
        filters=filters
    )


def build_tortoise_filters(filters: Dict[str, Any]) -> Optional[Q]:
    """
    根据字典构建Tortoise ORM的过滤条件
    
    Args:
        filters: 过滤条件字典，格式为 {field__operator: value}
                支持的操作符: eq, ne, gt, gte, lt, lte, in, not_in, contains, icontains,
                              startswith, istartswith, endswith, iendswith, isnull
                
    Returns:
        Optional[Q]: Tortoise ORM的Q对象过滤条件
    """
    if not filters:
        return None
    
    q_filters = Q()
    for key, value in filters.items():
        # 忽略None值的过滤条件，除非操作符是isnull
        if value is None and not key.endswith('__isnull'):
            continue
            
        q_filters &= Q(**{key: value})
    
    return q_filters 