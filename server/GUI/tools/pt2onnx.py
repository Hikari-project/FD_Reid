import torch
import torch.onnx
from ultralytics import YOLO
import os

def convert_to_onnx(model_path, onnx_path):
    # 加载配置
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    # 加载YOLO模型
    model = YOLO(model_path)
    
    # 导出ONNX模型
    model.export(format='onnx', 
                imgsz=[640, 640],  # YOLO标准输入尺寸
                opset=12,          # ONNX操作集版本
                simplify=True,     # 简化模型
                dynamic=True,      # 动态批处理大小
                half=False)        # FP16精度
    
    print(f"YOLO模型已成功转换为ONNX格式并保存到: {onnx_path}")

if __name__ == "__main__":
    model_path = "../models/yolo12s.pt"  # YOLO模型路径
    onnx_path = "yolo12s.onnx"    # 输出ONNX模型路径
    convert_to_onnx(model_path, onnx_path)
