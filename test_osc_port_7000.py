#!/usr/bin/env python3
"""
使用端口 7000 的 OSC 测试脚本
"""

import time
from pythonosc.udp_client import SimpleUDPClient

def test_osc_port_7000():
    print("=== OSC 端口 7000 测试 ===")
    
    osc_ip = "127.0.0.1"
    osc_port = 7000
    osc_address = "/position"
    
    print(f"发送OSC消息到: {osc_ip}:{osc_port}")
    print(f"OSC地址: {osc_address}")
    print("请确保 VCV Rack 中的 cvOSCcv 模块设置为端口 7000")
    print("按 Ctrl+C 停止测试\n")
    
    try:
        client = SimpleUDPClient(osc_ip, osc_port)
        
        # 测试不同的位置
        test_positions = [
            (0, 0, "左上角"),
            (117, 0, "右上角"),
            (58.5, 34, "中心"),
            (0, 68, "左下角"),
            (117, 68, "右下角"),
        ]
        
        while True:
            for x, y, name in test_positions:
                print(f"发送位置: ({x}, {y}) - {name}")
                client.send_message(osc_address, [float(x), float(y)])
                time.sleep(2)  # 每2秒发送一次
                
    except KeyboardInterrupt:
        print("\n测试结束")
    except Exception as e:
        print(f"OSC发送错误: {e}")

if __name__ == "__main__":
    test_osc_port_7000() 