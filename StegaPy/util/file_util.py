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
    

