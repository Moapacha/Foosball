import yaml
import numpy as np
from utils.audio_stream import AudioStream
from utils.localization import compute_rms, estimate_position, detect_goals
from utils.osc_sender import OSCSender
from utils.tempo_mapper import TempoMapper

def load_config(path="mic_config.yaml"):
    with open(path, 'r') as f:
        config = yaml.safe_load(f)
    return config

def main():
    print("=== Foosball 声音定位系统 ===")
    print("程序开始运行...")
    config = load_config()
    print(f"配置加载成功")
    
    mic_positions = np.array([mic['position'] for mic in config['mics'][:6]])  # 只使用前6个麦克风进行定位
    device_id = config['device_id']
    sample_rate = config['sample_rate']
    channels = config['channels']
    chunk_duration = config['chunk_duration']
    
    # OSC配置
    osc_ip = config['osc']['ip']
    osc_port = config['osc']['port']
    osc_address = config['osc']['address']
    
    # 位置估计独立OSC配置
    position_osc_ip = config['position_osc']['ip']
    position_osc_port = config['position_osc']['port']
    position_osc_address = config['position_osc']['address']
    
    print(f"麦克风位置: {mic_positions}")
    print(f"音频设备ID: {device_id}")
    print(f"采样率: {sample_rate}")
    print(f"通道数: {channels}")
    print(f"采样时长: {chunk_duration}")
    print(f"主OSC目标: {osc_ip}:{osc_port}")
    print(f"主OSC地址: {osc_address}")
    print(f"位置OSC目标: {position_osc_ip}:{position_osc_port}")
    print(f"位置OSC地址: {position_osc_address}")

    audio_stream = AudioStream(device=device_id, samplerate=sample_rate,
                               channels=channels, chunk_duration=chunk_duration)
    osc_sender = OSCSender(ip=osc_ip, port=osc_port, 
                          position_ip=position_osc_ip, position_port=position_osc_port)
    
    # 初始化BPM映射器
    tempo_mapper = TempoMapper(
        base_bpm=120,
        max_bpm=180,
        min_bpm=60,
        attack_rate=0.1,
        decay_rate=0.05,
        silence_decay_rate=0.3,
        silence_threshold=0.05
    )

    print("\n开始采集与定位，按 Ctrl+C 退出")
    print("请确保:")
    print("1. BlackHole 16ch 设备正在接收音频")
    print("2. Max/MSP 已启动并配置了OSC接收")
    print("3. Max/MSP 监听端口 11111 (主状态)")
    print("4. Max/MSP 监听端口 11112 (位置估计)")

    try:
        while True:
            audio_chunk = audio_stream.get_audio_chunk()  # (channels, samples)
            
            # 分离立体声通道和球门麦克风
            stereo_channels = audio_chunk[:12]  # 前12个通道是立体声
            goal_channels = audio_chunk[12:]    # 后2个通道是球门麦克风
            
            # 处理立体声通道
            stereo_rms = compute_rms(stereo_channels, merge_stereo=True)  # 合并立体声为单声道
            pos = estimate_position(stereo_rms, mic_positions)  # (2,)
            
            # 处理球门麦克风
            goal_rms = compute_rms(goal_channels, merge_stereo=False)  # 球门麦克风是单声道
            goal_detection = detect_goals(goal_rms)  # [左球门进球(0/1), 右球门进球(0/1)]
            
            # 计算BPM和映射响度
            bpm, mapped_intensity = tempo_mapper.update_bpm(stereo_rms)
            
            # 计算每个通道的映射响度
            mapped_channels = []
            for i in range(6):  # 6个立体声通道
                channel_rms = stereo_rms[i] if i < len(stereo_rms) else 0
                channel_intensity = tempo_mapper.calculate_intensity([channel_rms])
                mapped_channel = tempo_mapper.map_intensity_to_0_100(channel_intensity)
                mapped_channels.append(mapped_channel)
            
            print(f"映射响度: {[f'{v:.1f}' for v in mapped_channels]}, 估计位置: {pos.round(3)}, 进球检测: {goal_detection}, BPM: {bpm:.1f}")
            
            # 发送主状态数据
            osc_sender.send_full_status(stereo_rms, pos[0], pos[1], goal_detection, bpm)
            
            # 发送位置估计到独立端口
            osc_sender.send_position(pos[0], pos[1])
    except KeyboardInterrupt:
        print("\n退出程序")

if __name__ == "__main__":
    main()
