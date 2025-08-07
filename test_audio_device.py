import sounddevice as sd
import numpy as np
import time

def test_audio_device():
    """测试音频设备配置"""
    print("=== 音频设备测试 ===")
    
    # 测试设备0 (BlackHole 16ch)
    print("测试设备0 (BlackHole 16ch):")
    try:
        device_info = sd.query_devices(0)
        print(f"设备信息: {device_info}")
        
        # 测试录音
        print("开始录音测试 (3秒)...")
        recording = sd.rec(int(44100 * 3), samplerate=44100, channels=14, device=0)
        sd.wait()
        
        # 分析录音数据
        print(f"录音形状: {recording.shape}")
        print(f"数据类型: {recording.dtype}")
        print(f"数据范围: [{recording.min():.6f}, {recording.max():.6f}]")
        
        # 计算每个通道的RMS
        rms_values = np.sqrt(np.mean(recording ** 2, axis=0))
        print(f"各通道RMS值: {rms_values}")
        
        # 检查是否有非零数据
        non_zero_channels = np.sum(rms_values > 0.001)
        print(f"有信号的通道数: {non_zero_channels}")
        
        if non_zero_channels == 0:
            print("⚠️  警告: 所有通道都没有检测到信号!")
            print("可能的原因:")
            print("1. BlackHole设备没有接收到音频")
            print("2. 音频源没有正确路由到BlackHole")
        else:
            print("✅ 检测到音频信号")
            
    except Exception as e:
        print(f"❌ 测试设备0失败: {e}")
    
    # 测试设备1 (BlackHole 2ch)
    print(f"\n测试设备1 (BlackHole 2ch):")
    try:
        device_info = sd.query_devices(1)
        print(f"设备信息: {device_info}")
        
        # 测试录音
        print("开始录音测试 (3秒)...")
        recording = sd.rec(int(44100 * 3), samplerate=44100, channels=2, device=1)
        sd.wait()
        
        # 分析录音数据
        print(f"录音形状: {recording.shape}")
        print(f"数据范围: [{recording.min():.6f}, {recording.max():.6f}]")
        
        # 计算RMS
        rms_values = np.sqrt(np.mean(recording ** 2, axis=0))
        print(f"各通道RMS值: {rms_values}")
        
    except Exception as e:
        print(f"❌ 测试设备1失败: {e}")

def test_main_config():
    """测试主程序配置"""
    print("\n=== 主程序配置测试 ===")
    
    try:
        import yaml
        from utils.audio_stream import AudioStream
        
        # 加载配置
        with open("mic_config.yaml", 'r') as f:
            config = yaml.safe_load(f)
        
        print(f"设备ID: {config['device_id']}")
        print(f"采样率: {config['sample_rate']}")
        print(f"通道数: {config['channels']}")
        
        # 测试AudioStream
        audio_stream = AudioStream(
            device=config['device_id'],
            samplerate=config['sample_rate'],
            channels=config['channels'],
            chunk_duration=config['chunk_duration']
        )
        
        print("✅ AudioStream初始化成功")
        
        # 测试录音
        print("测试录音...")
        audio_chunk = audio_stream.get_audio_chunk()
        print(f"录音形状: {audio_chunk.shape}")
        print(f"数据范围: [{audio_chunk.min():.6f}, {audio_chunk.max():.6f}]")
        
        print("✅ 主程序配置测试通过")
        
    except Exception as e:
        print(f"❌ 主程序配置测试失败: {e}")

if __name__ == "__main__":
    test_audio_device()
    test_main_config() 