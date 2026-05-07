"""
配置管理模块

Copyright (C) 2025  MearaY

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License along
with this program; if not, write to the Free Software Foundation, Inc.,
51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""


class StegaPyConfig:
    """StegaPy 全局配置管理类，维护数据压缩、加密算法及密码等运行时设置。"""
    
    USE_COMPRESSION = "useCompression"
    USE_ENCRYPTION = "useEncryption"
    PASSWORD = "password"
    ENCRYPTION_ALGORITHM = "encryptionAlgorithm"
    
    def __init__(self, **kwargs):
        """使用关键字参数初始化配置信息。"""
        self.use_compression = kwargs.get('use_compression', True)
        self.use_encryption = kwargs.get('use_encryption', False)
        self.password = kwargs.get('password', None)
        self.encryption_algorithm = kwargs.get('encryption_algorithm', 'AES128')
    
    def is_use_compression(self):
        """判断当前是否启用了数据压缩功能。"""
        return self.use_compression
    
    def set_use_compression(self, value):
        """设置是否启用数据压缩。"""
        self.use_compression = value
    
    def is_use_encryption(self):
        """判断当前是否启用了数据加密功能。"""
        return self.use_encryption
    
    def set_use_encryption(self, value):
        """设置是否启用数据加密。"""
        self.use_encryption = value
    
    def get_password(self):
        """获取当前设置的加密/水印密码。"""
        return self.password
    
    def set_password(self, password):
        """设置用于加密或水印操作的凭证密码。"""
        self.password = password
    
    def get_encryption_algorithm(self):
        """获取当前配置的加密算法名称（如 AES128）。"""
        return self.encryption_algorithm
    
    def set_encryption_algorithm(self, algorithm):
        """指定运行时所需的加密算法。"""
        self.encryption_algorithm = algorithm

