#!/usr/bin/env bash
init(){
    # 获取Python版本号（去掉"Python "前缀）
    python_version=$(python -V 2>&1 | sed 's/Python //' | cut -d. -f1,2)
    required_version="3.8"
    
    # 版本比较
    if printf '%s\n' "$required_version" "$python_version" | sort -V -C; then
        echo "Python version: $python_version (符合要求)"
    else
        echo "Python version need >= 3.8"
        exit -2
    fi
    
    # 设置PYTHONPATH
    project_path=$(pwd)
    echo "export PYTHONPATH=$PYTHONPATH:$project_path" >> ~/.bashrc
    export PYTHONPATH=$PYTHONPATH:$project_path
    
    # 安装依赖
    pip install -r ./requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
    pip install onnxruntime -i https://pypi.tuna.tsinghua.edu.cn/simple
    pip install --no-cache "onnx" "onnxruntime"  --user -i https://pypi.tuna.tsinghua.edu.cn/simple
    
    echo "Installation completed!"
}

init