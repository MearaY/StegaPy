"""
图像处理工具模块
"""

import io
import numpy as np
from PIL import Image
import random


class ImageUtil:
    """图像处理工具类"""
    
    @staticmethod
    def byte_array_to_image(data, filename=None):
        """将字节数组转换为PIL图像"""
        try:
            # 检查数据是否为空
            if data is None:
                raise ValueError("图像数据为空")
            
            # 统一转换为字节数组
            data_bytes = None
            if isinstance(data, io.BytesIO):
                # 对于 BytesIO 对象，先读取所有内容
                try:
                    current_pos = data.tell()
                    data.seek(0)  # 重置指针到开头
                    data_bytes = data.read()
                    # 恢复原位置（如果可能）
                    try:
                        data.seek(current_pos)
                    except:
                        pass
                except Exception as e:
                    raise ValueError(f"无法从BytesIO读取数据: {str(e)}")
            elif isinstance(data, (bytes, bytearray)):
                data_bytes = bytes(data)
            else:
                # 尝试转换为字节数组
                try:
                    data_bytes = bytes(data)
                except (TypeError, ValueError) as e:
                    raise ValueError(f"不支持的图像数据类型: {type(data).__name__}, 错误: {str(e)}")
            
            # 验证数据不为空
            if data_bytes is None or len(data_bytes) == 0:
                raise ValueError("图像数据为空")
            
            # 验证数据大小（至少要有文件头）
            if len(data_bytes) < 8:
                raise ValueError(f"图像数据太小（仅{len(data_bytes)}字节），不是有效的图像文件")
            
            # 验证图像文件头（检查常见格式）
            header = data_bytes[:8]
            is_valid_image = False
            
            # PNG: 89 50 4E 47 0D 0A 1A 0A
            if header.startswith(b'\x89PNG\r\n\x1a\n'):
                is_valid_image = True
            # JPEG: FF D8 FF
            elif header.startswith(b'\xff\xd8\xff'):
                is_valid_image = True
            # BMP: 42 4D
            elif header.startswith(b'BM'):
                is_valid_image = True
            # GIF: 47 49 46 38
            elif header.startswith(b'GIF8'):
                is_valid_image = True
            # TIFF: 49 49 2A 00 或 4D 4D 00 2A
            elif header.startswith(b'II*\x00') or header.startswith(b'MM\x00*'):
                is_valid_image = True
            
            if not is_valid_image:
                # 即使文件头不匹配，也尝试让PIL识别（某些格式可能有不同的头）
                pass
            
            # 创建新的 BytesIO 对象以确保数据完整性
            data = io.BytesIO(data_bytes)
            
            # 打开图像（PIL 会自动验证图像格式）
            # 注意：如果数据不是有效的图像，这里会抛出异常
            img = Image.open(data)
            
            # 加载图像数据（延迟加载，需要显式调用load）
            img.load()
            
            # 转换为RGB模式以支持所有操作
            if img.mode != 'RGB':
                img = img.convert('RGB')
            return img
        except Exception as e:
            file_info = f" (文件: {filename})" if filename else ""
            # 提供更详细的错误信息
            try:
                if 'data_bytes' in locals() and data_bytes is not None:
                    data_size = len(data_bytes)
                    data_type = type(data).__name__
                    if isinstance(data, io.BytesIO):
                        error_msg = f"无法读取图像{file_info}: {str(e)} (数据类型: BytesIO, 数据大小: {data_size}字节)"
                    else:
                        error_msg = f"无法读取图像{file_info}: {str(e)} (数据类型: {data_type}, 数据大小: {data_size}字节)"
                else:
                    data_type = type(data).__name__ if data is not None else "None"
                    error_msg = f"无法读取图像{file_info}: {str(e)} (数据类型: {data_type})"
            except:
                error_msg = f"无法读取图像{file_info}: {str(e)}"
            raise Exception(error_msg)
    
    @staticmethod
    def image_to_byte_array(image, filename=None, format='PNG'):
        """将PIL图像转换为字节数组"""
        try:
            # 根据文件名确定格式
            if filename:
                ext = filename.rsplit('.', 1)[-1].lower()
                if ext in ['jpg', 'jpeg']:
                    format = 'JPEG'
                elif ext == 'png':
                    format = 'PNG'
                elif ext == 'bmp':
                    format = 'BMP'
            
            output = io.BytesIO()
            image.save(output, format=format)
            return output.getvalue()
        except Exception as e:
            raise Exception(f"无法保存图像: {str(e)}")
    
    @staticmethod
    def generate_random_image(num_pixels):
        """生成随机图像"""
        # 计算合适的尺寸（接近正方形）
        side = int(np.sqrt(num_pixels)) + 1
        width = side
        height = side
        
        # 生成随机RGB图像
        random.seed()
        pixels = []
        for _ in range(height):
            row = []
            for _ in range(width):
                row.append((
                    random.randint(0, 255),
                    random.randint(0, 255),
                    random.randint(0, 255)
                ))
            pixels.append(row)
        
        img = Image.new('RGB', (width, height))
        img.putdata([pixel for row in pixels for pixel in row])
        return img
    
    @staticmethod
    def get_image_pixels(image):
        """获取图像像素数组"""
        return np.array(image)
    
    @staticmethod
    def set_image_pixels(image, pixels):
        """设置图像像素"""
        # 确保像素值在0-255范围内，避免uint8溢出错误
        pixels = np.clip(pixels, 0, 255)
        return Image.fromarray(pixels.astype(np.uint8))
    
    @staticmethod
    def get_yuv_from_image(image):
        """将RGB图像转换为YUV色彩空间"""
        rgb_array = np.array(image, dtype=np.float32)
        r, g, b = rgb_array[:, :, 0], rgb_array[:, :, 1], rgb_array[:, :, 2]
        
        # RGB to YUV转换
        y = 0.299 * r + 0.587 * g + 0.114 * b
        u = -0.14713 * r - 0.28886 * g + 0.436 * b
        v = 0.615 * r - 0.51499 * g - 0.10001 * b
        
        return [y.astype(np.int32), u.astype(np.int32), v.astype(np.int32)]
    
    @staticmethod
    def get_image_from_yuv(yuv, img_type='RGB'):
        """将YUV色彩空间转换回RGB图像"""
        y, u, v = yuv[0].astype(np.float32), yuv[1].astype(np.float32), yuv[2].astype(np.float32)
        
        # YUV to RGB转换
        r = y + 1.13983 * v
        g = y - 0.39465 * u - 0.58060 * v
        b = y + 2.03211 * u
        
        # 限制范围到0-255
        r = np.clip(r, 0, 255)
        g = np.clip(g, 0, 255)
        b = np.clip(b, 0, 255)
        
        rgb_array = np.stack([r, g, b], axis=2).astype(np.uint8)
        return Image.fromarray(rgb_array)
    
    @staticmethod
    def pixel_range(value):
        """将像素值限制在0-255范围内"""
        return max(0, min(255, int(value)))

