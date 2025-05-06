import hashlib
import secrets
import base64
from typing import Tuple
from passlib.context import CryptContext

# 创建passlib上下文，用于密码哈希和验证
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """
    使用 bcrypt 算法对密码进行哈希
    
    Args:
        password: 要加密的原始密码
        
    Returns:
        str: 加密后的密码哈希
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码是否与哈希值匹配
    
    Args:
        plain_password: 原始密码
        hashed_password: 存储的密码哈希
        
    Returns:
        bool: 验证是否成功
    """
    return pwd_context.verify(plain_password, hashed_password)


def generate_salt(length: int = 16) -> str:
    """
    生成随机盐值
    
    Args:
        length: 盐值长度 (默认16字节)
        
    Returns:
        str: base64编码的盐值
    """
    return base64.b64encode(secrets.token_bytes(length)).decode('utf-8')


def hash_password_with_salt(password: str, salt: str = None) -> Tuple[str, str]:
    """
    使用自定义盐值对密码进行哈希 (SHA-256)
    
    Args:
        password: 要加密的原始密码
        salt: 可选的自定义盐值，如果不提供则生成新的
        
    Returns:
        Tuple[str, str]: (哈希密码, 盐值)
    """
    if salt is None:
        salt = generate_salt()
    
    # 组合密码和盐值
    salted_password = password + salt
    
    # 使用SHA-256进行哈希
    hashed = hashlib.sha256(salted_password.encode('utf-8')).hexdigest()
    
    return hashed, salt


def verify_password_with_salt(password: str, stored_hash: str, salt: str) -> bool:
    """
    验证带盐值的密码
    
    Args:
        password: 原始密码
        stored_hash: 存储的密码哈希
        salt: 存储的盐值
        
    Returns:
        bool: 验证是否成功
    """
    # 计算哈希
    calculated_hash, _ = hash_password_with_salt(password, salt)
    
    # 比较哈希值
    return secrets.compare_digest(calculated_hash, stored_hash)


class PasswordManager:
    """密码管理器类，封装密码哈希和验证功能"""
    
    @staticmethod
    def hash(password: str) -> str:
        """使用bcrypt对密码进行哈希"""
        return hash_password(password)
    
    @staticmethod
    def verify(plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        return verify_password(plain_password, hashed_password)
    
    @staticmethod
    def hash_with_salt(password: str) -> Tuple[str, str]:
        """使用自定义盐值进行哈希"""
        return hash_password_with_salt(password)
    
    @staticmethod
    def verify_with_salt(password: str, stored_hash: str, salt: str) -> bool:
        """验证带盐值的密码"""
        return verify_password_with_salt(password, stored_hash, salt) 