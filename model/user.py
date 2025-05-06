from model.base import TimestampMixin
from tortoise import fields, models
from model.operation_log import OperationLog

# --- 用户模型 (Tortoise ORM version) ---

class User(TimestampMixin, models.Model):
    """
    用户模型 (Tortoise ORM version)
    """
    id: fields.IntField = fields.IntField(pk=True) # Tortoise adds 'id' automatically if no pk is defined, but explicit is often clearer.
    username: fields.CharField = fields.CharField(
        max_length=20, unique=True, index=True, description="用户名"
    )
    password: fields.CharField = fields.CharField(
        max_length=255, description="密码哈希"
    ) # Store hash, not plain text
    nickname: fields.CharField = fields.CharField(
        max_length=20, null=True, default=None, description='昵称'
    )
    user_type: fields.IntField = fields.IntField(
        default=2, description="用户类型 超级管理员0 管理员1 普通2"
    )
    user_email: fields.CharField = fields.CharField(
        max_length=255, unique=True, index=True, null=True, default=None, description='邮箱'
    )
    user_status: fields.IntField = fields.IntField(
        default=1, description='0未激活 1正常 2禁用'
    )
    user_phone: fields.CharField = fields.CharField(
        max_length=11, unique=True, index=True, null=True, default=None, description="手机号"
    )
    login_time: fields.DatetimeField = fields.DatetimeField(
        null=True, default=None, description="最后登录时间"
    )
    avatar: fields.CharField = fields.CharField(
        max_length=255, null=True, default=None, description='头像URL'
    )
    sex: fields.IntField = fields.IntField(
        null=True, default=None, description='性别 1男 2女 0未知'
    )
    remarks: fields.CharField = fields.CharField(
        max_length=255, null=True, default=None, description="备注"
    ) # Consider fields.TextField if remarks can be very long
    client_host: fields.CharField = fields.CharField(
        max_length=45, null=True, default=None, description="最后登录IP"
    ) # Sufficient for IPv4, potentially short for IPv6 FQDNs, adjust if needed

    # 添加类型提示，这不会影响数据库结构，只用于代码提示
    operation_logs: fields.ReverseRelation["OperationLog"]

    class Meta:
        table = "user" # Explicitly set table name
        # If you had composite unique constraints in SQLModel's __table_args__ using UniqueConstraint,
        # you would define them here like:
        # unique_together = (("field1", "field2"),)
        ordering = ["id"] # Optional: default ordering

    def __str__(self) -> str:
        return self.username or f"User {self.id}" # For better representatio
    
class test(models.Model):
    id: fields.IntField = fields.IntField(pk=True)
    name: fields.CharField = fields.CharField(max_length=20)

    class Meta:
        table = "test"
        
