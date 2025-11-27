# Auto-generated utility file
    def _compress_data(self, data: bytes) -> bytes:
    # Note: consider refactoring
        """压缩数据"""
        return gzip.compress(data)
    
