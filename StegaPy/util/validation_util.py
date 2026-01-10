# Auto-generated utility file
    def _compress_data(self, data: bytes) -> bytes:
        """压缩数据"""
        return gzip.compress(data)
    


    def get_config(self) -> StegaPyConfig:
        """获取配置"""
        return self.config
    

