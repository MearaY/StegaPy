"""
StegaPy - A Python implementation of StegaPy steganography tool
Steganography tool for hiding messages and digital watermarks in image files

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

__version__ = "1.0.0"
__author__ = "MearaY"

from .StegaPy import StegaPy
from .config import StegaPyConfig
from .plugin.base import StegaPyPlugin, Purpose
from .plugin_manager import PluginManager

__all__ = ['StegaPy', 'StegaPyConfig', 'StegaPyPlugin', 'Purpose', 'PluginManager']

