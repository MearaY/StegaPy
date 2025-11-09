# StegaPy

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-GPLv2-green.svg)](LICENSE)
[![Code Lines](https://img.shields.io/badge/code%20lines-2500%2B-orange.svg)]()

**Language**: [中文](README.md) | English

**StegaPy** is a Python-based information hiding (steganography) tool inspired by [OpenStego](https://github.com/syvaidya/openstego). It is a powerful steganography tool for hiding data and embedding digital watermarks in image files.

## 📋 About

This project is a Python-based steganography tool inspired by the OpenStego project. It is developed in Python and implements core functionality while introducing some improvements and extensions. Please note that this is a work in progress and may have limitations or incomplete features. Ongoing maintenance and improvements are planned.

- 🔄 **Feature Implementation**: Major steganography and watermarking algorithms
- 🌐 **Modern Web Interface**: Interactive web application built with Streamlit for easier use
- 📝 **Code Quality**: PEP 8 compliant with type hints and documentation
- 🏗️ **Modular Design**: Plugin-based architecture for better maintainability
- 💻 **Cross-Platform Support**: Native Python cross-platform support for easier deployment
- 📦 **Python Ecosystem**: Utilizes libraries like NumPy and Pillow for enhanced performance

**Note**: This is an experimental project. Some features may not be fully implemented or tested. Feedback is welcome.


## 🚀 Quick Start

### Environment Setup

#### Using Conda (Recommended)

```bash
# Create conda environment
conda env create -f environment.yml

# Activate environment
conda activate StegaPy
```

#### Using pip

```bash
# Install dependencies
pip install -r requirements.txt

# Install package (development mode)
pip install -e .
```

### Web Interface

Start the Streamlit web application:

```bash
# Use default port (usually 8501)
streamlit run app.py

# Or specify a custom port (recommended to use an available port, e.g., 8501)
streamlit run app.py --server.port 8501
```

The web interface provides complete functionality, including:
- Data hiding (embed/extract)
- Digital watermarking (generate/embed/verify)
- Image difference visualization
- Real-time processing feedback


## 📁 Project Structure

```
StegaPy/
├── StegaPy/            # Main package
│   ├── plugin/         # Plugin modules (LSB, RandomLSB, DWT, etc.)
│   └── util/           # Utility modules
├── app.py              # Streamlit application
├── data/               # Data directory
├── requirements.txt    # pip dependencies
└── README.md          # Documentation
```

## 📄 License

This project is licensed under the **GNU General Public License v2.0 (GPL-2.0)**.

**For the complete license text, see**: [LICENSE](LICENSE)

## 🙏 Acknowledgments

### Inspiration

This project is inspired by the [OpenStego](https://github.com/syvaidya/openstego) project. We thank the original project authors for their contributions and inspiration.

- **Original Project Homepage**: https://www.openstego.com
- **Original Project Authors**:
  - Samir Vaidya ([@syvaidya](https://github.com/syvaidya)) (samir [at] openstego.com)
  - Zelong Zhang ([@superzhangzl](https://github.com/superzhangzl))
- **Original Project License**: GNU General Public License v2.0

**Note**: This project is an independent implementation, not a direct port of the original project.

### Algorithm Acknowledgments

The digital watermarking algorithm is based on excellent research by Peter Meerwald:
- Peter Meerwald, Digital Image Watermarking in the Wavelet Transfer Domain, Master's Thesis, Department of Scientific Computing, University of Salzburg, Austria, January 2001.
- Reference: http://www.cosy.sbg.ac.at/~pmeerw/Watermarking/

### Open Source Community

Thanks to all developers who contribute to open source software!

## 📧 Contact

For questions or suggestions, please contact us via GitHub Issues.

---

**Note**: This project is intended for educational and legal purposes only. Do not use for any illegal activities.

