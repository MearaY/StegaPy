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
    

