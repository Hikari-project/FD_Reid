# -*- coding: UTF-8 -*-
'''
@Project :fd_project 
@Author  :风吹落叶
@Contack :Waitkey1@outlook.com
@Version :V1.0
@Date    :2025/04/25 13:31 
@Describe:
'''

import sys
import subprocess
import time


def rtsp_out(video_list):
    processes = []
    for i, video_path in enumerate(video_list):
        command = [
            sys.executable,  # 使用当前Python解释器
            "rtsp.py",  # 脚本名称（确保路径正确）
            "-i",
            video_path,
            "-o",
            f"rtsp://192.168.21.161:8554/test_{i + 1}",
            "--loop"
        ]

        try:
            # 异步启动子进程，不等待完成
            process = subprocess.Popen(
                command,
                stdout=sys.stdout,  # 实时输出到控制台
                stderr=subprocess.STDOUT  # 合并错误输出到标准输出
            )
            processes.append(process)
        except Exception as e:
            print(f"启动进程失败：{str(e)}")

    # 可选：返回进程列表以便后续管理
    return processes


if __name__ == '__main__':
    video_list = [
        # r"H:\fd_project\FD_REID_Project\data\test1.mp4",
        # r"H:\fd_project\FD_REID_Project\data\test2.mp4",

        r"H:\fd_project\FD_REID_Project\data\FD_video_1216\901_20241216_174435.mkv",
         r"H:\fd_project\FD_REID_Project\data\FD_video_1216\801_20241216_174432.mkv",
    ]

    # 启动所有推流任务
    processes = rtsp_out(video_list)

    # 主进程可继续执行其他操作或进入等待状态
    # 示例：保持主进程运行（按Ctrl+C退出）
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n主进程退出")