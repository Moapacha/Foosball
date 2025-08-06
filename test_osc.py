#!/usr/bin/env python3
"""
OSC发送测试脚本
用于测试OSC消息是否能正确发送到VCV Rack
"""

import time
import yaml
from utils.osc_sender import OSCSender

def load_config(path="mic_config.yaml"):
    with open(path, 'r') as f:
        config = yaml.safe_load(f)
    return config

def test_osc():
    print("=== OSC发送测试 ===")
    
    config = load_config()
    osc_ip = config['osc']['ip']
    osc_port = config['osc']['port']
    osc_address = config['osc']['address']
    
    print(f"发送OSC消息到: {osc_ip}:{osc_port}")
    print(f"OSC地址: {osc_address}")
    print("按 Ctrl+C 停止测试\n")
    
    osc_sender = OSCSender(ip=osc_ip, port=osc_port)
    
    try:
        # 测试不同的位置
        test_positions = [
            (0, 0),      # 左上角
            (117, 0),    # 右上角
            (58.5, 34),  # 中心
            (0, 68),     # 左下角
            (117, 68),   # 右下角
        ]
        
        while True:
            for x, y in test_positions:
                print(f"发送位置: ({x}, {y})")
                osc_sender.send_position(x, y)
                time.sleep(2)  # 每2秒发送一次
                
    except KeyboardInterrupt:
        print("\n测试结束")

if __name__ == "__main__":
    test_osc() 