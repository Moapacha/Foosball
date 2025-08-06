import yaml
import numpy as np
from utils.audio_stream import AudioStream
from utils.localization import compute_rms, estimate_position
from utils.osc_sender import OSCSender

def load_config(path="mic_config.yaml"):
    with open(path, 'r') as f:
        config = yaml.safe_load(f)
    return config

def main():
    print("=== Foosball 声音定位系统 ===")
    print("程序开始运行...")
    config = load_config()
    print(f"配置加载成功")
    
    mic_positions = np.array([mic['position'] for mic in config['mics']])
    device_id = config['device_id']
    sample_rate = config['sample_rate']
    channels = config['channels']
    chunk_duration = config['chunk_duration']
    
    # OSC配置
    osc_ip = config['osc']['ip']
    osc_port = config['osc']['port']
    osc_address = config['osc']['address']
    
    print(f"麦克风位置: {mic_positions}")
    print(f"音频设备ID: {device_id}")
    print(f"采样率: {sample_rate}")
    print(f"通道数: {channels}")
    print(f"采样时长: {chunk_duration}")
    print(f"OSC目标: {osc_ip}:{osc_port}")
    print(f"OSC地址: {osc_address}")

    audio_stream = AudioStream(device=device_id, samplerate=sample_rate,
                               channels=channels, chunk_duration=chunk_duration)
    osc_sender = OSCSender(ip=osc_ip, port=osc_port)

    print("\n开始采集与定位，按 Ctrl+C 退出")
    print("请确保:")
    print("1. BlackHole 16ch 设备正在接收音频")
    print("2. VCV Rack 已启动并配置了OSC接收模块")
    print("3. VCV Rack 监听端口 7001")

    try:
        while True:
            audio_chunk = audio_stream.get_audio_chunk()  # (channels, samples)
            rms = compute_rms(audio_chunk)                # (channels,)
            pos = estimate_position(rms, mic_positions)  # (2,)
            
            print(f"响度: {rms.round(3)}, 估计位置: {pos.round(3)}")
            osc_sender.send_position(pos[0], pos[1])
    except KeyboardInterrupt:
        print("\n退出程序")

if __name__ == "__main__":
    main()
