"""
RandomLSB输入流
"""

import random
import numpy as np
from PIL import Image
from ..lsb.lsb_data_header import LSBDataHeader
from ..lsb.lsb_config import LSBConfig
from ...util.common_util import CommonUtil


class RandomLSBInputStream:
    """RandomLSB输入流，使用随机序列提取数据"""
    
    def __init__(self, image: Image.Image, config: LSBConfig, password: str = None):
        """初始化RandomLSB输入流"""
        self.image = image
        self.config = config
        
        # 将图像转换为numpy数组
        self.pixels = np.array(image)
        self.height, self.width, self.channels = self.pixels.shape
        
        # 生成随机序列（基于密码）
        if password:
            seed = CommonUtil.password_hash(password)
        else:
            seed = random.randint(0, 2**32 - 1)
        
        self.random_gen = random.Random(seed)
        
        # 生成随机像素访问序列
        total_positions = self.width * self.height * self.channels
        self.position_sequence = list(range(total_positions))
        self.random_gen.shuffle(self.position_sequence)
        
        # 初始化读取位置
        self.current_index = 0
        self.current_bit = 0
        
        # 读取数据头
        header_bytes = self._read_bytes(LSBDataHeader.get_max_header_size())
        self.header = LSBDataHeader.from_bytes(header_bytes)
    
    def _read_bytes(self, count: int) -> bytes:
        """读取指定数量的字节"""
        result = bytearray()
        for _ in range(count):
            result.append(self._read_byte())
        return bytes(result)
    
    def _read_byte(self) -> int:
        """读取一个字节"""
        byte_value = 0
        for bit_pos in range(8):
            bit = self._read_bit()
            byte_value = (byte_value << 1) | bit
        return byte_value
    
    def _read_bit(self) -> int:
        """从随机位置读取一个位"""
        if self.current_index >= len(self.position_sequence):
            raise ValueError("已读取到图像末尾")
        
        # 获取随机位置
        position = self.position_sequence[self.current_index]
        pixel_idx = position // self.channels
        channel = position % self.channels
        
        row = pixel_idx // self.width
        col = pixel_idx % self.width
        
        # 获取当前像素值
        pixel_value = self.pixels[row, col, channel]
        
        # 读取最低有效位
        bits_to_use = self.config.get_max_bits_used_per_channel()
        if self.current_bit < bits_to_use:
            bit = (pixel_value >> self.current_bit) & 1
        else:
            bit = 0
        
        # 移动到下一个位置
        self.current_bit += 1
        if self.current_bit >= bits_to_use:
            self.current_bit = 0
            self.current_index += 1
        
        return bit
    
    def read(self, size: int = -1) -> bytes:
        """读取数据"""
        if size < 0:
            size = self.header.get_data_length()
        
        return self._read_bytes(min(size, self.header.get_data_length()))
    
    def get_data_header(self) -> LSBDataHeader:
        """获取数据头"""
        return self.header

