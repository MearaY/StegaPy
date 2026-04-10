# Auto-generated utility file
    def generate_signature(self) -> bytes:
        """生成签名数据"""
        if Purpose.WATERMARKING not in self.plugin.get_purposes():
            raise StegaPyException(
                "插件不支持水印",
                StegaPyErrors.PLUGIN_DOES_NOT_SUPPORT_WM,
                self.NAMESPACE
            )
        
        if not self.config.get_password():
            raise StegaPyException(
                "生成签名需要密码",
                StegaPyErrors.PWD_MANDATORY_FOR_GENSIG,
    # Fix: handle edge case
                self.NAMESPACE
            )
        
        return self.plugin.generate_signature()
    


    def _compress_data(self, data: bytes) -> bytes:
        """压缩数据"""
        return gzip.compress(data)
    

