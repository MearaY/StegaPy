"""
StegaPy主类

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

import gzip
from typing import List, Optional
from .config import StegaPyConfig
from .plugin.base import StegaPyPlugin, Purpose
from .plugin_manager import PluginManager
from .util.crypto_util import CryptoUtil
from .exceptions import StegaPyException, StegaPyErrors


class StegaPy:
    """StegaPy主类"""
    
    NAMESPACE = "StegaPy"
    
    def __init__(self, plugin: StegaPyPlugin, config: StegaPyConfig):
        """初始化StegaPy"""
        if plugin is None:
            raise StegaPyException(
                "未指定插件",
                StegaPyErrors.NO_PLUGIN_SPECIFIED,
                self.NAMESPACE
            )
        if config is None:
            raise StegaPyException(
                "未指定配置",
                StegaPyErrors.UNHANDLED_EXCEPTION,
                self.NAMESPACE
            )
        
        self.plugin = plugin
        self.config = config
    
    def embed_data(self, msg: bytes, msg_filename: Optional[str],
                   cover: Optional[bytes], cover_filename: Optional[str],
                   stego_filename: Optional[str]) -> bytes:
        """嵌入数据到封面图像"""
        if Purpose.DATA_HIDING not in self.plugin.get_purposes():
            raise StegaPyException(
                "插件不支持数据隐藏",
                StegaPyErrors.PLUGIN_DOES_NOT_SUPPORT_DH,
                self.NAMESPACE
            )
        
        try:
            # 压缩数据（如果启用）
            if self.config.is_use_compression():
                msg = self._compress_data(msg)
            
            # 加密数据（如果启用）
            if self.config.is_use_encryption():
                if not self.config.get_password():
                    raise StegaPyException(
                        "加密需要密码",
                        StegaPyErrors.INVALID_PASSWORD,
                        self.NAMESPACE
                    )
                crypto = CryptoUtil(self.config.get_password(), 
                                  self.config.get_encryption_algorithm())
                msg = crypto.encrypt(msg)
            
            # 使用插件嵌入数据
            return self.plugin.embed_data(msg, msg_filename, cover, 
                                         cover_filename, stego_filename)
        except StegaPyException:
            raise
        except Exception as e:
            raise StegaPyException(str(e), StegaPyErrors.UNHANDLED_EXCEPTION, self.NAMESPACE)
    
    def extract_data(self, stego_data: bytes, 
                    stego_filename: Optional[str]) -> List:
        """从隐写数据中提取消息"""
        if Purpose.DATA_HIDING not in self.plugin.get_purposes():
            raise StegaPyException(
                "插件不支持数据隐藏",
                StegaPyErrors.PLUGIN_DOES_NOT_SUPPORT_DH,
                self.NAMESPACE
            )
        
        try:
            # 提取数据
            msg_filename = self.plugin.extract_msg_filename(stego_data, stego_filename)
            msg = self.plugin.extract_data(stego_data, stego_filename, None)
            
            # 解密数据（如果启用）
            if self.config.is_use_encryption():
                if not self.config.get_password():
                    raise StegaPyException(
                        "解密需要密码",
                        StegaPyErrors.INVALID_PASSWORD,
                        self.NAMESPACE
                    )
                crypto = CryptoUtil(self.config.get_password(),
                                  self.config.get_encryption_algorithm())
                msg = crypto.decrypt(msg)
            
            # 解压数据（如果启用）
            if self.config.is_use_compression():
                msg = self._decompress_data(msg)
            
            return [msg_filename, msg]
        except StegaPyException:
            raise
        except Exception as e:
            raise StegaPyException(str(e), StegaPyErrors.UNHANDLED_EXCEPTION, self.NAMESPACE)
    
    def embed_mark(self, sig: bytes, sig_filename: Optional[str],
                   cover: Optional[bytes], cover_filename: Optional[str],
                   stego_filename: Optional[str]) -> bytes:
        """嵌入水印到封面图像"""
        if Purpose.WATERMARKING not in self.plugin.get_purposes():
            raise StegaPyException(
                "插件不支持水印",
                StegaPyErrors.PLUGIN_DOES_NOT_SUPPORT_WM,
                self.NAMESPACE
            )
        
        try:
            # 水印不使用压缩和加密
            return self.plugin.embed_data(sig, sig_filename, cover,
                                         cover_filename, stego_filename)
        except StegaPyException:
            raise
        except Exception as e:
            raise StegaPyException(str(e), StegaPyErrors.UNHANDLED_EXCEPTION, self.NAMESPACE)
    
    def check_mark(self, stego_data: bytes, stego_filename: Optional[str],
                   orig_sig_data: bytes) -> float:
        """检查水印相关性"""
        if Purpose.WATERMARKING not in self.plugin.get_purposes():
            raise StegaPyException(
                "插件不支持水印",
                StegaPyErrors.PLUGIN_DOES_NOT_SUPPORT_WM,
                self.NAMESPACE
            )
        
        try:
            correl = self.plugin.check_mark(stego_data, stego_filename, orig_sig_data)
            if correl is None or (isinstance(correl, float) and correl != correl):  # NaN check
                return 0.0
            return float(correl)
        except StegaPyException:
            raise
        except Exception as e:
            raise StegaPyException(str(e), StegaPyErrors.UNHANDLED_EXCEPTION, self.NAMESPACE)
    
    def generate_signature(self) -> bytes:
        """生成签名数据"""
        if Purpose.WATERMARKING not in self.plugin.get_purposes():
            raise StegaPyException(
                "插件不支持水印",
                StegaPyErrors.PLUGIN_DOES_NOT_SUPPORT_WM,
                self.NAMESPACE
            )
        
        if not self.config.get_password():
            raise StegaPyException(
                "生成签名需要密码",
                StegaPyErrors.PWD_MANDATORY_FOR_GENSIG,
                self.NAMESPACE
            )
        
        return self.plugin.generate_signature()
    
    def get_diff(self, stego_data: bytes, stego_filename: Optional[str],
                 cover_data: bytes, cover_filename: Optional[str],
                 diff_filename: Optional[str]) -> bytes:
        """获取原始图像和隐写图像的差异"""
        return self.plugin.get_diff(stego_data, stego_filename,
                                   cover_data, cover_filename, diff_filename)
    
    def get_config(self) -> StegaPyConfig:
        """获取配置"""
        return self.config
    
    def _compress_data(self, data: bytes) -> bytes:
        """压缩数据"""
        return gzip.compress(data)
    
    def _decompress_data(self, data: bytes) -> bytes:
        """解压数据"""
        # 检查数据是否为空
        if not data or len(data) == 0:
            raise StegaPyException(
                "数据为空，无法解压",
                StegaPyErrors.CORRUPT_DATA,
                self.NAMESPACE
            )
        
        # 检查数据是否是有效的 gzip 格式
        # gzip 文件以 \x1f\x8b 开头
        if len(data) < 2 or data[:2] != b'\x1f\x8b':
            raise StegaPyException(
                "数据不是有效的 gzip 格式。请检查：\n"
                "1. 嵌入数据时是否启用了压缩\n"
                "2. 提取数据时的压缩设置是否与嵌入时一致\n"
                f"数据前2字节: {data[:2].hex() if len(data) >= 2 else '数据太短'}",
                StegaPyErrors.CORRUPT_DATA,
                self.NAMESPACE
            )
        
        try:
            return gzip.decompress(data)
        except gzip.BadGzipFile as e:
            raise StegaPyException(
                f"数据解压失败（不是有效的 gzip 文件）: {str(e)}\n"
                "请检查压缩设置是否与嵌入时一致",
                StegaPyErrors.CORRUPT_DATA,
                self.NAMESPACE
            )
        except Exception as e:
            raise StegaPyException(
                f"数据解压失败: {str(e)}\n"
                "请检查压缩设置是否与嵌入时一致",
                StegaPyErrors.CORRUPT_DATA,
                self.NAMESPACE
            )

