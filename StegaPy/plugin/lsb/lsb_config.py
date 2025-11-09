"""
LSB插件配置
"""

from ..base import StegaPyConfig


class LSBConfig(StegaPyConfig):
    """LSB插件配置类"""
    
    def __init__(self, max_bits_used_per_channel=1, **kwargs):
        """初始化LSB配置"""
        super().__init__(**kwargs)
        self.max_bits_used_per_channel = max_bits_used_per_channel
    
    def get_max_bits_used_per_channel(self):
        """获取每个通道使用的最大位数"""
        return self.max_bits_used_per_channel
    
    def set_max_bits_used_per_channel(self, value):
        """设置每个通道使用的最大位数"""
        if value < 1 or value > 8:
            raise ValueError("每个通道使用的位数必须在1-8之间")
        self.max_bits_used_per_channel = value

