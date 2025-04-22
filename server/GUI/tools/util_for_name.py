# data\glry_test\dir_test\0000_c1_0002.jpg

# 遍历GUI\models\data\glry_test\dir_test下.jpg文件，将所有.jpg文件的名称保存为一个txt文件，每个.jpg文件名占一行

import os

path = 'data/glry_test/dir_test'
file_list = os.listdir(r"GUI\models\data\glry_test\dir_test")
jpg_list = [file for file in file_list if file.endswith('.jpg')]

with open('jpg_list.txt', 'w') as f:
    for jpg in jpg_list:
        f.write(path + '/' + jpg + '\n')