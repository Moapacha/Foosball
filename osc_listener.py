#!/usr/bin/env python3
"""
OSC 监听器
用于监听和验证 OSC 消息
"""

import socket
import struct
import time
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer

def print_handler(address, *args):
    """处理接收到的 OSC 消息"""
    print(f"📨 收到 OSC 消息:")
    print(f"   地址: {address}")
    print(f"   参数: {args}")
    print(f"   参数类型: {[type(arg) for arg in args]}")
    print(f"   时间: {time.strftime('%H:%M:%S')}")
    print("-" * 40)

def main():
    """启动 OSC 监听器"""
    print("=== OSC 监听器 ===")
    print("监听端口: 7001")
    print("OSC 地址: /position")
    print("按 Ctrl+C 停止监听\n")
    
    # 创建调度器
    dispatcher = Dispatcher()
    dispatcher.map("/position", print_handler)
    
    # 创建服务器
    server = BlockingOSCUDPServer(("127.0.0.1", 7001), dispatcher)
    
    try:
        print("🎧 开始监听 OSC 消息...")
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n⏹️  停止监听")
    except Exception as e:
        print(f"❌ 监听器错误: {e}")

if __name__ == "__main__":
    main() 