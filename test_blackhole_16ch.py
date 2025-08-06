#!/usr/bin/env python3
"""
测试 BlackHole 16ch 设备的音频输入（6通道模式）
"""

import sounddevice as sd
import numpy as np
import time

def test_blackhole_6ch():
    """测试 BlackHole 16ch 设备的音频输入（使用前6个通道）"""
    print("=== BlackHole 16ch 音频输入测试（6通道模式）===")
    
    # 配置参数
    device_id = 1  # BlackHole 16ch 设备ID
    sample_rate = 44100
    channels = 6   # 只使用6个通道
    duration = 0.1  # 每次采样0.1秒
    
    print(f"设备ID: {device_id}")
    print(f"采样率: {sample_rate}")
    print(f"通道数: {channels}")
    print(f"采样时长: {duration}秒")
    print("\n开始测试音频输入...")
    print("请确保有音频源正在输出到 BlackHole 16ch 设备的前6个通道")
    print("按 Ctrl+C 退出\n")
    
    try:
        while True:
            # 录制音频
            recording = sd.rec(int(sample_rate * duration), 
                             samplerate=sample_rate,
                             channels=channels, 
                             device=device_id)
            sd.wait()
            
            # 计算每个通道的RMS值
            rms_values = np.sqrt(np.mean(recording ** 2, axis=0))
            
            # 显示结果
            print(f"时间: {time.strftime('%H:%M:%S')}")
            print(f"响度: {rms_values.round(4)}")
            print(f"最大响度: {np.max(rms_values):.4f} (通道 {np.argmax(rms_values)})")
            print(f"平均响度: {np.mean(rms_values):.4f}")
            print("-" * 50)
            
            time.sleep(0.5)  # 等待0.5秒再进行下一次采样
            
    except KeyboardInterrupt:
        print("\n测试结束")

if __name__ == "__main__":
    test_blackhole_6ch() 