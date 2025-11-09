"""
通用工具函数
"""

import io
import hashlib


class CommonUtil:
    """通用工具类"""
    
    @staticmethod
    def file_to_bytes(file_path):
        """读取文件为字节数组"""
        with open(file_path, 'rb') as f:
            return f.read()
    
    @staticmethod
    def bytes_to_file(data, file_path):
        """将字节数组写入文件"""
        with open(file_path, 'wb') as f:
            f.write(data)
    
    @staticmethod
    def stream_to_bytes(stream):
        """将流转换为字节数组"""
        if isinstance(stream, bytes):
            return stream
        if hasattr(stream, 'read'):
            return stream.read()
        return bytes(stream)
    
    @staticmethod
    def password_hash(password):
        """计算密码哈希值"""
        return int(hashlib.sha256(password.encode()).hexdigest()[:16], 16)
    
    @staticmethod
    def get_file_extension(filename):
        """获取文件扩展名"""
        if not filename:
            return ""
        parts = filename.rsplit('.', 1)
        return parts[1].lower() if len(parts) > 1 else ""

