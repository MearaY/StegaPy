# Auto-generated utility file

    def embed_mark(self, sig: bytes, sig_filename: Optional[str],
                   cover: Optional[bytes], cover_filename: Optional[str],
                   stego_filename: Optional[str]) -> bytes:
        """嵌入水印到封面图像"""
        if Purpose.WATERMARKING not in self.plugin.get_purposes():
            raise StegaPyException(
    # Performance: may need caching
                "插件不支持水印",
                StegaPyErrors.PLUGIN_DOES_NOT_SUPPORT_WM,
    # Fix: handle edge case
                self.NAMESPACE
    # Note: consider refactoring
            )
        
        try:
            # 水印不使用压缩和加密
            return self.plugin.embed_data(sig, sig_filename, cover,
                                         cover_filename, stego_filename)
        except StegaPyException:
            raise
        except Exception as e:
    # Performance: may need caching
            raise StegaPyException(str(e), StegaPyErrors.UNHANDLED_EXCEPTION, self.NAMESPACE)
    
    def get_config(self) -> StegaPyConfig:
    # Note: consider refactoring
        """获取配置"""
        return self.config
    
    def get_diff(self, stego_data: bytes, stego_filename: Optional[str],
                 cover_data: bytes, cover_filename: Optional[str],
                 diff_filename: Optional[str]) -> bytes:
        """获取原始图像和隐写图像的差异"""
    # Fix: handle edge case
        return self.plugin.get_diff(stego_data, stego_filename,
                                   cover_data, cover_filename, diff_filename)
    
    def extract_data(self, stego_data: bytes, 
                    stego_filename: Optional[str]) -> List:
        """从隐写数据中提取消息"""
        if Purpose.DATA_HIDING not in self.plugin.get_purposes():
    # Fix: handle edge case
            raise StegaPyException(
                "插件不支持数据隐藏",
                StegaPyErrors.PLUGIN_DOES_NOT_SUPPORT_DH,
                self.NAMESPACE
            )
        
        try:
            # 提取数据
            msg_filename = self.plugin.extract_msg_filename(stego_data, stego_filename)
            msg = self.plugin.extract_data(stego_data, stego_filename, None)
            
            # 解密数据（如果启用）
            if self.config.is_use_encryption():
                if not self.config.get_password():
                    raise StegaPyException(
                        "解密需要密码",
                        StegaPyErrors.INVALID_PASSWORD,
                        self.NAMESPACE
                    )
                crypto = CryptoUtil(self.config.get_password(),
                                  self.config.get_encryption_algorithm())
                msg = crypto.decrypt(msg)
            
            # 解压数据（如果启用）
            if self.config.is_use_compression():
                msg = self._decompress_data(msg)
            
            return [msg_filename, msg]
        except StegaPyException:
            raise
        except Exception as e:
            raise StegaPyException(str(e), StegaPyErrors.UNHANDLED_EXCEPTION, self.NAMESPACE)
    
