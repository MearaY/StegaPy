# StegaPy

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-GPLv2-green.svg)](LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/MearaY/StegaPy.svg?style=social&label=Star)](https://github.com/MearaY/StegaPy)
[![Code Lines](https://img.shields.io/badge/code%20lines-2236%2B-orange.svg)](https://github.com/MearaY/StegaPy)

**语言**: 中文 | [English](README_en.md)

**StegaPy** 是一个基于 Python 的信息隐藏（隐写）工具，灵感来自 [OpenStego](https://github.com/syvaidya/openstego)。它是一个强大的隐写术工具，用于在图像文件中隐藏数据和嵌入数字水印。

## 📋 关于项目

本项目是一个基于 Python 的隐写术工具，灵感来自 OpenStego 项目。采用Python语言开发，在实现核心功能的同时引入了一些改进和扩展。请注意，这是一个进行中的项目，可能存在功能不完整或不足之处，后续会持续补充和维护。

- 🔄 **功能实现**: 主要隐写和水印算法
- 🌐 **现代化 Web 界面**: 基于 Streamlit 构建的交互式 Web 应用，使用更便捷
- 📝 **代码质量**: 符合 PEP 8 规范，包含类型提示和文档
- 🏗️ **模块化设计**: 基于插件的架构，便于维护
- 💻 **跨平台支持**: 原生 Python 跨平台支持，部署更便捷
- 📦 **Python 生态**: 利用 NumPy、Pillow 等库提升性能

**注意**: 这是一个实验性项目，部分功能可能尚未完全实现或测试。欢迎反馈。


## 🚀 快速开始

### 环境安装

#### 使用 Conda（推荐）

```bash
# 创建 conda 环境
conda env create -f environment.yml

# 激活环境
conda activate StegaPy
```

#### 使用 pip

```bash
# 安装依赖
pip install -r requirements.txt

# 安装包（开发模式）
pip install -e .
```

### Web 界面启动

启动 Streamlit Web 应用：

```bash
# 使用默认端口
streamlit run app.py

# 或指定自定义端口（推荐使用未被占用的端口，如 8501）
streamlit run app.py --server.port 8501
```

Web 界面提供完整功能，包括：
- 数据隐藏（嵌入/提取）
- 数字水印（生成/嵌入/验证）
- 图像差异可视化
- 实时处理反馈

## 📁 项目结构

```
StegaPy/
├── StegaPy/          # 主包
│   ├── plugin/         # 插件模块（LSB、RandomLSB、DWT等）
│   └── util/           # 工具模块
├── app.py              # Streamlit 应用
├── data/               # 数据目录
├── requirements.txt    # pip 依赖
└── README.md          # 说明文档
```

## 📄 许可证

本项目采用 **GNU 通用公共许可证 v2.0 (GPL-2.0)**。

**完整许可证文本请参见**: [LICENSE](LICENSE)

## 🙏 致谢

### 灵感来源

本项目灵感来自 [OpenStego](https://github.com/syvaidya/openstego) 项目。我们感谢原始项目作者们的贡献和启发。

- **原始项目主页**: https://www.openstego.com
- **原始项目作者**:
  - Samir Vaidya ([@syvaidya](https://github.com/syvaidya)) (samir [at] openstego.com)
  - 张泽龙 ([@superzhangzl](https://github.com/superzhangzl))
- **原始项目许可证**: GNU 通用公共许可证 v2.0

**注意**: 本项目为独立实现，并非对原始项目的直接移植。

### 算法致谢

数字水印算法基于 Peter Meerwald 的优秀研究：
- Peter Meerwald, Digital Image Watermarking in the Wavelet Transfer Domain, Master's Thesis, Department of Scientific Computing, University of Salzburg, Austria, January 2001.
- 参考：http://www.cosy.sbg.ac.at/~pmeerw/Watermarking/

### 开源社区

感谢所有为开源软件做出贡献的开发者！

## 📧 联系方式

如有问题或建议，请通过 GitHub Issues 联系我们。

---

**注意**：本项目仅用于教育和合法目的。请勿用于任何非法活动。
