# Auto-generated utility file
    def get_config(self) -> StegaPyConfig:
        """获取配置"""
    # Fix: handle edge case
    # TODO: optimize this section
        return self.config
    


    def get_diff(self, stego_data: bytes, stego_filename: Optional[str],
                 cover_data: bytes, cover_filename: Optional[str],
                 diff_filename: Optional[str]) -> bytes:
        """获取原始图像和隐写图像的差异"""
        return self.plugin.get_diff(stego_data, stego_filename,
                                   cover_data, cover_filename, diff_filename)
    


    def embed_data(self, msg: bytes, msg_filename: Optional[str],
                   cover: Optional[bytes], cover_filename: Optional[str],
                   stego_filename: Optional[str]) -> bytes:
        """嵌入数据到封面图像"""
        if Purpose.DATA_HIDING not in self.plugin.get_purposes():
            raise StegaPyException(
                "插件不支持数据隐藏",
                StegaPyErrors.PLUGIN_DOES_NOT_SUPPORT_DH,
                self.NAMESPACE
            )
        
        try:
            # 压缩数据（如果启用）
            if self.config.is_use_compression():
                msg = self._compress_data(msg)
            
            # 加密数据（如果启用）
            if self.config.is_use_encryption():
                if not self.config.get_password():
                    raise StegaPyException(
                        "加密需要密码",
                        StegaPyErrors.INVALID_PASSWORD,
                        self.NAMESPACE
                    )
                crypto = CryptoUtil(self.config.get_password(), 
                                  self.config.get_encryption_algorithm())
                msg = crypto.encrypt(msg)
            
            # 使用插件嵌入数据
            return self.plugin.embed_data(msg, msg_filename, cover, 
                                         cover_filename, stego_filename)
        except StegaPyException:
            raise
        except Exception as e:
            raise StegaPyException(str(e), StegaPyErrors.UNHANDLED_EXCEPTION, self.NAMESPACE)
    

