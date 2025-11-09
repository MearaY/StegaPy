"""
加密工具模块
"""

import os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import hashlib


class CryptoUtil:
    """加密工具类"""
    
    ALGO_DES = "DES"
    ALGO_AES128 = "AES128"
    ALGO_AES256 = "AES256"
    
    # 8字节盐值
    SALT = bytes([0x28, 0x5F, 0x71, 0xC9, 0x1E, 0x35, 0x0A, 0x62])
    ITER_COUNT = 7
    
    def __init__(self, password, algorithm='AES128'):
        """初始化加密工具"""
        self.password = password
        self.algorithm = algorithm.upper() if algorithm else 'AES128'
        
        # 根据算法确定密钥长度
        if self.algorithm == 'AES128':
            self.key_length = 16
        elif self.algorithm == 'AES256':
            self.key_length = 32
        elif self.algorithm == 'DES':
            self.key_length = 8
            raise ValueError("DES算法已弃用，请使用AES128或AES256")
        else:
            raise ValueError(f"不支持的加密算法: {algorithm}")
        
        # 生成密钥
        self.key = self._derive_key(password)
    
    def _derive_key(self, password):
        """从密码派生密钥"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=self.key_length,
            salt=self.SALT,
            iterations=self.ITER_COUNT,
            backend=default_backend()
        )
        return kdf.derive(password.encode())
    
    def encrypt(self, data):
        """加密数据"""
        try:
            # 生成随机IV
            iv = os.urandom(16)
            
            # 创建加密器
            if self.algorithm.startswith('AES'):
                cipher = Cipher(
                    algorithms.AES(self.key),
                    modes.CBC(iv),
                    backend=default_backend()
                )
            else:
                raise ValueError(f"不支持的算法: {self.algorithm}")
            
            encryptor = cipher.encryptor()
            
            # 填充数据
            padder = padding.PKCS7(128).padder()
            padded_data = padder.update(data)
            padded_data += padder.finalize()
            
            # 加密
            ciphertext = encryptor.update(padded_data) + encryptor.finalize()
            
            # 返回: IV长度(1字节) + IV + 加密数据
            result = bytes([len(iv)]) + iv + ciphertext
            return result
        except Exception as e:
            raise Exception(f"加密失败: {str(e)}")
    
    def decrypt(self, data):
        """解密数据"""
        try:
            # 读取IV长度
            iv_len = data[0]
            # 读取IV
            iv = data[1:1+iv_len]
            # 读取密文
            ciphertext = data[1+iv_len:]
            
            # 创建解密器
            if self.algorithm.startswith('AES'):
                cipher = Cipher(
                    algorithms.AES(self.key),
                    modes.CBC(iv),
                    backend=default_backend()
                )
            else:
                raise ValueError(f"不支持的算法: {self.algorithm}")
            
            decryptor = cipher.decryptor()
            
            # 解密
            padded_data = decryptor.update(ciphertext) + decryptor.finalize()
            
            # 去除填充
            unpadder = padding.PKCS7(128).unpadder()
            plaintext = unpadder.update(padded_data)
            plaintext += unpadder.finalize()
            
            return plaintext
        except Exception as e:
            if "Bad" in str(e) or "Invalid" in str(e):
                raise Exception("密码错误或数据损坏")
            raise Exception(f"解密失败: {str(e)}")

