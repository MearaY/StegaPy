"""
DWT Dugad水印插件
基于Dugad算法的离散小波变换水印实现

使用PyWavelets库进行小波变换，使用NumPy进行数值计算。

主要特性：
- 水印生成：基于密码生成正态分布随机序列
- 水印嵌入：在DWT子带中嵌入水印
- 水印检测：计算水印相关性
"""

from typing import List, Optional
import struct
import io
import random
import numpy as np
from PIL import Image
from ..base import StegaPyPlugin, Purpose
from ...util.image_util import ImageUtil
from ...util.dwt_util import DWTUtil
from ...util.common_util import CommonUtil
from ...exceptions import StegaPyException, StegaPyErrors
from ...config import StegaPyConfig


class DWTDugadPlugin(StegaPyPlugin):
    """DWT Dugad水印插件
    
    提供完整的水印生成、嵌入和检测功能。
    """
    
    NAMESPACE = "DWTDUGAD"
    SIG_MARKER = b"DGSG"
    WM_MARKER = b"DGWM"
    
    # 默认参数
    DEFAULT_WATERMARK_LENGTH = 1000
    DEFAULT_DECOMPOSITION_LEVEL = 3
    DEFAULT_ALPHA = 0.2
    DEFAULT_CASTING_THRESHOLD = 40.0
    DEFAULT_DETECTION_THRESHOLD = 50.0
    DEFAULT_WAVELET = 'db1'
    # 保留这些参数
    DEFAULT_WAVELET_FILTER_METHOD = 2
    DEFAULT_FILTER_ID = 1
    
    def __init__(self, config: Optional[StegaPyConfig] = None):
        """初始化DWT Dugad插件"""
        super().__init__(config or StegaPyConfig())
    
    def get_name(self) -> str:
        """获取插件名称"""
        return "DWTDugad"
    
    def get_purposes(self) -> List[Purpose]:
        """获取插件支持的用途"""
        return [Purpose.WATERMARKING]
    
    def get_description(self) -> str:
        """获取插件描述"""
        return "DWT Dugad水印算法，基于离散小波变换的数字水印技术"
    
    def embed_data(self, msg: bytes, msg_filename: Optional[str],
                   cover: Optional[bytes], cover_filename: Optional[str],
                   stego_filename: Optional[str]) -> bytes:
        """嵌入水印到封面图像"""
        if cover is None:
            raise StegaPyException(
                "水印功能需要封面图像",
                StegaPyErrors.ERR_NO_COVER_FILE,
                self.NAMESPACE
            )
        
        try:
            # msg参数是签名数据，直接加载
            sig = self._load_signature(msg)
            
            # 读取图像
            image = ImageUtil.byte_array_to_image(cover, cover_filename)
            img_array = np.array(image)
            
            # 转换为YUV色彩空间
            yuv = ImageUtil.get_yuv_from_image(image)
            luminance = yuv[0].astype(np.float64)
            
            # 保存原始尺寸，用于后续尺寸匹配
            original_shape = luminance.shape
            
            # 执行小波变换
            coeffs = DWTUtil.forward_dwt(luminance, self.DEFAULT_WAVELET, sig['decomposition_level'])
            
            # 在所有分解层级的子带中嵌入水印
            for level in range(1, sig['decomposition_level'] + 1):
                if level >= len(coeffs):
                    raise StegaPyException(
                        "图像太小，无法进行指定层数的小波分解",
                        StegaPyErrors.ERR_FILE_TOO_SMALL,
                        self.NAMESPACE
                    )
                
                cH, cV, cD = coeffs[level]
                
                # 在三个子带中嵌入水印
                self._wm_subband(cH, sig['watermark'], sig['watermark_length'],
                                sig['alpha'], sig['casting_threshold'])
                self._wm_subband(cV, sig['watermark'], sig['watermark_length'],
                                sig['alpha'], sig['casting_threshold'])
                self._wm_subband(cD, sig['watermark'], sig['watermark_length'],
                                sig['alpha'], sig['casting_threshold'])
            
            # 执行逆向小波变换
            luminance = DWTUtil.inverse_dwt(coeffs, self.DEFAULT_WAVELET)
            
            # 确保尺寸与原始图像一致（小波变换可能会改变尺寸）
            if luminance.shape != original_shape:
                # 如果尺寸不匹配，裁剪或填充到原始尺寸
                h, w = original_shape
                current_h, current_w = luminance.shape
                
                # 裁剪或填充到原始尺寸
                if current_h > h or current_w > w:
                    # 裁剪到原始尺寸
                    luminance = luminance[:h, :w]
                elif current_h < h or current_w < w:
                    # 填充到原始尺寸（使用边缘值填充）
                    padded = np.zeros(original_shape, dtype=luminance.dtype)
                    padded[:current_h, :current_w] = luminance
                    # 填充边缘：使用最后一行的值填充高度，使用最后一列的值填充宽度
                    if current_h < h:
                        padded[current_h:, :current_w] = luminance[-1:, :]
                    if current_w < w:
                        padded[:, current_w:] = padded[:, current_w-1:current_w]
                    luminance = padded
            
            luminance = np.clip(luminance, 0, 255).astype(np.uint8)
            
            # 转换回RGB
            yuv[0] = luminance.astype(np.int32)
            image = ImageUtil.get_image_from_yuv(yuv, 'RGB')
            
            return ImageUtil.image_to_byte_array(image, stego_filename)
        except StegaPyException:
            raise
        except Exception as e:
            raise StegaPyException(str(e), StegaPyErrors.UNHANDLED_EXCEPTION, self.NAMESPACE)
    
    def extract_data(self, stego_data: bytes, stego_filename: Optional[str],
                    orig_sig_data: Optional[bytes] = None) -> bytes:
        """从隐写数据中提取水印信息"""
        if orig_sig_data is None:
            raise StegaPyException(
                "提取水印需要原始签名数据",
                StegaPyErrors.ERR_SIG_NOT_VALID,
                self.NAMESPACE
            )
        
        try:
            # 读取签名
            sig = self._load_signature(orig_sig_data)
            
            # 读取图像
            image = ImageUtil.byte_array_to_image(stego_data, stego_filename)
            yuv = ImageUtil.get_yuv_from_image(image)
            luminance = yuv[0].astype(np.float64)
            
            # 执行小波变换
            coeffs = DWTUtil.forward_dwt(luminance, self.DEFAULT_WAVELET, sig['decomposition_level'])
            
            # 提取水印信息
            output = io.BytesIO()
            output.write(self.WM_MARKER)
            output.write(struct.pack('>i', sig['decomposition_level']))
            output.write(struct.pack('>d', sig['alpha']))
            
            for level in range(1, sig['decomposition_level'] + 1):
                cH, cV, cD = coeffs[level]
                
                # 从三个子带提取水印
                vals_h = self._inv_wm_subband(cH, sig['watermark'], sig['watermark_length'],
                                              sig['detection_threshold'])
                output.write(struct.pack('>i', vals_h[0]))
                output.write(struct.pack('>d', vals_h[1]))
                output.write(struct.pack('>d', vals_h[2]))
                
                vals_v = self._inv_wm_subband(cV, sig['watermark'], sig['watermark_length'],
                                              sig['detection_threshold'])
                output.write(struct.pack('>i', vals_v[0]))
                output.write(struct.pack('>d', vals_v[1]))
                output.write(struct.pack('>d', vals_v[2]))
                
                vals_d = self._inv_wm_subband(cD, sig['watermark'], sig['watermark_length'],
                                              sig['detection_threshold'])
                output.write(struct.pack('>i', vals_d[0]))
                output.write(struct.pack('>d', vals_d[1]))
                output.write(struct.pack('>d', vals_d[2]))
            
            return output.getvalue()
        except Exception as e:
            raise StegaPyException(str(e), StegaPyErrors.UNHANDLED_EXCEPTION, self.NAMESPACE)
    
    def extract_msg_filename(self, stego_data: bytes,
                            stego_filename: Optional[str]) -> str:
        """提取消息文件名（水印不支持）"""
        return ""
    
    def generate_signature(self) -> bytes:
        """生成签名数据"""
        if not self.config or not self.config.get_password():
            raise StegaPyException(
                "生成签名需要密码",
                StegaPyErrors.PWD_MANDATORY_FOR_GENSIG,
                self.NAMESPACE
            )
        
        # 基于密码生成随机数生成器
        seed = CommonUtil.password_hash(self.config.get_password())
        rand = random.Random(seed)
        
        # 生成水印数据（正态分布）
        watermark_length = self.DEFAULT_WATERMARK_LENGTH
        watermark = []
        
        for i in range(0, watermark_length, 2):
            # Box-Muller变换生成正态分布随机数
            while True:
                x1 = 2.0 * rand.random() - 1.0
                x2 = 2.0 * rand.random() - 1.0
                x = x1 * x1 + x2 * x2
                if x < 1.0:
                    break
            
            r = np.sqrt(-2.0 * np.log(x) / x)
            watermark.append(x1 * r)
            if i + 1 < watermark_length:
                watermark.append(x2 * r)
        
        # 创建签名
        sig = {
            'watermark_length': watermark_length,
            'wavelet_filter_method': self.DEFAULT_WAVELET_FILTER_METHOD,
            'filter_id': self.DEFAULT_FILTER_ID,
            'decomposition_level': self.DEFAULT_DECOMPOSITION_LEVEL,
            'alpha': self.DEFAULT_ALPHA,
            'casting_threshold': self.DEFAULT_CASTING_THRESHOLD,
            'detection_threshold': self.DEFAULT_DETECTION_THRESHOLD,
            'watermark': np.array(watermark, dtype=np.float64)
        }
        
        return self._save_signature(sig)
    
    def get_watermark_correlation(self, orig_sig_data: bytes,
                                  watermark_data: bytes) -> float:
        """获取水印相关性"""
        try:
            # 读取原始签名
            sig = self._load_signature(orig_sig_data)
            
            # 解析水印数据
            if len(watermark_data) < len(self.WM_MARKER):
                raise StegaPyException(
                    "无效的水印数据",
                    StegaPyErrors.ERR_SIG_NOT_VALID,
                    self.NAMESPACE
                )
            
            if watermark_data[:len(self.WM_MARKER)] != self.WM_MARKER:
                raise StegaPyException(
                    "无效的水印标记",
                    StegaPyErrors.ERR_SIG_NOT_VALID,
                    self.NAMESPACE
                )
            
            offset = len(self.WM_MARKER)
            level = struct.unpack('>i', watermark_data[offset:offset+4])[0]
            # 从水印数据中读取alpha
            alpha = struct.unpack('>d', watermark_data[offset+4:offset+12])[0]
            
            offset += 12  # 跳过level和alpha
            n = level * 3
            ok = 0
            
            # 调试信息：统计z、v、alpha的值
            debug_info = []
            
            for i in range(level):
                # HL子带
                if offset + 20 > len(watermark_data):
                    break
                m = struct.unpack('>i', watermark_data[offset:offset+4])[0]
                z = struct.unpack('>d', watermark_data[offset+4:offset+12])[0]
                v = struct.unpack('>d', watermark_data[offset+12:offset+20])[0]
                offset += 20
                
                if m != 0:
                    threshold = v * alpha
                    # 检测条件：z > v * alpha
                    is_match = z > threshold
                    if is_match:
                        ok += 1
                    debug_info.append(('HL', i, m, z, v, alpha, threshold, is_match))
                else:
                    n -= 1
                
                # LH子带
                if offset + 20 > len(watermark_data):
                    break
                m = struct.unpack('>i', watermark_data[offset:offset+4])[0]
                z = struct.unpack('>d', watermark_data[offset+4:offset+12])[0]
                v = struct.unpack('>d', watermark_data[offset+12:offset+20])[0]
                offset += 20
                
                if m != 0:
                    threshold = v * alpha
                    # 检测条件：z > v * alpha
                    is_match = z > threshold
                    if is_match:
                        ok += 1
                    debug_info.append(('LH', i, m, z, v, alpha, threshold, is_match))
                else:
                    n -= 1
                
                # HH子带
                if offset + 20 > len(watermark_data):
                    break
                m = struct.unpack('>i', watermark_data[offset:offset+4])[0]
                z = struct.unpack('>d', watermark_data[offset+4:offset+12])[0]
                v = struct.unpack('>d', watermark_data[offset+12:offset+20])[0]
                offset += 20
                
                if m != 0:
                    threshold = v * alpha
                    # 检测条件：z > v * alpha
                    is_match = z > threshold
                    if is_match:
                        ok += 1
                    debug_info.append(('HH', i, m, z, v, alpha, threshold, is_match))
                else:
                    n -= 1
            
            if n == 0:
                return 0.0
            
            correlation = float(ok) / float(n)
            
            # 将调试信息存储到实例变量中，供外部访问
            self._last_correlation_debug = {
                'correlation': correlation,
                'ok': ok,
                'n': n,
                'alpha': alpha,
                'debug_info': debug_info
            }
            
            return correlation
        except Exception as e:
            raise StegaPyException(str(e), StegaPyErrors.UNHANDLED_EXCEPTION, self.NAMESPACE)
    
    def get_high_watermark_level(self) -> float:
        """获取高水印阈值"""
        return 0.7
    
    def get_low_watermark_level(self) -> float:
        """获取低水印阈值"""
        return 0.3
    
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
        return ['png', 'bmp']
    
    def _wm_subband(self, img_data, watermark, n, alpha, threshold):
        """在子带中嵌入水印"""
        flat_data = img_data.flatten()
        for i in range(len(flat_data)):
            if abs(flat_data[i]) > threshold:
                flat_data[i] += alpha * abs(flat_data[i]) * watermark[i % n]
        img_data[:] = flat_data.reshape(img_data.shape)
    
    def _inv_wm_subband(self, img_data, watermark, n, threshold):
        """从子带中提取水印
        
        提取逻辑：
        - 嵌入时：使用 abs(flat_data[i]) > threshold 判断
        - 提取时：使用 flat_data[i] > threshold 判断（只处理正数系数）
        
        这是原始算法的设计，只提取正数系数来计算相关性。
        
        Args:
            img_data: 图像子带数据
            watermark: 水印数据
            n: 水印长度
            threshold: 阈值
        """
        flat_data = img_data.flatten()
        m = 0
        z = 0.0
        v = 0.0
        
        for i in range(len(flat_data)):
            # 只处理正数系数
            if flat_data[i] > threshold:
                z += flat_data[i] * watermark[i % n]
                v += abs(flat_data[i])
                m += 1
        
        return (m, z, v)
    
    def _create_signature_from_message(self, msg: bytes):
        """从消息创建签名（用于数据隐藏模式）"""
        # 使用消息的哈希作为随机种子
        seed = int.from_bytes(msg[:16] if len(msg) >= 16 else msg + b'\x00' * (16 - len(msg)), 'big')
        rand = random.Random(seed)
        
        watermark_length = self.DEFAULT_WATERMARK_LENGTH
        watermark = []
        
        for i in range(0, watermark_length, 2):
            while True:
                x1 = 2.0 * rand.random() - 1.0
                x2 = 2.0 * rand.random() - 1.0
                x = x1 * x1 + x2 * x2
                if x < 1.0:
                    break
            r = np.sqrt(-2.0 * np.log(x) / x)
            watermark.append(x1 * r)
            if i + 1 < watermark_length:
                watermark.append(x2 * r)
        
        return {
            'watermark_length': watermark_length,
            'wavelet_filter_method': self.DEFAULT_WAVELET_FILTER_METHOD,
            'filter_id': self.DEFAULT_FILTER_ID,
            'decomposition_level': self.DEFAULT_DECOMPOSITION_LEVEL,
            'alpha': self.DEFAULT_ALPHA,
            'casting_threshold': self.DEFAULT_CASTING_THRESHOLD,
            'detection_threshold': self.DEFAULT_DETECTION_THRESHOLD,
            'watermark': np.array(watermark, dtype=np.float64)
        }
    
    def _save_signature(self, sig: dict) -> bytes:
        """保存签名到字节数组
        
        使用二进制格式保存签名数据。
        格式：标记 + watermark_length + wavelet_filter_method + filter_id + 
              decomposition_level + alpha + casting_threshold + detection_threshold + 
              watermark数据（每个double 8字节）
        """
        output = io.BytesIO()
        output.write(self.SIG_MARKER)
        output.write(struct.pack('>i', sig['watermark_length']))
        output.write(struct.pack('>i', sig.get('wavelet_filter_method', self.DEFAULT_WAVELET_FILTER_METHOD)))
        output.write(struct.pack('>i', sig.get('filter_id', self.DEFAULT_FILTER_ID)))
        output.write(struct.pack('>i', sig['decomposition_level']))
        output.write(struct.pack('>d', sig['alpha']))
        output.write(struct.pack('>d', sig['casting_threshold']))
        output.write(struct.pack('>d', sig['detection_threshold']))
        
        for w in sig['watermark']:
            output.write(struct.pack('>d', w))
        
        return output.getvalue()
    
    def _load_signature(self, sig_data: bytes) -> dict:
        """从字节数组加载签名
        
        支持两种格式：
        1. 序列化格式：包含序列化头部的二进制格式
        2. 直接二进制格式：以标记开头的二进制格式
        """
        # 首先尝试查找标记位置（支持包含序列化头部的格式和直接二进制格式）
        marker_pos = sig_data.find(self.SIG_MARKER)
        if marker_pos == -1:
            raise StegaPyException(
                "无法找到签名标记，签名文件可能已损坏或格式不正确",
                StegaPyErrors.ERR_SIG_NOT_VALID,
                self.NAMESPACE
            )
        
        # 从标记后开始读取
        offset = marker_pos + len(self.SIG_MARKER)
        
        # 验证offset是否在有效范围内
        if offset + 16 > len(sig_data):
            raise StegaPyException(
                "签名数据不完整",
                StegaPyErrors.ERR_SIG_NOT_VALID,
                self.NAMESPACE
            )
        
        watermark_length = struct.unpack('>i', sig_data[offset:offset+4])[0]
        offset += 4
        
        # 验证watermark_length是否合理
        if watermark_length < 0 or watermark_length > 100000:
            raise StegaPyException(
                f"无效的水印长度: {watermark_length}",
                StegaPyErrors.ERR_SIG_NOT_VALID,
                self.NAMESPACE
            )
        
        # 读取wavelet_filter_method
        wavelet_filter_method = struct.unpack('>i', sig_data[offset:offset+4])[0]
        offset += 4
        # 读取filter_id
        filter_id = struct.unpack('>i', sig_data[offset:offset+4])[0]
        offset += 4
        
        # 验证offset是否足够读取decomposition_level
        if offset + 4 > len(sig_data):
            raise StegaPyException(
                "签名数据不完整，无法读取分解层级",
                StegaPyErrors.ERR_SIG_NOT_VALID,
                self.NAMESPACE
            )
        
        decomposition_level = struct.unpack('>i', sig_data[offset:offset+4])[0]
        offset += 4
        
        # 验证decomposition_level是否合理
        if decomposition_level < 1 or decomposition_level > 10:
            raise StegaPyException(
                f"无效的分解层级: {decomposition_level}（必须在1-10之间）",
                StegaPyErrors.ERR_SIG_NOT_VALID,
                self.NAMESPACE
            )
        alpha = struct.unpack('>d', sig_data[offset:offset+8])[0]
        offset += 8
        casting_threshold = struct.unpack('>d', sig_data[offset:offset+8])[0]
        offset += 8
        detection_threshold = struct.unpack('>d', sig_data[offset:offset+8])[0]
        offset += 8
        
        watermark = []
        for i in range(watermark_length):
            if offset + 8 > len(sig_data):
                break
            watermark.append(struct.unpack('>d', sig_data[offset:offset+8])[0])
            offset += 8
        
        return {
            'watermark_length': watermark_length,
            'wavelet_filter_method': wavelet_filter_method,
            'filter_id': filter_id,
            'decomposition_level': decomposition_level,
            'alpha': alpha,
            'casting_threshold': casting_threshold,
            'detection_threshold': detection_threshold,
            'watermark': np.array(watermark, dtype=np.float64)
        }

