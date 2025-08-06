#!/usr/bin/env python3
"""
详细的OSC连接测试脚本
用于诊断OSC连接问题
"""

import time
import yaml
from pythonosc.udp_client import SimpleUDPClient
import socket

def load_config(path="mic_config.yaml"):
    with open(path, 'r') as f:
        config = yaml.safe_load(f)
    return config

def test_port_availability(ip, port):
    """测试端口是否可用"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(1)
        result = sock.connect_ex((ip, port))
        sock.close()
        return result == 0
    except Exception as e:
        print(f"端口测试错误: {e}")
        return False

def test_osc_connection():
    print("=== 详细OSC连接测试 ===")
    
    config = load_config()
    osc_ip = config['osc']['ip']
    osc_port = config['osc']['port']
    osc_address = config['osc']['address']
    
    print(f"配置的OSC设置:")
    print(f"  IP地址: {osc_ip}")
    print(f"  端口: {osc_port}")
    print(f"  OSC地址: {osc_address}")
    print()
    
    # 测试端口可用性
    print("测试端口可用性...")
    if test_port_availability(osc_ip, osc_port):
        print(f"✅ 端口 {osc_port} 可用")
    else:
        print(f"❌ 端口 {osc_port} 不可用")
        print("请检查:")
        print("1. VCV Rack 是否已启动")
        print("2. cvOSCcv 模块是否正确配置")
        print("3. 端口号是否正确")
        return False
    
    print("\n开始发送测试OSC消息...")
    print("请检查 VCV Rack 中的 cvOSCcv 模块是否收到数据")
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
                time.sleep(3)  # 每3秒发送一次
                
    except KeyboardInterrupt:
        print("\n测试结束")
    except Exception as e:
        print(f"OSC发送错误: {e}")
        return False
    
    return True

if __name__ == "__main__":
    test_osc_connection() 