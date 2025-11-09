"""
LSB隐写插件
"""

from typing import List, Optional
import numpy as np
from PIL import Image
from ..base import StegaPyPlugin, Purpose
from ...util.image_util import ImageUtil
from ...exceptions import StegaPyException, StegaPyErrors
from .lsb_config import LSBConfig
from .lsb_output_stream import LSBOutputStream
from .lsb_input_stream import LSBInputStream


class LSBPlugin(StegaPyPlugin):
    """LSB（最低有效位）隐写插件"""
    
    NAMESPACE = "LSB"
    
    def __init__(self, config: Optional[LSBConfig] = None):
        """初始化LSB插件"""
        super().__init__(config or LSBConfig())
    
    def get_name(self) -> str:
        """获取插件名称"""
        return "LSB"
    
    def get_purposes(self) -> List[Purpose]:
        """获取插件支持的用途"""
        return [Purpose.DATA_HIDING]
    
    def get_description(self) -> str:
        """获取插件描述"""
        return "LSB（最低有效位）隐写算法，将数据隐藏在图像像素的最低有效位中"
    
    def embed_data(self, msg: bytes, msg_filename: Optional[str],
                   cover: Optional[bytes], cover_filename: Optional[str],
                   stego_filename: Optional[str]) -> bytes:
        """嵌入数据到封面图像"""
        try:
            # 如果没有提供封面图像，生成随机图像
            if cover is None:
                # 计算需要的像素数
                from .lsb_data_header import LSBDataHeader
                header_size = LSBDataHeader.get_max_header_size()
                num_pixels = int(header_size * 8 / 3.0)
                num_pixels += int(len(msg) * 8 / (3.0 * self.config.get_max_bits_used_per_channel()))
                image = ImageUtil.generate_random_image(num_pixels)
            else:
                image = ImageUtil.byte_array_to_image(cover, cover_filename)
            
            # 使用LSB输出流嵌入数据
            lsb_os = LSBOutputStream(image, len(msg), msg_filename, self.config)
            lsb_os.write(msg)
            lsb_os.flush()
            image = lsb_os.get_image()
            
            return ImageUtil.image_to_byte_array(image, stego_filename)
        except Exception as e:
            raise StegaPyException(str(e), StegaPyErrors.UNHANDLED_EXCEPTION, self.NAMESPACE)
    
    def extract_msg_filename(self, stego_data: bytes,
                            stego_filename: Optional[str]) -> str:
        """从隐写数据中提取消息文件名"""
        try:
            image = ImageUtil.byte_array_to_image(stego_data, stego_filename)
            lsb_is = LSBInputStream(image, self.config)
            return lsb_is.get_data_header().get_filename()
        except Exception as e:
            raise StegaPyException(str(e), StegaPyErrors.UNHANDLED_EXCEPTION, self.NAMESPACE)
    
    def extract_data(self, stego_data: bytes, stego_filename: Optional[str],
                    orig_sig_data: Optional[bytes] = None) -> bytes:
        """从隐写数据中提取消息"""
        try:
            image = ImageUtil.byte_array_to_image(stego_data, stego_filename)
            lsb_is = LSBInputStream(image, self.config)
            header = lsb_is.get_data_header()
            data = lsb_is.read(header.get_data_length())
            
            if len(data) != header.get_data_length():
                raise StegaPyException(
                    "数据读取不完整",
                    StegaPyErrors.ERR_IMAGE_DATA_READ,
                    self.NAMESPACE
                )
            
            return data
        except StegaPyException:
            raise
        except Exception as e:
            raise StegaPyException(str(e), StegaPyErrors.UNHANDLED_EXCEPTION, self.NAMESPACE)
    
    def generate_signature(self) -> bytes:
        """生成签名数据（LSB不支持水印）"""
        raise StegaPyException(
            "LSB插件不支持水印功能",
            StegaPyErrors.PLUGIN_DOES_NOT_SUPPORT_WM,
            self.NAMESPACE
        )
    
    def get_watermark_correlation(self, orig_sig_data: bytes,
                                  watermark_data: bytes) -> float:
        """获取水印相关性（LSB不支持）"""
        raise StegaPyException(
            "LSB插件不支持水印功能",
            StegaPyErrors.PLUGIN_DOES_NOT_SUPPORT_WM,
            self.NAMESPACE
        )
    
    def get_high_watermark_level(self) -> float:
        """获取高水印阈值（LSB不支持）"""
        return 0.0
    
    def get_low_watermark_level(self) -> float:
        """获取低水印阈值（LSB不支持）"""
        return 0.0
    
    def get_diff(self, stego_data: bytes, stego_filename: Optional[str],
                cover_data: bytes, cover_filename: Optional[str],
                diff_filename: Optional[str]) -> bytes:
        """获取原始图像和隐写图像的差异"""
        try:
            stego_image = ImageUtil.byte_array_to_image(stego_data, stego_filename)
            cover_image = ImageUtil.byte_array_to_image(cover_data, cover_filename)
            
            stego_pixels = ImageUtil.get_image_pixels(stego_image)
            cover_pixels = ImageUtil.get_image_pixels(cover_image)
            
            # 计算差异（放大差异以便可视化）
            diff_pixels = np.abs(stego_pixels.astype(np.int16) - cover_pixels.astype(np.int16)) * 10
            diff_pixels = np.clip(diff_pixels, 0, 255).astype(np.uint8)
            
            diff_image = ImageUtil.set_image_pixels(Image.new('RGB', stego_image.size), diff_pixels)
            return ImageUtil.image_to_byte_array(diff_image, diff_filename)
        except Exception as e:
            raise StegaPyException(str(e), StegaPyErrors.UNHANDLED_EXCEPTION, self.NAMESPACE)
    
    def get_readable_file_extensions(self) -> List[str]:
        """获取支持读取的文件扩展名"""
        return ['png', 'bmp', 'jpg', 'jpeg']
    
    def get_writable_file_extensions(self) -> List[str]:
        """获取支持写入的文件扩展名"""
        # LSB需要无损格式
        return ['png', 'bmp']
    
    def create_config(self) -> LSBConfig:
        """创建默认配置"""
        return LSBConfig()

