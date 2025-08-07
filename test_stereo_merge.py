#!/usr/bin/env python3
"""
测试立体声合并功能
"""

import numpy as np
from utils.localization import merge_stereo_to_mono, compute_rms

def test_stereo_merge():
    """测试立体声合并功能"""
    print("=== 立体声合并测试 ===")
    
    # 创建模拟的立体声数据 (12个通道 = 6个立体声对)
    sample_rate = 44100
    duration = 0.1
    samples = int(sample_rate * duration)
    
    # 创建测试信号：每个立体声对有不同的响度
    test_signals = np.zeros((12, samples))
    
    # 立体声对1: 左声道=0.5, 右声道=0.3
    test_signals[0] = 0.5 * np.sin(2 * np.pi * 440 * np.linspace(0, duration, samples))
    test_signals[1] = 0.3 * np.sin(2 * np.pi * 440 * np.linspace(0, duration, samples))
    
    # 立体声对2: 左声道=0.2, 右声道=0.8
    test_signals[2] = 0.2 * np.sin(2 * np.pi * 880 * np.linspace(0, duration, samples))
    test_signals[3] = 0.8 * np.sin(2 * np.pi * 880 * np.linspace(0, duration, samples))
    
    # 立体声对3: 左声道=0.1, 右声道=0.1
    test_signals[4] = 0.1 * np.sin(2 * np.pi * 220 * np.linspace(0, duration, samples))
    test_signals[5] = 0.1 * np.sin(2 * np.pi * 220 * np.linspace(0, duration, samples))
    
    # 立体声对4: 左声道=0.7, 右声道=0.7
    test_signals[6] = 0.7 * np.sin(2 * np.pi * 660 * np.linspace(0, duration, samples))
    test_signals[7] = 0.7 * np.sin(2 * np.pi * 660 * np.linspace(0, duration, samples))
    
    # 立体声对5: 左声道=0.0, 右声道=0.0
    test_signals[8] = 0.0
    test_signals[9] = 0.0
    
    # 立体声对6: 左声道=0.9, 右声道=0.1
    test_signals[10] = 0.9 * np.sin(2 * np.pi * 1100 * np.linspace(0, duration, samples))
    test_signals[11] = 0.1 * np.sin(2 * np.pi * 1100 * np.linspace(0, duration, samples))
    
    print(f"原始信号形状: {test_signals.shape}")
    print(f"原始信号 - 前4个通道的RMS:")
    for i in range(4):
        rms = np.sqrt(np.mean(test_signals[i] ** 2))
        print(f"  通道 {i}: {rms:.3f}")
    
    # 测试立体声合并
    print(f"\n=== 立体声合并结果 ===")
    mono_signals = merge_stereo_to_mono(test_signals)
    print(f"合并后信号形状: {mono_signals.shape}")
    
    for i in range(6):
        rms = np.sqrt(np.mean(mono_signals[i] ** 2))
        left_rms = np.sqrt(np.mean(test_signals[i*2] ** 2))
        right_rms = np.sqrt(np.mean(test_signals[i*2+1] ** 2))
        expected_rms = (left_rms + right_rms) / 2.0
        print(f"立体声对 {i+1}: 左={left_rms:.3f}, 右={right_rms:.3f}, 合并={rms:.3f}, 期望={expected_rms:.3f}")
    
    # 测试compute_rms函数
    print(f"\n=== compute_rms 函数测试 ===")
    rms_with_merge = compute_rms(test_signals, merge_stereo=True)
    rms_without_merge = compute_rms(test_signals, merge_stereo=False)
    
    print(f"合并立体声的RMS: {rms_with_merge}")
    print(f"不合并的RMS (前6个): {rms_without_merge[:6]}")
    
    print(f"\n✅ 立体声合并测试完成！")

if __name__ == "__main__":
    test_stereo_merge() 