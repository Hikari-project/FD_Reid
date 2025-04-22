import cv2
import numpy as np
import mediapipe as mp
from dataclasses import dataclass
from typing import List, Tuple, Dict
from pathlib import Path

@dataclass
class CompletenessScore:
    visible_keypoints: int
    total_keypoints: int
    visibility_score: float
    pose_score: float
    total_score: float
    status: str

class BodyCompletenessDetector:
    def __init__(self, use_gpu: bool = True):
        self.mp_pose = mp.solutions.pose
        self.mp_draw = mp.solutions.drawing_utils
        self.pose = self.mp_pose.Pose(
            static_image_mode=True,
            model_complexity=1,
            enable_segmentation=True,
            min_detection_confidence=0.5
        )
        
        # 关键点权重
        self.keypoint_weights = {
            'head': 0.3,      # 头部
            'torso': 0.35,     # 躯干
            'arms': 0.20,     # 手臂
            'legs': 0.20      # 腿部
        }
        
        # 关键点分组
        self.keypoint_groups = {
            'head': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            'torso': [11, 12, 23, 24],
            'arms': [13, 14, 15, 16, 17, 18, 19, 20],
            'legs': [25, 26, 27, 28, 29, 30, 31, 32]
        }
        
    def detect(self, image: np.ndarray) -> CompletenessScore:
        """检测人体完整度"""
        results = self.pose.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        
        if not results.pose_landmarks:
            return CompletenessScore(0, 33, 0.0, 0.0, 0.0, "未检测到人体")
            
        # 计算可见关键点
        visible_points = sum(1 for landmark in results.pose_landmarks.landmark 
                           if landmark.visibility > 0.5)
                           
        # 计算姿态分数
        pose_score = self._calculate_pose_score(results.pose_landmarks.landmark)
        
        # 计算总分
        visibility_score = visible_points / 33.0
        total_score = 0.6 * visibility_score + 0.4 * pose_score
        
        # 确定状态
        status = self._determine_status(total_score)
        
        return CompletenessScore(
            visible_keypoints=visible_points,
            total_keypoints=33,
            visibility_score=visibility_score,
            pose_score=pose_score,
            total_score=total_score,
            status=status
        )

    def _calculate_pose_score(self, landmarks) -> float:
        """计算姿态分数"""
        group_scores = {}
        
        # 计算每组关键点的分数
        for group_name, indices in self.keypoint_groups.items():
            visibilities = [landmarks[idx].visibility for idx in indices]
            group_scores[group_name] = sum(visibilities) / len(visibilities)
        
        # 计算加权总分
        total_score = sum(
            group_scores[group] * weight 
            for group, weight in self.keypoint_weights.items()
        )
        
        return total_score
        
    def _determine_status(self, score: float) -> str:
        """确定完整度状态"""
        if score > 0.85:
            return "完全可见"
        elif score > 0.7:
            return "大部分可见"
        elif score > 0.5:
            return "部分遮挡"
        elif score > 0.3:
            return "严重遮挡"
        else:
            return "几乎不可见"
            
    def visualize(self, image: np.ndarray, score: CompletenessScore) -> np.ndarray:
        """可视化结果"""
        result = image.copy()
        
        # 绘制关键点
        results = self.pose.process(cv2.cvtColor(result, cv2.COLOR_BGR2RGB))
        if results.pose_landmarks:
            self.mp_draw.draw_landmarks(
                result, 
                results.pose_landmarks, 
                self.mp_pose.POSE_CONNECTIONS
            )
        
        # 添加文字信息
        # cv2.putText(result, f"status: {score.status}", (10, 30),
        #             cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.putText(result, f"total score: {score.total_score:.2f}", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        return result

def test_detector():
    """测试人体完整度检测"""
    detector = BodyCompletenessDetector()
    image_path = "E:\git\MultiHeadPassengerFlow\GUI\extracted_persons\person_52_1741937768487_-1.jpg"
    # if not image_path.exists():
    #     print(f"未找到测试图片: {image_path}")
    #     return
        
    image = cv2.imread(str(image_path))
    if image is None:
        print("图片加载失败")
        return
        
    score = detector.detect(image)
    print("\n检测结果:")
    print(f"可见关键点: {score.visible_keypoints}/{score.total_keypoints}")
    print(f"可见性分数: {score.visibility_score:.2f}")
    print(f"姿态分数: {score.pose_score:.2f}")
    print(f"总分: {score.total_score:.2f}")
    print(f"状态: {score.status}")
    
    # 显示结果
    result = detector.visualize(image, score)
    cv2.imshow("人体完整度检测", result)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    test_detector()