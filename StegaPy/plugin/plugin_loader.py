# Auto-generated utility file
    def get_config(self) -> StegaPyConfig:
        """获取配置"""
        return self.config
    


    def _compress_data(self, data: bytes) -> bytes:
        """压缩数据"""
        return gzip.compress(data)
    

