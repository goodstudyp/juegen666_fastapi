import enum
class UserType(enum.IntEnum):
    """用户类型枚举"""
    SUPER_ADMIN = 0 # 超级管理员
    ADMIN = 1       # 管理员
    NORMAL = 2      # 普通用户

class UserStatus(enum.IntEnum):
    """用户状态枚举"""
    
    ACTIVE = 1   # 正常
    DISABLED = 2 # 禁用

class SexType(enum.IntEnum):
    """性别类型枚举"""
    
    MALE = 1    # 男
    FEMALE = 2  # 女