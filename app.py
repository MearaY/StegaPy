"""
StegaPy Streamlit应用

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

import streamlit as st
import io
from PIL import Image
from StegaPy import StegaPy, StegaPyConfig, __version__, __author__
from StegaPy.plugin_manager import PluginManager
from StegaPy.plugin.base import Purpose
from StegaPy.exceptions import StegaPyException

# 页面配置
st.set_page_config(
    page_title="StegaPy - 隐写术工具",
    page_icon="🔒",
    layout="wide"
)

# 初始化插件管理器
PluginManager.load_plugins()


def main():
    """主函数"""
    st.title("🔒 StegaPy - 隐写术工具")
    st.markdown("---")
    
    # 侧边栏
    with st.sidebar:
        st.header("功能选择")
        mode = st.radio(
            "选择功能模式",
            ["数据隐藏", "数字水印"],
            help="数据隐藏：将任意数据隐藏在图像中\n数字水印：在图像中嵌入不可见的水印签名"
        )
        
        st.markdown("---")
        st.header("算法选择")
        
        if mode == "数据隐藏":
            plugin_name = st.selectbox(
                "选择隐写算法",
                ["LSB", "RandomLSB"],
                help="LSB：最低有效位算法\nRandomLSB：随机LSB算法，提供更好的安全性"
            )
        else:
            plugin_name = st.selectbox(
                "选择水印算法",
                ["DWTDugad"],
                help="DWT Dugad：基于离散小波变换的水印算法"
            )
        
        st.markdown("---")
        st.header("配置选项")
        
        use_compression = st.checkbox("使用压缩", value=True, 
                                     help="使用GZIP压缩数据以减少嵌入数据大小")
        use_encryption = st.checkbox("使用加密", value=False,
                                    help="使用AES加密保护数据")
        
        password = None
        encryption_algorithm = "AES128"
        if use_encryption:
            password = st.text_input("密码", type="password",
                                    help="用于加密/解密的密码")
            encryption_algorithm = st.selectbox(
                "加密算法",
                ["AES128", "AES256"],
                help="AES128：128位AES加密\nAES256：256位AES加密"
            )
        
        # LSB特定配置
        if plugin_name in ["LSB", "RandomLSB"]:
            st.markdown("---")
            st.header("LSB参数")
            max_bits = st.slider("每通道最大位数", 1, 8, 1,
                               help="每个颜色通道使用的最大位数")
        else:
            max_bits = 1
        
        # 关于信息
        st.markdown("---")
        st.header("📖 关于")
        
        github_url = "https://github.com/MearaY/StegaPy"
        
        st.markdown(f"""
        **StegaPy** v{__version__}
        
        **作者**: [{__author__}](https://github.com/MearaY)
        
        **GitHub 仓库**: [{github_url}]({github_url})
        
        **许可证**: [GPL-2.0](https://github.com/MearaY/StegaPy/blob/main/LICENSE)
        
        ⚠️ **免责声明**: 本项目仅用于教育和合法目的，请勿用于任何非法活动。
        """)
    
    # 主内容区
    if mode == "数据隐藏":
        data_hiding_ui(plugin_name, use_compression, use_encryption, 
                      password, encryption_algorithm, max_bits)
    else:
        watermarking_ui(plugin_name, use_compression, use_encryption,
                       password, encryption_algorithm)


def data_hiding_ui(plugin_name, use_compression, use_encryption,
                  password, encryption_algorithm, max_bits):
    """数据隐藏界面"""
    st.header("📦 数据隐藏")
    
    tab1, tab2 = st.tabs(["嵌入数据", "提取数据"])
    
    with tab1:
        st.subheader("将数据嵌入到图像中")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**封面图像**")
            cover_file = st.file_uploader(
                "上传封面图像",
                type=['png', 'jpg', 'jpeg', 'bmp'],
                help="用于隐藏数据的封面图像"
            )
            
            if cover_file:
                # 重置文件指针并读取数据用于预览
                cover_file.seek(0)
                cover_image = Image.open(cover_file)
                st.image(cover_image, caption="封面图像", width='stretch')
                # 重置文件指针，确保后续读取时数据可用
                cover_file.seek(0)
        
        with col2:
            st.write("**消息文件**")
            msg_file = st.file_uploader(
                "上传要隐藏的消息文件",
                type=None,
                help="要隐藏在图像中的文件"
            )
            
            if msg_file:
                st.info(f"文件: {msg_file.name}\n大小: {len(msg_file.read())} 字节")
                msg_file.seek(0)  # 重置文件指针
        
        if st.button("嵌入数据", type="primary"):
            if not cover_file:
                st.error("请上传封面图像")
            elif not msg_file:
                st.error("请上传消息文件")
            else:
                try:
                    with st.spinner("正在嵌入数据..."):
                        # 获取插件
                        plugin = PluginManager.get_plugin_by_name(plugin_name)
                        if plugin_name in ["LSB", "RandomLSB"]:
                            from StegaPy.plugin.lsb.lsb_config import LSBConfig
                            config = LSBConfig(
                                max_bits_used_per_channel=max_bits,
                                use_compression=use_compression,
                                use_encryption=use_encryption,
                                password=password,
                                encryption_algorithm=encryption_algorithm
                            )
                            plugin.config = config
                        else:
                            config = StegaPyConfig(
                                use_compression=use_compression,
                                use_encryption=use_encryption,
                                password=password,
                                encryption_algorithm=encryption_algorithm
                            )
                        
                        # 读取数据（确保文件指针在开头）
                        cover_file.seek(0)
                        cover_data = cover_file.read()
                        msg_file.seek(0)
                        msg_data = msg_file.read()
                        
                        # 创建StegaPy实例
                        stegapy = StegaPy(plugin, config)
                        
                        # 嵌入数据
                        stego_data = stegapy.embed_data(
                            msg_data,
                            msg_file.name,
                            cover_data,
                            cover_file.name,
                            "stego.png"
                        )
                        
                        # 显示结果
                        stego_image = Image.open(io.BytesIO(stego_data))
                        st.success("数据嵌入成功！")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.image(cover_image, caption="原始图像", width='stretch')
                        with col2:
                            st.image(stego_image, caption="隐写图像", width='stretch')
                        
                        # 下载按钮
                        st.download_button(
                            label="下载隐写图像",
                            data=stego_data,
                            file_name="stego.png",
                            mime="image/png"
                        )
                        
                        # 显示差异（如果可能）
                        if st.checkbox("显示差异"):
                            try:
                                diff_data = stegapy.get_diff(
                                    stego_data, "stego.png",
                                    cover_data, cover_file.name,
                                    "diff.png"
                                )
                                diff_image = Image.open(io.BytesIO(diff_data))
                                st.image(diff_image, caption="差异图像（放大10倍）", width='stretch')
                            except Exception as e:
                                st.warning(f"无法生成差异图像: {str(e)}")
                
                except StegaPyException as e:
                    st.error(f"错误: {str(e)}")
                except Exception as e:
                    st.error(f"未知错误: {str(e)}")
    
    with tab2:
        st.subheader("从图像中提取数据")
        
        stego_file = st.file_uploader(
            "上传隐写图像",
            type=['png', 'jpg', 'jpeg', 'bmp'],
            help="包含隐藏数据的图像"
        )
        
        if stego_file:
            # 重置文件指针并读取数据用于预览
            stego_file.seek(0)
            stego_image = Image.open(stego_file)
            st.image(stego_image, caption="隐写图像", width='stretch')
            # 重置文件指针，确保后续读取时数据可用
            stego_file.seek(0)
        
        if st.button("提取数据", type="primary"):
            if not stego_file:
                st.error("请上传隐写图像")
            else:
                try:
                    with st.spinner("正在提取数据..."):
                        # 获取插件
                        plugin = PluginManager.get_plugin_by_name(plugin_name)
                        if plugin_name in ["LSB", "RandomLSB"]:
                            from StegaPy.plugin.lsb.lsb_config import LSBConfig
                            config = LSBConfig(
                                max_bits_used_per_channel=max_bits,
                                use_compression=use_compression,
                                use_encryption=use_encryption,
                                password=password,
                                encryption_algorithm=encryption_algorithm
                            )
                            plugin.config = config
                        else:
                            config = StegaPyConfig(
                                use_compression=use_compression,
                                use_encryption=use_encryption,
                                password=password,
                                encryption_algorithm=encryption_algorithm
                            )
                        
                        # 读取数据（确保文件指针在开头）
                        stego_file.seek(0)
                        stego_data = stego_file.read()
                        
                        # 创建StegaPy实例
                        stegapy = StegaPy(plugin, config)
                        
                        # 提取数据
                        result = stegapy.extract_data(stego_data, stego_file.name)
                        msg_filename, msg_data = result[0], result[1]
                        
                        st.success(f"数据提取成功！\n文件名: {msg_filename}")
                        
                        # 下载按钮
                        st.download_button(
                            label=f"下载提取的文件: {msg_filename}",
                            data=msg_data,
                            file_name=msg_filename,
                            mime="application/octet-stream"
                        )
                
                except StegaPyException as e:
                    st.error(f"错误: {str(e)}")
                except Exception as e:
                    st.error(f"未知错误: {str(e)}")


def watermarking_ui(plugin_name, use_compression, use_encryption,
                   password, encryption_algorithm):
    """数字水印界面"""
    st.header("💧 数字水印")
    
    tab1, tab2, tab3 = st.tabs(["生成签名", "嵌入水印", "验证水印"])
    
    with tab1:
        st.subheader("生成水印签名")
        st.info("水印签名基于密码生成，相同的密码会生成相同的签名")
        
        gen_password = st.text_input("输入密码（用于生成签名）", type="password")
        
        if st.button("生成签名", type="primary"):
            if not gen_password:
                st.error("请输入密码")
            else:
                try:
                    with st.spinner("正在生成签名..."):
                        plugin = PluginManager.get_plugin_by_name(plugin_name)
                        config = StegaPyConfig(password=gen_password)
                        plugin.config = config
                        
                        stegapy = StegaPy(plugin, config)
                        sig_data = stegapy.generate_signature()
                        
                        st.success("签名生成成功！")
                        st.download_button(
                            label="下载签名文件",
                            data=sig_data,
                            file_name="signature.dat",
                            mime="application/octet-stream"
                        )
                except Exception as e:
                    st.error(f"错误: {str(e)}")
    
    with tab2:
        st.subheader("嵌入水印到图像")
        
        col1, col2 = st.columns(2)
        
        with col1:
            cover_file = st.file_uploader(
                "上传封面图像",
                type=['png', 'jpg', 'jpeg', 'bmp']
            )
            if cover_file:
                # 重置文件指针并读取数据用于预览
                cover_file.seek(0)
                cover_image = Image.open(cover_file)
                st.image(cover_image, caption="封面图像", width='stretch')
                # 重置文件指针，确保后续读取时数据可用
                cover_file.seek(0)
        
        with col2:
            # 选择水印信息类型
            watermark_type = st.radio(
                "水印信息类型",
                ["签名文件 (.dat)", "文本文件 (.txt)"],
                help="选择上传签名文件或文本文件作为水印信息"
            )
            
            if watermark_type == "签名文件 (.dat)":
                sig_file = st.file_uploader(
                    "上传签名文件",
                    type=['dat'],
                    help="之前生成的签名文件"
                )
                
                if sig_file:
                    st.info(f"签名文件: {sig_file.name}\n大小: {len(sig_file.read())} 字节")
                    sig_file.seek(0)
                else:
                    sig_file = None
            else:
                txt_file = st.file_uploader(
                    "上传文本文件",
                    type=['txt', 'text'],
                    help="上传包含水印信息的文本文件（.txt格式）"
                )
                
                if txt_file:
                    # 读取文本内容预览
                    txt_content = txt_file.read()
                    txt_file.seek(0)
                    # 尝试解码为文本显示
                    try:
                        text_preview = txt_content.decode('utf-8')
                        if len(text_preview) > 200:
                            text_preview = text_preview[:200] + "..."
                        st.text_area("文本内容预览", text_preview, height=100, disabled=True)
                    except:
                        st.info(f"文本文件: {txt_file.name}\n大小: {len(txt_content)} 字节")
                else:
                    txt_file = None
                sig_file = None
        
        if st.button("嵌入水印", type="primary"):
            if not cover_file:
                st.error("请上传封面图像")
            elif watermark_type == "签名文件 (.dat)" and not sig_file:
                st.error("请上传签名文件")
            elif watermark_type == "文本文件 (.txt)" and not txt_file:
                st.error("请上传文本文件")
            else:
                try:
                    with st.spinner("正在嵌入水印..."):
                        plugin = PluginManager.get_plugin_by_name(plugin_name)
                        config = StegaPyConfig()
                        stegapy = StegaPy(plugin, config)
                        
                        # 读取数据（确保文件指针在开头）
                        cover_file.seek(0)
                        cover_data = cover_file.read()
                        
                        if watermark_type == "签名文件 (.dat)":
                            # 使用签名文件
                            sig_file.seek(0)
                            sig_data = sig_file.read()
                            stego_data = stegapy.embed_mark(
                                sig_data, sig_file.name,
                                cover_data, cover_file.name,
                                "watermarked.png"
                            )
                        else:
                            # 使用文本文件，直接使用embed_data方法（会自动从文本创建签名）
                            txt_file.seek(0)
                            txt_data = txt_file.read()
                            stego_data = stegapy.embed_data(
                                txt_data, txt_file.name,
                                cover_data, cover_file.name,
                                "watermarked.png"
                            )
                        
                        stego_image = Image.open(io.BytesIO(stego_data))
                        st.success("水印嵌入成功！")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.image(cover_image, caption="原始图像", width='stretch')
                        with col2:
                            st.image(stego_image, caption="水印图像", width='stretch')
                        
                        st.download_button(
                            label="下载水印图像",
                            data=stego_data,
                            file_name="watermarked.png",
                            mime="image/png"
                        )
                        
                        # 如果是文本文件，提示用户保存文本内容用于验证
                        if watermark_type == "文本文件 (.txt)":
                            st.info("💡 提示：请保存您的文本文件，验证水印时需要相同的文本文件。")
                except Exception as e:
                    st.error(f"错误: {str(e)}")
    
    with tab3:
        st.subheader("验证水印")
        
        col1, col2 = st.columns(2)
        
        with col1:
            stego_file = st.file_uploader(
                "上传水印图像",
                type=['png', 'jpg', 'jpeg', 'bmp']
            )
            if stego_file:
                # 重置文件指针并读取数据用于预览
                stego_file.seek(0)
                stego_image = Image.open(stego_file)
                st.image(stego_image, caption="水印图像", width='stretch')
                # 重置文件指针，确保后续读取时数据可用
                stego_file.seek(0)
        
        with col2:
            # 选择验证信息类型
            verify_type = st.radio(
                "验证信息类型",
                ["签名文件 (.dat)", "文本文件 (.txt)"],
                help="选择上传签名文件或文本文件用于验证"
            )
            
            if verify_type == "签名文件 (.dat)":
                orig_sig_file = st.file_uploader(
                    "上传原始签名文件",
                    type=['dat']
                )
                if orig_sig_file:
                    st.info(f"签名文件: {orig_sig_file.name}")
                else:
                    orig_sig_file = None
            else:
                orig_txt_file = st.file_uploader(
                    "上传原始文本文件",
                    type=['txt', 'text'],
                    help="上传用于嵌入水印的原始文本文件（必须与嵌入时使用的文件相同）"
                )
                if orig_txt_file:
                    # 读取文本内容预览
                    txt_content = orig_txt_file.read()
                    orig_txt_file.seek(0)
                    try:
                        text_preview = txt_content.decode('utf-8')
                        if len(text_preview) > 200:
                            text_preview = text_preview[:200] + "..."
                        st.text_area("文本内容预览", text_preview, height=100, disabled=True)
                    except:
                        st.info(f"文本文件: {orig_txt_file.name}\n大小: {len(txt_content)} 字节")
                else:
                    orig_txt_file = None
                orig_sig_file = None
        
        if st.button("验证水印", type="primary"):
            if not stego_file:
                st.error("请上传水印图像")
            elif verify_type == "签名文件 (.dat)" and not orig_sig_file:
                st.error("请上传原始签名文件")
            elif verify_type == "文本文件 (.txt)" and not orig_txt_file:
                st.error("请上传原始文本文件")
            else:
                try:
                    with st.spinner("正在验证水印..."):
                        plugin = PluginManager.get_plugin_by_name(plugin_name)
                        config = StegaPyConfig()
                        stegapy = StegaPy(plugin, config)
                        
                        # 读取数据（确保文件指针在开头）
                        stego_file.seek(0)
                        stego_data = stego_file.read()
                        
                        if verify_type == "签名文件 (.dat)":
                            # 使用签名文件
                            orig_sig_file.seek(0)
                            orig_sig_data = orig_sig_file.read()
                        else:
                            # 从文本文件创建签名
                            orig_txt_file.seek(0)
                            txt_data = orig_txt_file.read()
                            # 使用DWT插件的私有方法从文本创建签名
                            from StegaPy.plugin.dwtdugad.dwt_dugad_plugin import DWTDugadPlugin
                            if isinstance(plugin, DWTDugadPlugin):
                                sig_dict = plugin._create_signature_from_message(txt_data)
                                orig_sig_data = plugin._save_signature(sig_dict)
                            else:
                                raise Exception("当前插件不支持从文本文件创建签名")
                        
                        correlation = stegapy.check_mark(
                            stego_data, stego_file.name, orig_sig_data
                        )
                        
                        high_level = plugin.get_high_watermark_level()
                        low_level = plugin.get_low_watermark_level()
                        
                        st.success(f"水印相关性: {correlation:.4f}")
                        
                        # 显示相关性指标
                        # 改进判断逻辑：相关性 > 0 表示检测到水印，只是强度不同
                        if correlation >= high_level:
                            st.success(f"✅ 水印强度高（阈值: {high_level:.2f}）")
                        elif correlation >= low_level:
                            st.warning(f"⚠️ 水印强度中等（阈值: {low_level:.2f}）")
                        elif correlation > 0.1:
                            # 相关性在0.1到低阈值之间，表示检测到水印但强度较低
                            st.info(f"ℹ️ 检测到水印，但强度较低（相关性: {correlation:.4f}，建议阈值: {low_level:.2f}）")
                        else:
                            st.error(f"❌ 未检测到有效水印（相关性: {correlation:.4f}，阈值: {low_level:.2f}）")
                        
                        # 如果相关性很低，显示调试信息
                        if correlation < 0.5 and hasattr(plugin, '_last_correlation_debug'):
                            debug_info = plugin._last_correlation_debug
                            with st.expander("🔍 调试信息（相关性较低）", expanded=True):
                                st.write(f"**统计信息:**")
                                st.write(f"- 匹配的子带数: {debug_info['ok']} / {debug_info['n']}")
                                st.write(f"- Alpha值: {debug_info['alpha']:.6f}")
                                st.write(f"- 相关性: {debug_info['correlation']:.4f}")
                                
                                if debug_info['debug_info']:
                                    st.write(f"**前5个子带的详细信息:**")
                                    for info in debug_info['debug_info'][:5]:
                                        subband, level, m, z, v, alpha, threshold, is_match = info
                                        match_icon = "✅" if is_match else "❌"
                                        st.write(f"{match_icon} {subband} level={level}: m={m}, z={z:.4f}, v={v:.4f}, threshold={threshold:.4f}, match={is_match}")
                                    
                                    if len(debug_info['debug_info']) > 5:
                                        st.write(f"... 还有 {len(debug_info['debug_info']) - 5} 个子带未显示")
                        
                        # 可视化相关性
                        try:
                            import plotly.graph_objects as go
                            fig = go.Figure(go.Indicator(
                            mode="gauge+number",
                            value=correlation,
                            domain={'x': [0, 1], 'y': [0, 1]},
                            title={'text': "水印相关性"},
                            gauge={
                                'axis': {'range': [None, 1]},
                                'bar': {'color': "darkblue"},
                                'steps': [
                                    {'range': [0, low_level], 'color': "lightgray"},
                                    {'range': [low_level, high_level], 'color': "gray"}
                                ],
                                'threshold': {
                                    'line': {'color': "red", 'width': 4},
                                    'thickness': 0.75,
                                    'value': high_level
                                }
                            }
                        ))
                            st.plotly_chart(fig, width='stretch')
                        except ImportError:
                            st.info("安装plotly以查看相关性图表: pip install plotly")
                
                except Exception as e:
                    st.error(f"错误: {str(e)}")


if __name__ == "__main__":
    main()

