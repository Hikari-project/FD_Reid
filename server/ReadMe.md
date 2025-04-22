# 一、环境配置
## Install & Run 
- step1: conda create -n reid_gui python=3.10
- step2: conda activate reid_gui
- step3: If mac or linux OS: sh install.sh; 
         or win OS:  ./install.bat
- step4: cd GUI; python main_detect.py


## UI modified by Users
- using qt designer
- pyside6-uic home.ui > home.py

## support GPU
> 我们支持GPU去加速推理,目前只支持N卡。需要大家自己配置好cuda/cudnn,然后安装时执行install_gpu.sh or install_gpu.bat
> 

# 二、数据下载
## 模型数据
下载地址：https://drive.google.com/file/d/1xV04nQqmwbalaPUxep2M9a7PrLOZ1BUD/view?usp=drive_link
下载内容放到GUI/models中
![img.png](img.png)
## 测试视频
下载地址：https://drive.google.com/file/d/1H-zftcOXm-oWNvNm_zPJlCnF5Gb2-ceY/view?usp=drive_link
下载内容放到：data中
![img_1.png](img_1.png)