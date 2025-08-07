#!/usr/bin/env python3
"""
测试BPM映射功能
"""

import numpy as np
import time
from utils.tempo_mapper import TempoMapper

def test_tempo_mapper():
    """测试BPM映射功能"""
    print("=== BPM映射测试 ===")
    
    # 创建BPM映射器
    tempo_mapper = TempoMapper(
        base_bpm=120,
        max_bpm=180,
        min_bpm=60,
        attack_rate=0.1,
        decay_rate=0.05,
        silence_decay_rate=0.3,
        silence_threshold=0.05
    )
    
    print("测试场景1: 静音状态")
    for i in range(10):
        rms_values = [0.01, 0.02, 0.01, 0.02, 0.01, 0.02]  # 低音量
        bpm = tempo_mapper.update_bpm(rms_values)
        print(f"  步骤 {i+1}: RMS={np.mean(rms_values):.3f}, BPM={bpm:.1f}")
        time.sleep(0.1)
    
    print("\n测试场景2: 正常音量")
    for i in range(10):
        rms_values = [0.1, 0.15, 0.12, 0.13, 0.11, 0.14]  # 正常音量
        bpm = tempo_mapper.update_bpm(rms_values)
        print(f"  步骤 {i+1}: RMS={np.mean(rms_values):.3f}, BPM={bpm:.1f}")
        time.sleep(0.1)
    
    print("\n测试场景3: 激烈场面")
    for i in range(10):
        # 逐渐增加音量
        intensity = 0.2 + i * 0.05
        rms_values = [intensity, intensity*1.1, intensity*0.9, intensity*1.2, intensity*0.8, intensity*1.0]
        bpm = tempo_mapper.update_bpm(rms_values)
        print(f"  步骤 {i+1}: RMS={np.mean(rms_values):.3f}, BPM={bpm:.1f}")
        time.sleep(0.1)
    
    print("\n测试场景4: 非常激烈")
    for i in range(10):
        rms_values = [0.8, 0.9, 0.7, 1.0, 0.6, 0.8]  # 高音量
        bpm = tempo_mapper.update_bpm(rms_values)
        print(f"  步骤 {i+1}: RMS={np.mean(rms_values):.3f}, BPM={bpm:.1f}")
        time.sleep(0.1)
    
    print("\n测试场景5: 回到静音")
    for i in range(15):
        rms_values = [0.01, 0.02, 0.01, 0.02, 0.01, 0.02]  # 低音量
        bpm = tempo_mapper.update_bpm(rms_values)
        print(f"  步骤 {i+1}: RMS={np.mean(rms_values):.3f}, BPM={bpm:.1f}")
        time.sleep(0.1)
    
    print(f"\n✅ BPM映射测试完成！")

def test_intensity_calculation():
    """测试强度计算"""
    print("\n=== 强度计算测试 ===")
    
    tempo_mapper = TempoMapper()
    
    # 测试不同RMS值的强度计算
    test_cases = [
        ([0.1, 0.1, 0.1, 0.1, 0.1, 0.1], "均匀低音量"),
        ([0.5, 0.3, 0.4, 0.2, 0.3, 0.4], "中等音量"),
        ([0.8, 0.9, 0.7, 1.0, 0.6, 0.8], "高音量"),
        ([0.1, 0.8, 0.1, 0.8, 0.1, 0.8], "变化剧烈"),
    ]
    
    for rms_values, description in test_cases:
        intensity = tempo_mapper.calculate_intensity(rms_values)
        print(f"{description}: RMS={rms_values}, 强度={intensity:.3f}")

if __name__ == "__main__":
    test_tempo_mapper()
    test_intensity_calculation() 