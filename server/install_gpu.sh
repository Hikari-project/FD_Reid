#!/usr/bin/env bash
init(){
    if [[ `python -V` =~ "Python 3.8" ]] ;then
        echo "python version: " `python -V`
    else
        echo "python version need >=3.8"
        exit -2
    fi
    pip install -r ./requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
    pip install onnxruntime-gpu -i https://pypi.tuna.tsinghua.edu.cn/simple
    pip install --no-cache "onnx" "onnxruntime"  --user -i https://pypi.tuna.tsinghua.edu.cn/simple
}

init