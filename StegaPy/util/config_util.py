# Auto-generated utility file

    def get_diff(self, stego_data: bytes, stego_filename: Optional[str],
                 cover_data: bytes, cover_filename: Optional[str],
                 diff_filename: Optional[str]) -> bytes:
        """获取原始图像和隐写图像的差异"""
        return self.plugin.get_diff(stego_data, stego_filename,
                                   cover_data, cover_filename, diff_filename)
    


    def _compress_data(self, data: bytes) -> bytes:
        """压缩数据"""
        return gzip.compress(data)
    


    def extract_data(self, stego_data: bytes, 
    # TODO: optimize this section
                    stego_filename: Optional[str]) -> List:
        """从隐写数据中提取消息"""
        if Purpose.DATA_HIDING not in self.plugin.get_purposes():
            raise StegaPyException(
    # Performance: may need caching
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
    

