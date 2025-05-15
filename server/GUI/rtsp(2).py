# -*- coding: UTF-8 -*-
'''
@Project :fd_project 
@Author  :风吹落叶
@Contack :Waitkey1@outlook.com
@Version :V1.0
@Date    :2025/04/25 1:00 
@Describe:
'''
# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""
基于ffmpeg的视频推流服务器
支持从视频文件或摄像头读取并推送到RTSP或HTTP流
"""

import os
import sys
import time
import signal
import argparse
import subprocess
import threading
import logging
import socket
from typing import Optional, List, Dict, Union, Tuple

# 设置日志格式
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('视频推流')


class StreamServer:
    """基于ffmpeg的视频推流服务器"""

    def __init__(self,
                 input_path: str,
                 output_url: str,
                 output_type: str = 'rtsp',
                 input_options: Optional[Dict[str, str]] = None,
                 output_options: Optional[Dict[str, str]] = None,
                 log_level: str = 'info'):
        """
        初始化视频推流服务器

        参数:
            input_path: 输入视频路径或摄像头索引
            output_url: 推流地址 (RTSP或HTTP URL)
            output_type: 输出类型 ('rtsp', 'http', 'udp')
            input_options: ffmpeg输入选项
            output_options: ffmpeg输出选项
            log_level: 日志级别
        """
        self.input_path = input_path
        self.output_url = output_url
        self.output_type = output_type.lower()
        self.input_options = input_options or {}
        self.output_options = output_options or {}
        self.log_level = log_level
        self.process = None
        self.is_running = False
        self.thread = None
        self.http_server = None

        # 检测ffmpeg是否已安装
        try:
            subprocess.run(
                ['ffmpeg', '-version'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )
        except (subprocess.SubprocessError, FileNotFoundError):
            logger.error("未找到ffmpeg，请先安装ffmpeg并确保其在系统PATH中")
            raise RuntimeError("未找到ffmpeg，推流服务无法启动")

        # 如果使用HTTP输出且URL以localhost或127.0.0.1开头，检查端口是否可用
        if self.output_type == 'http' and ('localhost' in self.output_url or '127.0.0.1' in self.output_url):
            self._check_port_available()

    def _check_port_available(self):
        """检查HTTP服务端口是否可用"""
        try:
            # 从URL中提取端口
            port_start = self.output_url.rfind(':')
            port_end = self.output_url.find('/', port_start)
            if port_end == -1:
                port_end = len(self.output_url)

            port = int(self.output_url[port_start + 1:port_end])

            # 测试端口是否被占用
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('127.0.0.1', port))
            sock.close()

            if result == 0:
                logger.warning(f"端口 {port} 已被占用，请确保该端口没有其他服务在使用")
        except Exception as e:
            logger.warning(f"检查端口时出错: {str(e)}")

    def _build_command(self) -> List[str]:
        """构建ffmpeg命令"""
        command = ['ffmpeg']

        # 添加通用选项
        command.extend(['-y', '-loglevel', self.log_level])

        # 判断输入源类型
        if self.input_path.isdigit():
            # 使用摄像头
            device_index = int(self.input_path)
            if sys.platform == 'win32':
                # Windows平台
                command.extend(['-f', 'dshow', '-i', f'video={device_index}'])
            elif sys.platform == 'darwin':
                # macOS平台
                command.extend(['-f', 'avfoundation', '-i', f'{device_index}'])
            else:
                # Linux平台
                command.extend(['-f', 'v4l2', '-i', f'/dev/video{device_index}'])
        elif self.input_path.startswith(('rtsp://', 'http://', 'https://')):
            # 网络流
            command.extend(['-i', self.input_path])
        else:
            # 本地文件
            if not os.path.exists(self.input_path):
                raise FileNotFoundError(f"输入文件不存在: {self.input_path}")

            # 文件是否支持循环播放
            if self.input_options.get('loop', 'false').lower() == 'true':
                command.extend(['-stream_loop', '-1'])

            command.extend(['-i', self.input_path])

        # 添加输入选项
        for key, value in self.input_options.items():
            if key != 'loop':  # 循环已经处理
                command.extend([f'-{key}', value])

        # 添加视频编码选项
        command.extend([
            '-c:v', self.output_options.get('vcodec', 'libx265'),
            '-preset', self.output_options.get('preset', 'medium'),
            '-tune', self.output_options.get('tune', 'zerolatency')
        ])

        # 添加音频编码选项
        command.extend([
            '-c:a', self.output_options.get('acodec', 'aac'),
            '-strict', 'experimental'
        ])

        # 添加H.265特定参数
        if self.output_options.get('vcodec', 'libx265') == 'libx265':
            command.extend([
                '-x265-params', f"crf={self.output_options.get('crf', '23')}:qp-adaptation-range=1.0"
            ])

        # 设置比特率
        if 'bitrate' in self.output_options:
            command.extend(['-b:v', self.output_options['bitrate']])

        # 设置分辨率
        if 'resolution' in self.output_options:
            command.extend(['-s', self.output_options['resolution']])

        # 设置帧率
        if 'framerate' in self.output_options:
            command.extend(['-r', self.output_options['framerate']])

        # 添加输出选项
        for key, value in self.output_options.items():
            if key not in ('vcodec', 'preset', 'tune', 'bitrate', 'resolution', 'framerate', 'crf'):
                command.extend([f'-{key}', value])

        # 基于输出类型设置不同的输出参数
        if self.output_type == 'rtsp':
            # RTSP输出
            command.extend([
                '-f', 'rtsp',
                '-rtsp_transport', 'tcp',
                '-muxdelay', '0.1',
                '-g', '50',  # GOP大小，增加关键帧频率
                self.output_url
            ])
        elif self.output_type == 'udp':
            # UDP输出
            command.extend([
                '-f', 'mpegts',
                '-muxdelay', '0',
                self.output_url
            ])
        elif self.output_type == 'http':
            # HTTP输出
            command.extend([
                '-f', 'mpegts',
                '-movflags', 'frag_keyframe+empty_moov',
                self.output_url
            ])
        else:
            # 默认使用RTSP
            command.extend([
                '-f', 'rtsp',
                '-rtsp_transport', 'tcp',
                self.output_url
            ])

        return command

    def start(self, block: bool = False):
        """
        启动视频推流

        参数:
            block: 是否阻塞等待完成
        """
        if self.is_running:
            logger.warning("推流服务已在运行中")
            return

        try:
            command = self._build_command()
            logger.info(f"启动视频推流: {' '.join(command)}")

            # 创建进程
            self.process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )

            self.is_running = True

            if block:
                # 阻塞模式，直接等待完成
                self._monitor_process()
            else:
                # 非阻塞模式，创建监控线程
                self.thread = threading.Thread(target=self._monitor_process)
                self.thread.daemon = True
                self.thread.start()

            logger.info(f"视频推流服务已启动: {self.output_url}")
        except Exception as e:
            logger.error(f"启动视频推流服务失败: {str(e)}")
            self.stop()
            raise

    def _monitor_process(self):
        """监控ffmpeg进程"""
        try:
            # 读取进程输出
            for line in self.process.stderr:
                if line.strip():
                    logger.debug(f"ffmpeg: {line.strip()}")

            # 等待进程结束
            retcode = self.process.wait()
            self.is_running = False

            if retcode != 0 and retcode != -9:  # -9是SIGKILL信号，通常是我们主动终止
                logger.error(f"ffmpeg进程异常退出，返回码: {retcode}")
            else:
                logger.info("ffmpeg进程已正常退出")
        except Exception as e:
            logger.error(f"监控ffmpeg进程时出错: {str(e)}")
            self.is_running = False

    def stop(self):
        """停止视频推流"""
        if not self.is_running:
            logger.warning("推流服务不在运行中")
            return

        if self.process:
            logger.info("正在停止视频推流服务...")

            # 尝试正常终止
            if sys.platform == 'win32':
                self.process.terminate()
            else:
                self.process.send_signal(signal.SIGTERM)

            # 等待一段时间
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                # 超时，强制终止
                logger.warning("ffmpeg进程未能正常退出，强制终止")
                self.process.kill()

            self.process = None

        self.is_running = False
        logger.info("视频推流服务已停止")

    def restart(self):
        """重启视频推流"""
        logger.info("正在重启视频推流服务...")
        self.stop()
        time.sleep(1)  # 短暂延时确保资源释放
        self.start()

    def __enter__(self):
        """支持上下文管理器"""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文时关闭推流"""
        self.stop()


class HttpServer:
    """简易HTTP服务器，用于提供HTTP视频流访问"""

    def __init__(self, port: int = 8080, directory: str = None):
        """
        初始化HTTP服务器

        参数:
            port: 服务器端口
            directory: 提供文件的目录，None为当前目录
        """
        self.port = port
        self.directory = directory
        self.server = None
        self.thread = None
        self.is_running = False

    def start(self):
        """启动HTTP服务器"""
        if self.is_running:
            logger.warning("HTTP服务器已在运行中")
            return

        try:
            import http.server
            import socketserver

            handler = http.server.SimpleHTTPRequestHandler
            if self.directory:
                os.chdir(self.directory)

            self.server = socketserver.TCPServer(("", self.port), handler)
            self.is_running = True

            # 在新线程中启动服务器
            self.thread = threading.Thread(target=self.server.serve_forever)
            self.thread.daemon = True
            self.thread.start()

            logger.info(f"HTTP服务器已启动于端口 {self.port}")
        except Exception as e:
            logger.error(f"启动HTTP服务器失败: {str(e)}")
            self.is_running = False
            raise

    def stop(self):
        """停止HTTP服务器"""
        if not self.is_running:
            return

        if self.server:
            self.server.shutdown()
            self.server = None

        self.is_running = False
        logger.info("HTTP服务器已停止")


class VideoProcessor:
    """视频处理器，支持从本地文件或摄像头读取并进行处理"""

    def __init__(self, input_path: str, processor=None):
        """
        初始化视频处理器

        参数:
            input_path: 输入视频路径或摄像头索引
            processor: 处理回调函数，接收帧和时间戳参数
        """
        self.input_path = input_path
        self.processor = processor
        self.cap = None
        self.is_running = False
        self.thread = None

    def start(self, block: bool = False):
        """
        启动视频处理

        参数:
            block: 是否阻塞等待完成
        """
        if self.is_running:
            logger.warning("视频处理器已在运行中")
            return

        try:
            import cv2

            # 打开视频源
            if self.input_path.isdigit():
                self.cap = cv2.VideoCapture(int(self.input_path))
            else:
                self.cap = cv2.VideoCapture(self.input_path)

            if not self.cap.isOpened():
                raise RuntimeError(f"无法打开视频源: {self.input_path}")

            self.is_running = True

            if block:
                # 阻塞模式直接处理
                self._process_frames()
            else:
                # 非阻塞模式创建线程
                self.thread = threading.Thread(target=self._process_frames)
                self.thread.daemon = True
                self.thread.start()
        except Exception as e:
            logger.error(f"启动视频处理器失败: {str(e)}")
            self.is_running = False
            raise

    def _process_frames(self):
        """处理视频帧"""
        import cv2

        try:
            frame_count = 0
            start_time = time.time()

            while self.is_running:
                ret, frame = self.cap.read()

                if not ret:
                    # 视频文件结束或读取错误
                    if isinstance(self.input_path, str) and not self.input_path.isdigit():
                        # 如果是视频文件，尝试循环播放
                        self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                        continue
                    break

                frame_count += 1
                current_time = time.time()
                elapsed = current_time - start_time

                # 调用处理函数
                if self.processor:
                    self.processor(frame, elapsed)

                # 计算FPS
                if frame_count % 30 == 0:
                    fps = frame_count / elapsed
                    logger.debug(f"处理FPS: {fps:.2f}")

                # 显示进度
                if frame_count % 100 == 0:
                    logger.debug(f"已处理 {frame_count} 帧")

                # 避免CPU占用过高
                time.sleep(0.001)
        except Exception as e:
            logger.error(f"处理视频帧时出错: {str(e)}")
        finally:
            if self.cap:
                self.cap.release()
            self.is_running = False

    def stop(self):
        """停止视频处理"""
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=5)
        if self.cap:
            self.cap.release()
            self.cap = None


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='基于ffmpeg的视频推流服务器')

    parser.add_argument('--input', '-i', required=True,
                        help='输入源，可以是视频文件路径、摄像头索引或RTSP/HTTP流地址')
    parser.add_argument('--output', '-o', required=True,
                        help='输出地址，例如: rtsp://localhost:8554/stream 或 http://localhost:8080/stream.ts')
    parser.add_argument('--type', '-t', default='auto',
                        choices=['auto', 'rtsp', 'http', 'udp'],
                        help='输出流类型, auto将根据URL自动选择')
    parser.add_argument('--resolution', '-s', default=None,
                        help='输出分辨率，例如: 1280x720')
    parser.add_argument('--framerate', '-r', default='25',
                        help='输出帧率')
    parser.add_argument('--bitrate', '-b', default='2M',
                        help='输出比特率，例如: 2M')
    parser.add_argument('--vcodec', '-c', default='libx265',
                        help='视频编码器，例如: libx264, libx265')
    parser.add_argument('--acodec', '-a', default='aac',
                        help='音频编码器，默认: aac')
    parser.add_argument('--preset', '-p', default='medium',
                        choices=['ultrafast', 'superfast', 'veryfast', 'faster', 'fast', 'medium', 'slow', 'slower',
                                 'veryslow'],
                        help='编码器预设')
    parser.add_argument('--crf', default='23',
                        help='视频质量控制参数(对于H.265，推荐值为18-28，数值越小质量越高)')
    parser.add_argument('--loop', action='store_true',
                        help='循环播放输入视频文件')
    parser.add_argument('--log_level', '-l', default='info',
                        choices=['quiet', 'panic', 'fatal', 'error', 'warning', 'info', 'verbose', 'debug'],
                        help='日志级别')

    return parser.parse_args()


def main():
    """主函数"""
    args = parse_args()

    # 自动确定输出类型
    output_type = args.type
    if output_type == 'auto':
        if args.output.startswith('rtsp://'):
            output_type = 'rtsp'
        elif args.output.startswith('udp://'):
            output_type = 'udp'
        elif args.output.startswith(('http://', 'https://')):
            output_type = 'http'
        else:
            # 默认使用HTTP
            output_type = 'http'

    # 输入选项
    input_options = {}
    if args.loop:
        input_options['loop'] = 'true'

    # 输出选项
    output_options = {
        'vcodec': args.vcodec,
        'acodec': args.acodec,
        'preset': args.preset,
        'framerate': args.framerate,
        'bitrate': args.bitrate,
        'crf': args.crf
    }

    if args.resolution:
        output_options['resolution'] = args.resolution

    # 如果是使用HTTP输出到本地，并且用户没有指定输出格式，确保使用mpegts格式
    if output_type == 'http' and ('localhost' in args.output or '127.0.0.1' in args.output):
        if not args.output.endswith('.ts'):
            logger.warning("建议HTTP输出URL以.ts结尾以确保兼容性")

    # 创建并启动推流服务器
    server = StreamServer(
        input_path=args.input,
        output_url=args.output,
        output_type=output_type,
        input_options=input_options,
        output_options=output_options,
        log_level=args.log_level
    )

    try:
        output_type_str = '视频'
        if output_type == 'rtsp':
            output_type_str = 'RTSP'
        elif output_type == 'http':
            output_type_str = 'HTTP'
        elif output_type == 'udp':
            output_type_str = 'UDP'

        print(f"启动{output_type_str}推流服务，将 {args.input} 推送到 {args.output}")
        print("按 Ctrl+C 停止推流...")

        # 阻塞模式启动
        server.start(block=True)
    except KeyboardInterrupt:
        print("\n用户中断，停止推流...")
    except Exception as e:
        print(f"推流过程中出错: {str(e)}")
    finally:
        server.stop()
        print("推流服务已停止")


if __name__ == "__main__":
    main()
