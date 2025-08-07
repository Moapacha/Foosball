#!/usr/bin/env python3
"""
网络数据包监控工具
监控 UDP 端口 7001 的数据包
"""

import socket
import struct
import time
import threading

def monitor_udp_port(port=7001, duration=30):
    """监控指定端口的 UDP 数据包"""
    print(f"=== UDP 端口 {port} 监控 ===")
    print(f"监控时长: {duration} 秒")
    print("按 Ctrl+C 停止监控\n")
    
    # 创建原始套接字
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('127.0.0.1', port))
        sock.settimeout(1)
        
        print(f"🎧 开始监控端口 {port}...")
        start_time = time.time()
        packet_count = 0
        
        while time.time() - start_time < duration:
            try:
                data, addr = sock.recvfrom(1024)
                packet_count += 1
                
                print(f"📦 数据包 #{packet_count}")
                print(f"   来源: {addr}")
                print(f"   大小: {len(data)} 字节")
                print(f"   时间: {time.strftime('%H:%M:%S.%f')[:-3]}")
                
                # 尝试解析 OSC 消息
                try:
                    # OSC 消息的基本结构
                    if len(data) > 0:
                        print(f"   数据: {data[:50]}...")  # 显示前50字节
                        
                        # 尝试解析 OSC 地址
                        if data.startswith(b'/position'):
                            print(f"   ✅ 检测到 OSC /position 消息")
                        else:
                            print(f"   ℹ️  其他 OSC 消息")
                            
                except Exception as e:
                    print(f"   ⚠️  数据解析错误: {e}")
                
                print("-" * 40)
                
            except socket.timeout:
                continue
            except Exception as e:
                print(f"❌ 接收数据错误: {e}")
                break
        
        print(f"\n📊 监控统计:")
        print(f"   总数据包数: {packet_count}")
        print(f"   平均频率: {packet_count/duration:.1f} 包/秒")
        
        sock.close()
        
    except Exception as e:
        print(f"❌ 监控器错误: {e}")

def test_osc_sending():
    """测试 OSC 发送"""
    print("\n=== 测试 OSC 发送 ===")
    
    try:
        from pythonosc.udp_client import SimpleUDPClient
        
        client = SimpleUDPClient("127.0.0.1", 7001)
        
        for i in range(5):
            x, y = 58.5 + i, 34.0 + i
            print(f"发送: ({x}, {y})")
            client.send_message("/position", [float(x), float(y)])
            time.sleep(0.5)
            
        print("✅ OSC 发送测试完成")
        
    except Exception as e:
        print(f"❌ OSC 发送测试失败: {e}")

def main():
    """主函数"""
    print("=== 网络数据包监控工具 ===")
    
    # 启动监控线程
    monitor_thread = threading.Thread(target=monitor_udp_port, args=(7001, 10))
    monitor_thread.daemon = True
    monitor_thread.start()
    
    # 等待一秒让监控器启动
    time.sleep(1)
    
    # 测试 OSC 发送
    test_osc_sending()
    
    # 等待监控完成
    monitor_thread.join()
    
    print("\n🎉 网络监控完成！")

if __name__ == "__main__":
    main() 