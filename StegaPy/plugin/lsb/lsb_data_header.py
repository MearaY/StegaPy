"""
LSB数据头
"""

import struct
from ...config import StegaPyConfig


class LSBDataHeader:
    """LSB数据头类，用于存储嵌入数据的元信息"""
    
    # 数据头标记（9字节）
    DATA_STAMP = b"STEGAPY  "  # 9字节，StegaPy项目标记
    HEADER_VERSION = b'\x02'  # 1字节，版本2
    FIXED_HEADER_LENGTH = 8  # 固定头长度
    CRYPT_ALGO_LENGTH = 8  # 加密算法名称长度
    MAX_FILENAME_LENGTH = 255  # 最大文件名长度
    
    def __init__(self, data_length=0, channel_bits_used=1, filename=None, config=None):
        """初始化数据头
        
        Args:
            data_length: 数据长度（不包括头）
            channel_bits_used: 每个颜色通道使用的位数
            filename: 文件名
            config: StegaPyConfig配置对象
        """
        self.data_length = data_length
        self.channel_bits_used = channel_bits_used
        self.filename = filename or ""
        self.config = config
        
        if len(self.filename.encode('utf-8')) > self.MAX_FILENAME_LENGTH:
            raise ValueError(f"文件名编码后长度不能超过{self.MAX_FILENAME_LENGTH}字节")
    
    def get_data_length(self):
        """获取数据长度"""
        return self.data_length
    
    def get_filename(self):
        """获取文件名"""
        return self.filename
    
    def get_channel_bits_used(self):
        """获取每个通道使用的位数"""
        return self.channel_bits_used
    
    def to_bytes(self):
        """转换为字节数组"""
        filename_bytes = self.filename.encode('utf-8')
        filename_len = len(filename_bytes)
        
        if filename_len > self.MAX_FILENAME_LENGTH:
            raise ValueError(f"文件名编码后长度超过{self.MAX_FILENAME_LENGTH}字节")
        
        # 构建头数据
        header = bytearray()
        
        # 1. DATA_STAMP (9字节)
        header.extend(self.DATA_STAMP)
        
        # 2. HEADER_VERSION (1字节)
        header.extend(self.HEADER_VERSION)
        
        # 3. FIXED_HEADER (8字节)
        # dataLength (4字节，小端序)
        header.extend(struct.pack('<I', self.data_length))
        # channelBitsUsed (1字节)
        header.append(self.channel_bits_used)
        # fileNameLen (1字节)
        header.append(filename_len)
        # useCompression (1字节)
        use_compression = 1 if (self.config and self.config.is_use_compression()) else 0
        header.append(use_compression)
        # useEncryption (1字节)
        use_encryption = 1 if (self.config and self.config.is_use_encryption()) else 0
        header.append(use_encryption)
        
        # 4. CRYPT_ALGO (8字节)
        if self.config and self.config.get_encryption_algorithm():
            crypt_algo = self.config.get_encryption_algorithm().encode('utf-8')
            # 截断或填充到8字节
            if len(crypt_algo) > self.CRYPT_ALGO_LENGTH:
                crypt_algo = crypt_algo[:self.CRYPT_ALGO_LENGTH]
            else:
                crypt_algo = crypt_algo.ljust(self.CRYPT_ALGO_LENGTH, b' ')
        else:
            crypt_algo = b' ' * self.CRYPT_ALGO_LENGTH
        header.extend(crypt_algo)
        
        # 5. fileName (变长)
        if filename_len > 0:
            header.extend(filename_bytes)
        
        return bytes(header)
    
    @staticmethod
    def from_bytes(data, config=None):
        """从字节数组解析数据头
        
        Args:
            data: 字节数组
            config: StegaPyConfig配置对象（会被更新）
        
        Returns:
            LSBDataHeader对象
        """
        if config is None:
            from ...config import StegaPyConfig
            config = StegaPyConfig()
        
        offset = 0
        
        # 1. 检查DATA_STAMP (9字节)
        stamp_len = len(LSBDataHeader.DATA_STAMP)
        if len(data) < offset + stamp_len:
            raise ValueError("数据头长度不足，无法读取DATA_STAMP")
        stamp = data[offset:offset+stamp_len]
        if stamp != LSBDataHeader.DATA_STAMP:
            raise ValueError(f"无效的数据头标记，期望'STEGAPY  '，实际为'{stamp.decode('utf-8', errors='ignore')}'")
        offset += stamp_len
        
        # 2. 检查HEADER_VERSION (1字节)
        version_len = len(LSBDataHeader.HEADER_VERSION)
        if len(data) < offset + version_len:
            raise ValueError("数据头长度不足，无法读取HEADER_VERSION")
        version = data[offset:offset+version_len]
        if version != LSBDataHeader.HEADER_VERSION:
            raise ValueError(f"无效的头版本，期望版本2，实际为{version[0]}")
        offset += version_len
        
        # 3. 读取FIXED_HEADER (8字节)
        if len(data) < offset + LSBDataHeader.FIXED_HEADER_LENGTH:
            raise ValueError("数据头长度不足，无法读取FIXED_HEADER")
        fixed_header = data[offset:offset+LSBDataHeader.FIXED_HEADER_LENGTH]
        # dataLength (4字节，小端序)
        data_length = struct.unpack('<I', fixed_header[0:4])[0]
        # channelBitsUsed (1字节)
        channel_bits_used = fixed_header[4]
        # fileNameLen (1字节)
        filename_len = fixed_header[5]
        # useCompression (1字节)
        config.set_use_compression(fixed_header[6] == 1)
        # useEncryption (1字节)
        config.set_use_encryption(fixed_header[7] == 1)
        offset += LSBDataHeader.FIXED_HEADER_LENGTH
        
        # 4. 读取CRYPT_ALGO (8字节)
        if len(data) < offset + LSBDataHeader.CRYPT_ALGO_LENGTH:
            raise ValueError("数据头长度不足，无法读取CRYPT_ALGO")
        crypt_algo = data[offset:offset+LSBDataHeader.CRYPT_ALGO_LENGTH]
        # 去除尾部空格
        crypt_algo_str = crypt_algo.rstrip(b' ').decode('utf-8', errors='ignore')
        if crypt_algo_str:
            config.set_encryption_algorithm(crypt_algo_str)
        offset += LSBDataHeader.CRYPT_ALGO_LENGTH
        
        # 5. 读取fileName (变长)
        if filename_len > LSBDataHeader.MAX_FILENAME_LENGTH:
            raise ValueError(f"文件名长度无效: {filename_len}")
        if len(data) < offset + filename_len:
            raise ValueError("数据头不完整，无法读取文件名")
        filename = ""
        if filename_len > 0:
            filename = data[offset:offset+filename_len].decode('utf-8')
        
        return LSBDataHeader(data_length, channel_bits_used, filename, config)
    
    @staticmethod
    def get_max_header_size():
        """获取最大数据头大小"""
        return (len(LSBDataHeader.DATA_STAMP) + 
                len(LSBDataHeader.HEADER_VERSION) + 
                LSBDataHeader.FIXED_HEADER_LENGTH + 
                LSBDataHeader.CRYPT_ALGO_LENGTH + 
                LSBDataHeader.MAX_FILENAME_LENGTH)
    
    def get_header_size(self):
        """获取当前数据头的实际大小"""
        filename_len = len(self.filename.encode('utf-8'))
        return (len(self.DATA_STAMP) + 
                len(self.HEADER_VERSION) + 
                self.FIXED_HEADER_LENGTH + 
                self.CRYPT_ALGO_LENGTH + 
                filename_len)

