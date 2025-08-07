#!/usr/bin/env python3
"""
测试进球检测功能
"""

import numpy as np
from utils.localization import detect_goals, compute_rms

def test_goal_detection():
    """测试进球检测功能"""
    print("=== 进球检测测试 ===")
    
    # 创建模拟的14通道音频数据
    sample_rate = 44100
    duration = 0.1
    samples = int(sample_rate * duration)
    
    # 创建测试信号
    test_signals = np.zeros((14, samples))
    
    # 前12个通道是立体声（6个立体声对）
    for i in range(6):
        # 每个立体声对有不同的响度
        left_amp = 0.1 + i * 0.1
        right_amp = 0.1 + i * 0.1
        test_signals[i*2] = left_amp * np.sin(2 * np.pi * (440 + i*100) * np.linspace(0, duration, samples))
        test_signals[i*2+1] = right_amp * np.sin(2 * np.pi * (440 + i*100) * np.linspace(0, duration, samples))
    
    # 后2个通道是球门麦克风
    # 通道12: 左球门麦克风
    # 通道13: 右球门麦克风
    
    print("测试场景1: 无进球")
    goal_rms = compute_rms(test_signals[12:], merge_stereo=False)
    goal_detection = detect_goals(goal_rms, goal_threshold=0.3)
    print(f"球门RMS: {goal_rms}")
    print(f"进球检测: {goal_detection}")
    print()
    
    print("测试场景2: 左球门进球")
    # 增加左球门麦克风的音量
    test_signals[12] = 0.5 * np.sin(2 * np.pi * 800 * np.linspace(0, duration, samples))
    goal_rms = compute_rms(test_signals[12:], merge_stereo=False)
    goal_detection = detect_goals(goal_rms, goal_threshold=0.3)
    print(f"球门RMS: {goal_rms}")
    print(f"进球检测: {goal_detection}")
    print()
    
    print("测试场景3: 右球门进球")
    # 重置左球门，增加右球门麦克风的音量
    test_signals[12] = 0.1 * np.sin(2 * np.pi * 800 * np.linspace(0, duration, samples))
    test_signals[13] = 0.6 * np.sin(2 * np.pi * 800 * np.linspace(0, duration, samples))
    goal_rms = compute_rms(test_signals[12:], merge_stereo=False)
    goal_detection = detect_goals(goal_rms, goal_threshold=0.3)
    print(f"球门RMS: {goal_rms}")
    print(f"进球检测: {goal_detection}")
    print()
    
    print("测试场景4: 双球门同时进球")
    # 两个球门都有高音量
    test_signals[12] = 0.7 * np.sin(2 * np.pi * 800 * np.linspace(0, duration, samples))
    test_signals[13] = 0.8 * np.sin(2 * np.pi * 800 * np.linspace(0, duration, samples))
    goal_rms = compute_rms(test_signals[12:], merge_stereo=False)
    goal_detection = detect_goals(goal_rms, goal_threshold=0.3)
    print(f"球门RMS: {goal_rms}")
    print(f"进球检测: {goal_detection}")
    print()
    
    # 测试不同阈值
    print("=== 阈值测试 ===")
    thresholds = [0.1, 0.2, 0.3, 0.4, 0.5]
    for threshold in thresholds:
        goal_detection = detect_goals(goal_rms, goal_threshold=threshold)
        print(f"阈值 {threshold}: 进球检测 {goal_detection}")
    
    print(f"\n✅ 进球检测测试完成！")

if __name__ == "__main__":
    test_goal_detection() 