"""
插件基类

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

from enum import Enum
from typing import List, Optional
from ..config import StegaPyConfig
from ..exceptions import StegaPyException


class Purpose(Enum):
    """插件用途枚举"""
    DATA_HIDING = "DATA_HIDING"  # 数据隐藏
    WATERMARKING = "WATERMARKING"  # 数字水印


class StegaPyPlugin:
    """StegaPy插件基类"""
    
    def __init__(self, config: Optional[StegaPyConfig] = None):
        """初始化插件"""
        self.config = config or self.create_config()
    
    def get_name(self) -> str:
        """获取插件名称"""
        raise NotImplementedError
    
    def get_purposes(self) -> List[Purpose]:
        """获取插件支持的用途"""
        raise NotImplementedError
    
    def get_description(self) -> str:
        """获取插件描述"""
        raise NotImplementedError
    
    def embed_data(self, msg: bytes, msg_filename: Optional[str], 
                   cover: bytes, cover_filename: Optional[str], 
                   stego_filename: Optional[str]) -> bytes:
        """嵌入数据到封面图像"""
        raise NotImplementedError
    
    def extract_msg_filename(self, stego_data: bytes, 
                             stego_filename: Optional[str]) -> str:
        """从隐写数据中提取消息文件名"""
        raise NotImplementedError
    
    def extract_data(self, stego_data: bytes, stego_filename: Optional[str],
                     orig_sig_data: Optional[bytes] = None) -> bytes:
        """从隐写数据中提取消息"""
        raise NotImplementedError
    
    def generate_signature(self) -> bytes:
        """生成签名数据（用于水印）"""
        raise NotImplementedError
    
    def check_mark(self, stego_data: bytes, stego_filename: Optional[str],
                   orig_sig_data: bytes) -> float:
        """检查水印相关性"""
        watermark_data = self.extract_data(stego_data, stego_filename, orig_sig_data)
        return self.get_watermark_correlation(orig_sig_data, watermark_data)
    
    def get_watermark_correlation(self, orig_sig_data: bytes, 
                                   watermark_data: bytes) -> float:
        """获取水印相关性"""
        raise NotImplementedError
    
    def get_high_watermark_level(self) -> float:
        """获取高水印阈值"""
        raise NotImplementedError
    
    def get_low_watermark_level(self) -> float:
        """获取低水印阈值"""
        raise NotImplementedError
    
    def get_diff(self, stego_data: bytes, stego_filename: Optional[str],
                 cover_data: bytes, cover_filename: Optional[str],
                 diff_filename: Optional[str]) -> bytes:
        """获取原始图像和隐写图像的差异"""
        raise NotImplementedError
    
    def get_readable_file_extensions(self) -> List[str]:
        """获取支持读取的文件扩展名"""
        raise NotImplementedError
    
    def get_writable_file_extensions(self) -> List[str]:
        """获取支持写入的文件扩展名"""
        raise NotImplementedError
    
    def create_config(self) -> StegaPyConfig:
        """创建默认配置"""
        return StegaPyConfig()
    
    def get_config(self) -> StegaPyConfig:
        """获取配置"""
        return self.config
    
    def reset_config(self, config: Optional[StegaPyConfig] = None):
        """重置配置"""
        self.config = config or self.create_config()

