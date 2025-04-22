import numpy as np
import cv2
from rknn.api import RKNN
import os
 
 
ONNX_MODEL = 'reid_person_0.737.onnx'
RKNN_MODEL = 'reid_person_0.737.rknn'
IMG_PATH = './bus.jpg'
DATASET = 'jpg_list.txt'
 
 
 
if __name__ == '__main__':
 
    # Create RKNN object
    rknn = RKNN(verbose=True)
 
    if not os.path.exists(ONNX_MODEL):
        print('model not exist')
        exit(-1)
    
    # pre-process config
    print('--> Config model')
    rknn.config(mean_values=[[0, 0, 0]],std_values=[[255, 255, 255]],optimization_level=3,target_platform = 'rk3588')
    print('done')
 
    # Load ONNX model
    print('--> Loading model')
    ret = rknn.load_onnx(model=ONNX_MODEL)  # need to check if it hits
    if ret != 0:
        print('Load failed!')
        exit(ret)
    print('done')
 
    # Build model
    print('--> Building model')
    ret = rknn.build(do_quantization=True, dataset=DATASET)
    if ret != 0:
        print('Build failed!')
        exit(ret)
    print('done')
 
    # Export RKNN model
    print('--> Export RKNN model')
    ret = rknn.export_rknn(RKNN_MODEL)
    if ret != 0:
        print('Export rknn failed!')
        exit(ret)
    print('done')