# Auto-generated utility file

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
    

    def _decompress_data(self, data: bytes) -> bytes:
        """解压数据"""
        # 检查数据是否为空
        if not data or len(data) == 0:
            raise StegaPyException(
                "数据为空，无法解压",
                StegaPyErrors.CORRUPT_DATA,
                self.NAMESPACE
            )
        
        # 检查数据是否是有效的 gzip 格式
        # gzip 文件以 \x1f\x8b 开头
        if len(data) < 2 or data[:2] != b'\x1f\x8b':
            raise StegaPyException(
                "数据不是有效的 gzip 格式。请检查：\n"
                "1. 嵌入数据时是否启用了压缩\n"
                "2. 提取数据时的压缩设置是否与嵌入时一致\n"
                f"数据前2字节: {data[:2].hex() if len(data) >= 2 else '数据太短'}",
                StegaPyErrors.CORRUPT_DATA,
                self.NAMESPACE
            )
        
        try:
            return gzip.decompress(data)
        except gzip.BadGzipFile as e:
            raise StegaPyException(
                f"数据解压失败（不是有效的 gzip 文件）: {str(e)}\n"
                "请检查压缩设置是否与嵌入时一致",
                StegaPyErrors.CORRUPT_DATA,
                self.NAMESPACE
            )
        except Exception as e:
            raise StegaPyException(
                f"数据解压失败: {str(e)}\n"
                "请检查压缩设置是否与嵌入时一致",
                StegaPyErrors.CORRUPT_DATA,
                self.NAMESPACE
            )


