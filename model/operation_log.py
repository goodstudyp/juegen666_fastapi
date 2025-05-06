from tortoise import fields
from model.base import TimestampMixin
from tortoise.models import Model
from typing import TYPE_CHECKING, Optional

# 只在类型检查时导入User，运行时不导入
if TYPE_CHECKING:
    from model.user import User


class OperationLog(TimestampMixin, Model):
    __tablename__ = 'operation_log'

    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=50, nullable=False)
    operation = fields.CharField(max_length=255, nullable=False)
    result = fields.CharField(max_length=255, nullable=False)

    # 使用字符串形式的模型引用，不是直接导入
    user = fields.ForeignKeyField("models.User", related_name="operation_logs", on_delete=fields.CASCADE)

    class Meta:
        table = "operation_log"
        table_description = "操作日志"

    def __str__(self):
        return f"<OperationLog(id={self.id}, user_id={self.user_id}, username={self.username}, operation={self.operation}, result={self.result}, create_time={self.create_time})>"

