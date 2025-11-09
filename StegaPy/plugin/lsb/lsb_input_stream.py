"""
LSB输入流
"""

import numpy as np
from PIL import Image
from .lsb_data_header import LSBDataHeader
from .lsb_config import LSBConfig


class LSBInputStream:
    """LSB输入流，用于从图像中提取数据"""
    
    def __init__(self, image: Image.Image, config: LSBConfig):
        """初始化LSB输入流"""
        self.image = image
        self.config = config
        
        # 将图像转换为numpy数组
        self.pixels = np.array(image)
        self.height, self.width, self.channels = self.pixels.shape
        
        # 初始化读取位置
        self.current_pixel = 0
        self.current_channel = 0
        self.current_bit = 0
        
        # 读取数据头
        # 先读取固定部分（DATA_STAMP + HEADER_VERSION + FIXED_HEADER + CRYPT_ALGO）
        fixed_part_size = (len(LSBDataHeader.DATA_STAMP) + 
                          len(LSBDataHeader.HEADER_VERSION) + 
                          LSBDataHeader.FIXED_HEADER_LENGTH + 
                          LSBDataHeader.CRYPT_ALGO_LENGTH)
        fixed_part = self._read_bytes(fixed_part_size)
        
        # 从固定部分中提取fileNameLen
        fixed_header_offset = len(LSBDataHeader.DATA_STAMP) + len(LSBDataHeader.HEADER_VERSION)
        filename_len = fixed_part[fixed_header_offset + 5]  # FIXED_HEADER的第6个字节（索引5）
        
        # 读取文件名部分
        filename_part = self._read_bytes(filename_len) if filename_len > 0 else b''
        
        # 组合完整的数据头
        header_bytes = fixed_part + filename_part
        
        # 解析数据头
        try:
            self.header = LSBDataHeader.from_bytes(header_bytes, config)
        except Exception as e:
            raise ValueError(f"无法解析数据头: {e}")
        
        # 更新配置中的channel_bits_used
        self.channel_bits_used = self.header.get_channel_bits_used()
    
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
        """读取一个位"""
        if self.current_pixel >= self.width * self.height:
            raise ValueError("已读取到图像末尾")
        
        row = self.current_pixel // self.width
        col = self.current_pixel % self.width
        
        # 获取当前像素值
        pixel_value = self.pixels[row, col, self.current_channel]
        
        # 读取最低有效位
        # 使用header中的channel_bits_used，如果还没有header则使用config中的值
        bits_to_use = getattr(self, 'channel_bits_used', None) or self.config.get_max_bits_used_per_channel()
        if self.current_bit < bits_to_use:
            bit = (pixel_value >> self.current_bit) & 1
        else:
            bit = 0
        
        # 移动到下一个位置
        self.current_bit += 1
        if self.current_bit >= bits_to_use:
            self.current_bit = 0
            self.current_channel += 1
            if self.current_channel >= self.channels:
                self.current_channel = 0
                self.current_pixel += 1
        
        return bit
    
    def read(self, size: int = -1) -> bytes:
        """读取数据"""
        if size < 0:
            size = self.header.get_data_length()
        
        return self._read_bytes(min(size, self.header.get_data_length()))
    
    def get_data_header(self) -> LSBDataHeader:
        """获取数据头"""
        return self.header

