# -*- coding: UTF-8 -*-
'''
@Project :AIProject
@Author  :self-798
@Contack :123090233@link.cuhk.edu.cn
@Version :V1.0
@Date    :2025/3/11 1:31
@Describe:
'''

class area_boundary_detect():
    def __init__(self, b1, b2, b3):
        """初始化三条边界线的方程系数"""
        self.b1 = b1  # 进出店识别线
        self.b2 = b2  # 过店识别线1
        self.b3 = b3  # 过店识别线2
        
        # 计算三条线的一般式方程系数 Ax + By + C = 0
        self.A1 = b1[3] - b1[1]
        self.B1 = b1[0] - b1[2]
        self.C1 = b1[2]*b1[1] - b1[0]*b1[3]
        
        self.A2 = b2[3] - b2[1]
        self.B2 = b2[0] - b2[2]
        self.C2 = b2[2]*b2[1] - b2[0]*b2[3]
        
        self.A3 = b3[3] - b3[1]
        self.B3 = b3[0] - b3[2]
        self.C3 = b3[2]*b3[1] - b3[0]*b3[3]
        
        # 计算参考点(过店识别线中点)用于确定符号方向
        self.ref_x2 = (b2[0] + b2[2])/2
        self.ref_y2 = (b2[1] + b2[3])/2
        self.ref_x3 = (b3[0] + b3[2])/2
        self.ref_y3 = (b3[1] + b3[3])/2
        
        # 确定方向符号
        self.sign1 = 1 if self.A1*self.ref_x2 + self.B1*self.ref_y2 + self.C1 > 0 else -1
        
    def area_boundary(self, x, y):
        """判断点(x,y)是否在店内"""
        # 判断点到进出店识别线的位置关系
        d1 = self.A1*x + self.B1*y + self.C1
        d2 = self.A2*x + self.B2*y + self.C2
        d3 = self.A3*x + self.B3*y + self.C3
        return (d1 * self.sign1) < 0 
        
    def pass_boundary(self, x, y):
        """判断点(x,y)是否在过店范围内"""
        # 判断点到两条过店识别线的位置关系
        d2 = self.A2*x + self.B2*y + self.C2
        d3 = self.A3*x + self.B3*y + self.C3
        
        # 点必须在两条过店识别线之间
        return (d2 * d3) < 0
    
    def get_location_type(self, x, y):
        """
        包装函数: 判断点的位置类型
        :param x,y: 坐标点
        :return: 'inside'/'outside'/'pass_area'
        """
        is_inside = self.area_boundary(x, y)
        is_pass = self.pass_boundary(x, y)
        
        if is_inside:
            return 'inside'
        elif is_pass:
            return 'pass_area' 
        return 'outside'
    