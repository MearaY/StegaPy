"""
插件管理器

Copyright (C) 2025  MearaY

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License along
with this program; if not, write to the Free Software Foundation, Inc.,
51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""

from typing import List, Optional, Dict
from .plugin.base import StegaPyPlugin
from .plugin.lsb import LSBPlugin
from .plugin.randlsb import RandomLSBPlugin
from .plugin.dwtdugad import DWTDugadPlugin


class PluginManager:
    """插件管理器类"""
    
    _plugins: Dict[str, StegaPyPlugin] = {}
    _initialized = False
    
    @classmethod
    def load_plugins(cls):
        """加载所有插件"""
        if cls._initialized:
            return
        
        # 注册内置插件
        cls._plugins['LSB'] = LSBPlugin()
        cls._plugins['RandomLSB'] = RandomLSBPlugin()
        cls._plugins['DWTDugad'] = DWTDugadPlugin()
        
        cls._initialized = True
    
    @classmethod
    def get_plugin_by_name(cls, name: str) -> Optional[StegaPyPlugin]:
        """根据名称获取插件"""
        if not cls._initialized:
            cls.load_plugins()
        return cls._plugins.get(name)
    
    @classmethod
    def get_all_plugins(cls) -> List[StegaPyPlugin]:
        """获取所有插件"""
        if not cls._initialized:
            cls.load_plugins()
        return list(cls._plugins.values())
    
    @classmethod
    def get_plugins_by_purpose(cls, purpose):
        """根据用途获取插件"""
        if not cls._initialized:
            cls.load_plugins()
        
        result = []
        for plugin in cls._plugins.values():
            if purpose in plugin.get_purposes():
                result.append(plugin)
        return result

