from tortoise import fields
class TimestampMixin:
    """
    时间戳混合类 (Tortoise ORM version)
    自动添加创建和更新时间
    """
    create_time: fields.DatetimeField = fields.DatetimeField(
        auto_now_add=True, description='创建时间'
    )
    update_time: fields.DatetimeField = fields.DatetimeField(
        auto_now=True, description="更新时间"
    )
    # Note: Tortoise handles default factory and onupdate via auto_now_add and auto_now
