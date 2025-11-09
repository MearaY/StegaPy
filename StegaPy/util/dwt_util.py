"""
离散小波变换工具
"""

import numpy as np
import pywt


class DWTUtil:
    """离散小波变换工具类"""
    
    @staticmethod
    def forward_dwt(image_data, wavelet='db1', level=3):
        """
        执行正向小波变换
        
        Args:
            image_data: 2D numpy数组，图像数据
            wavelet: 小波基名称，默认'db1'（Daubechies 1）
            level: 分解层数，默认3
        
        Returns:
            小波系数列表，格式为 [cA, (cH, cV, cD), ...]
        """
        coeffs = pywt.wavedec2(image_data, wavelet, level=level)
        return coeffs
    
    @staticmethod
    def inverse_dwt(coeffs, wavelet='db1'):
        """
        执行逆向小波变换
        
        Args:
            coeffs: 小波系数列表
            wavelet: 小波基名称
        
        Returns:
            重构后的图像数据
        """
        return pywt.waverec2(coeffs, wavelet)
    
    @staticmethod
    def get_subbands(coeffs):
        """
        从小波系数中提取子带
        
        Args:
            coeffs: 小波系数列表
        
        Returns:
            子带列表，每个元素为 (level, subband_type, data)
        """
        subbands = []
        cA = coeffs[0]  # 近似系数
        
        for i, (cH, cV, cD) in enumerate(coeffs[1:]):
            level = i + 1
            subbands.append((level, 'H', cH))  # 水平细节
            subbands.append((level, 'V', cV))  # 垂直细节
            subbands.append((level, 'D', cD))  # 对角细节
        
        return subbands
    
    @staticmethod
    def reconstruct_subbands(subbands, original_coeffs, wavelet='db1'):
        """
        从子带重构小波系数
        
        Args:
            subbands: 修改后的子带列表
            original_coeffs: 原始小波系数结构
            wavelet: 小波基名称
        
        Returns:
            重构的小波系数列表
        """
        # 重建系数结构
        new_coeffs = [original_coeffs[0]]  # 保留近似系数
        
        # 按层级组织子带
        max_level = max(s[0] for s in subbands)
        for level in range(1, max_level + 1):
            level_subbands = {s[1]: s[2] for s in subbands if s[0] == level}
            cH = level_subbands.get('H', original_coeffs[level][0])
            cV = level_subbands.get('V', original_coeffs[level][1])
            cD = level_subbands.get('D', original_coeffs[level][2])
            new_coeffs.append((cH, cV, cD))
        
        return new_coeffs

