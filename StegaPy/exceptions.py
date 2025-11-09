"""
异常处理模块
"""


class StegaPyException(Exception):
    """StegaPy基础异常类"""
    
    UNHANDLED_EXCEPTION = "UNHANDLED_EXCEPTION"
    
    def __init__(self, message=None, error_code=None, namespace=None, *args):
        """初始化异常"""
        self.error_code = error_code or self.UNHANDLED_EXCEPTION
        self.namespace = namespace
        self.args = args
        
        if message:
            self.message = message
        else:
            self.message = f"StegaPy错误: {self.error_code}"
            if args:
                self.message += f" - {', '.join(str(a) for a in args)}"
        
        super().__init__(self.message)
    
    def get_error_code(self):
        """获取错误代码"""
        return self.error_code
    
    def get_namespace(self):
        """获取命名空间"""
        return self.namespace


class StegaPyErrors:
    """错误代码常量"""
    UNHANDLED_EXCEPTION = "UNHANDLED_EXCEPTION"
    NO_PLUGIN_SPECIFIED = "NO_PLUGIN_SPECIFIED"
    PLUGIN_DOES_NOT_SUPPORT_DH = "PLUGIN_DOES_NOT_SUPPORT_DH"
    PLUGIN_DOES_NOT_SUPPORT_WM = "PLUGIN_DOES_NOT_SUPPORT_WM"
    PWD_MANDATORY_FOR_GENSIG = "PWD_MANDATORY_FOR_GENSIG"
    CORRUPT_DATA = "CORRUPT_DATA"
    INVALID_CRYPT_ALGO = "INVALID_CRYPT_ALGO"
    INVALID_PASSWORD = "INVALID_PASSWORD"
    ERR_NO_COVER_FILE = "ERR_NO_COVER_FILE"
    ERR_FILE_TOO_SMALL = "ERR_FILE_TOO_SMALL"
    ERR_SIG_NOT_VALID = "ERR_SIG_NOT_VALID"
    ERR_IMAGE_DATA_READ = "ERR_IMAGE_DATA_READ"

