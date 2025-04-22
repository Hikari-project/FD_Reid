@echo off

call :init
goto :eof

:init
for /f "tokens=*" %%i in ('python -V 2^>^&1') do set PYTHON_VERSION=%%i
echo %PYTHON_VERSION% | find "Python 3.8" > nul
if errorlevel 1 (
    echo python version need >=3.8
    exit /b -2
) else (
    echo %PYTHON_VERSION%
)

pip install -r ./requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
rem pip install torch==1.11.0+cpu torchvision==0.12.0+cpu torchaudio==0.11.0+cpu --extra-index-url https://download.pytorch.org/whl/cpu
pip install onnxruntime -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install --no-cache "onnx" "onnxruntime"  --user -i https://pypi.tuna.tsinghua.edu.cn/simple
goto :eof