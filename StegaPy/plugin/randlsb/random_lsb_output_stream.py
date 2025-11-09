"""
RandomLSB输出流
"""

import random
import numpy as np
from PIL import Image
from ..lsb.lsb_data_header import LSBDataHeader
from ..lsb.lsb_config import LSBConfig
from ...util.common_util import CommonUtil


class RandomLSBOutputStream:
    """RandomLSB输出流，使用随机序列嵌入数据"""
    
    def __init__(self, image: Image.Image, data_length: int,
                 filename: str, config: LSBConfig, password: str = None):
        """初始化RandomLSB输出流"""
        self.image = image.copy()
        self.config = config
        self.data_length = data_length
        self.filename = filename
        
        # 创建数据头
        self.header = LSBDataHeader(data_length, filename)
        
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
        
        # 初始化写入位置
        self.current_index = 0
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
        """写入一个位到随机位置"""
        if self.current_index >= len(self.position_sequence):
            raise ValueError("图像空间不足")
        
        # 获取随机位置
        position = self.position_sequence[self.current_index]
        pixel_idx = position // self.channels
        channel = position % self.channels
        
        row = pixel_idx // self.width
        col = pixel_idx % self.width
        
        # 获取当前像素值，转换为int类型以避免位操作时的符号问题
        pixel_value = int(self.pixels[row, col, channel])
        
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
            self.pixels[row, col, channel] = pixel_value
        
        # 移动到下一个位置
        self.current_bit += 1
        if self.current_bit >= bits_to_use:
            self.current_bit = 0
            self.current_index += 1
    
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

