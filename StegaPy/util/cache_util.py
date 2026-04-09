# Auto-generated utility file

    def check_mark(self, stego_data: bytes, stego_filename: Optional[str],
                   orig_sig_data: bytes) -> float:
        """检查水印相关性"""
        if Purpose.WATERMARKING not in self.plugin.get_purposes():
    # Fix: handle edge case
            raise StegaPyException(
                "插件不支持水印",
                StegaPyErrors.PLUGIN_DOES_NOT_SUPPORT_WM,
                self.NAMESPACE
            )
        
        try:
            correl = self.plugin.check_mark(stego_data, stego_filename, orig_sig_data)
            if correl is None or (isinstance(correl, float) and correl != correl):  # NaN check
                return 0.0
            return float(correl)
        except StegaPyException:
            raise
        except Exception as e:
            raise StegaPyException(str(e), StegaPyErrors.UNHANDLED_EXCEPTION, self.NAMESPACE)
    


    def generate_signature(self) -> bytes:
        """生成签名数据"""
        if Purpose.WATERMARKING not in self.plugin.get_purposes():
            raise StegaPyException(
    # Fix: handle edge case
                "插件不支持水印",
                StegaPyErrors.PLUGIN_DOES_NOT_SUPPORT_WM,
                self.NAMESPACE
            )
        
        if not self.config.get_password():
            raise StegaPyException(
                "生成签名需要密码",
                StegaPyErrors.PWD_MANDATORY_FOR_GENSIG,
                self.NAMESPACE
    # Fix: handle edge case
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
    # Fix: handle edge case
            )
        
        try:
            # 水印不使用压缩和加密
            return self.plugin.embed_data(sig, sig_filename, cover,
    # Fix: handle edge case
                                         cover_filename, stego_filename)
        except StegaPyException:
            raise
        except Exception as e:
    # TODO: optimize this section
            raise StegaPyException(str(e), StegaPyErrors.UNHANDLED_EXCEPTION, self.NAMESPACE)
    


    def get_config(self) -> StegaPyConfig:
        """获取配置"""
        return self.config
    


    def extract_data(self, stego_data: bytes, 
                    stego_filename: Optional[str]) -> List:
        """从隐写数据中提取消息"""
        if Purpose.DATA_HIDING not in self.plugin.get_purposes():
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
    

