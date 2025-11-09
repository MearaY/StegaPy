"""
LSB输出流
"""

import numpy as np
from PIL import Image
from .lsb_data_header import LSBDataHeader
from .lsb_config import LSBConfig


class LSBOutputStream:
    """LSB输出流，用于将数据嵌入到图像中"""
    
    def __init__(self, image: Image.Image, data_length: int, 
                 filename: str, config: LSBConfig):
        """初始化LSB输出流"""
        self.image = image.copy()
        self.config = config
        self.data_length = data_length
        self.filename = filename
        
        # 创建数据头（使用config中的channel_bits_used）
        channel_bits_used = config.get_max_bits_used_per_channel()
        self.header = LSBDataHeader(data_length, channel_bits_used, filename, config)
        
        # 将图像转换为numpy数组
        self.pixels = np.array(self.image)
        self.height, self.width, self.channels = self.pixels.shape
        
        # 计算需要的像素数
        header_bits = len(self.header.to_bytes()) * 8
        data_bits = data_length * 8
        total_bits = header_bits + data_bits
        bits_per_pixel = self.channels * config.get_max_bits_used_per_channel()
        required_pixels = (total_bits + bits_per_pixel - 1) // bits_per_pixel
        
        if required_pixels > self.width * self.height:
            raise ValueError(f"图像太小，无法嵌入{data_length}字节的数据")
        
        # 初始化写入位置
        self.current_pixel = 0
        self.current_channel = 0
        self.current_bit = 0
        
        # 写入数据头
        self._write_bytes(self.header.to_bytes())
    
    def _write_bytes(self, data: bytes):
        """写入字节数据"""
        for byte in data:
            self._write_byte(byte)
    
    def _write_byte(self, byte: int):
        """写入一个字节"""
        for bit_pos in range(8):
            bit = (byte >> (7 - bit_pos)) & 1
            self._write_bit(bit)
    
    def _write_bit(self, bit: int):
        """写入一个位"""
        if self.current_pixel >= self.width * self.height:
            raise ValueError("图像空间不足")
        
        row = self.current_pixel // self.width
        col = self.current_pixel % self.width
        
        # 获取当前像素值，转换为int类型以避免位操作时的符号问题
        pixel_value = int(self.pixels[row, col, self.current_channel])
        
        # 修改最低有效位
        bits_to_use = self.config.get_max_bits_used_per_channel()
        if self.current_bit < bits_to_use:
            # 清除当前位（使用正确的掩码，避免负数问题）
            mask = 0xFF ^ (1 << self.current_bit)  # 使用 XOR 而不是 ~ 来避免负数
            pixel_value = pixel_value & mask
            # 设置新位
            pixel_value = pixel_value | (bit << self.current_bit)
            # 确保值在0-255范围内
            pixel_value = max(0, min(255, pixel_value))
            self.pixels[row, col, self.current_channel] = pixel_value
        
        # 移动到下一个位置
        self.current_bit += 1
        if self.current_bit >= bits_to_use:
            self.current_bit = 0
            self.current_channel += 1
            if self.current_channel >= self.channels:
                self.current_channel = 0
                self.current_pixel += 1
    
    def write(self, data: bytes):
        """写入数据"""
        self._write_bytes(data)
    
    def flush(self):
        """刷新缓冲区"""
        # 确保像素值在0-255范围内，避免uint8溢出错误
        pixels_clipped = np.clip(self.pixels, 0, 255).astype(np.uint8)
        # 更新图像
        self.image = Image.fromarray(pixels_clipped)
    
    def get_image(self) -> Image.Image:
        """获取处理后的图像"""
        return self.image

