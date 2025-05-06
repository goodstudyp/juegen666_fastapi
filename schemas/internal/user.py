from typing import Optional, List, Generic, TypeVar, Dict, Any
from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime
from model.enum.user import UserType, UserStatus, SexType
from fastapi import Query



# 登录请求模型
class LoginRequest(BaseModel):
    username: str
    password: str


# 创建用户请求模型
class CreateUserRequest(BaseModel):
    username: str = Field(max_length=11)
    password: str = Field(max_length=20)
    nickname: Optional[str] = None
    user_type: UserType = UserType.NORMAL
    user_status: UserStatus = UserStatus.ACTIVE
    sex: Optional[SexType] = SexType.MALE
    remarks: Optional[str] = None
    user_phone: Optional[str] = None
    user_email: Optional[EmailStr] = None
    client_host: Optional[str] = None
    
    


# 更新用户请求模型
class UpdateUserRequest(BaseModel):
    username: Optional[str] = Field(max_length=11)
    password: Optional[str] = Field(max_length=20)
    nickname: Optional[str] = None
    user_type: Optional[UserType] = None
    user_status: Optional[UserStatus] = None
    sex: Optional[SexType] = None
    remarks: Optional[str] = None
    user_phone: Optional[str] = None
    user_email: Optional[EmailStr] = None
    client_host: Optional[str] = None
    

# 用户列表请求模型
class UserListRequest(BaseModel):
    page: int = Field(1, ge=1, description="页码，从1开始")
    page_size: int = Field(10, ge=1, le=100, description="每页条数")
    username: Optional[str] = None
    nickname: Optional[str] = None
    user_type: Optional[UserType] = None
    user_status: Optional[UserStatus] = None
    user_phone: Optional[str] = None
    user_email: Optional[str] = None
    sex: Optional[SexType] = None


# 单个用户列表项响应模型
class UserListItem(BaseModel):
    id: int
    username: str
    nickname: Optional[str] = None
    user_type: UserType
    user_status: UserStatus
    user_phone: Optional[str] = None
    user_email: Optional[EmailStr] = None
    avatar: Optional[str] = None
    
    class Config:
        from_attributes = True
        use_enum_values = True


# Token信息模型
class TokenPayload(BaseModel):
    user_id: int
    user_type: int 
    exp: Optional[datetime] = None














