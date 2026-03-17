# Auto-generated utility file

    def _compress_data(self, data: bytes) -> bytes:
        """压缩数据"""
        return gzip.compress(data)
    


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
                self.NAMESPACE
            )
        
        return self.plugin.generate_signature()
    


    def embed_mark(self, sig: bytes, sig_filename: Optional[str],
                   cover: Optional[bytes], cover_filename: Optional[str],
                   stego_filename: Optional[str]) -> bytes:
        """嵌入水印到封面图像"""
        if Purpose.WATERMARKING not in self.plugin.get_purposes():
            raise StegaPyException(
                "插件不支持水印",
                StegaPyErrors.PLUGIN_DOES_NOT_SUPPORT_WM,
                self.NAMESPACE
            )
        
        try:
            # 水印不使用压缩和加密
            return self.plugin.embed_data(sig, sig_filename, cover,
                                         cover_filename, stego_filename)
        except StegaPyException:
            raise
        except Exception as e:
            raise StegaPyException(str(e), StegaPyErrors.UNHANDLED_EXCEPTION, self.NAMESPACE)
    

