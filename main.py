import yaml
import numpy as np
from utils.audio_stream import AudioStream
from utils.localization import compute_rms, estimate_position_enhanced, estimate_position_with_smoothing, detect_goals
from utils.osc_sender import OSCSender
from utils.tempo_mapper import TempoMapper

def load_config(path="mic_config.yaml"):
    with open(path, 'r') as f:
        config = yaml.safe_load(f)
    return config

def map_coordinates_to_osc_range(x, y):
    """
    将原始坐标映射到OSC范围（-1到1）
    新坐标系: x: 0-117 -> -1到1, y: 0-68 -> -1到1
    """
    x_mapped = 2.0 * float(x) / 117.0 - 1.0
    y_mapped = 2.0 * float(y) / 68.0 - 1.0
    return x_mapped, y_mapped

def main():
    print("=== Foosball 声音定位系统 ===")
    print("程序开始运行...")
    config = load_config()
    print(f"配置加载成功")
    
    # 使用通道3-8进行定位（对应索引2-7）
    mic_positions = np.array([mic['position'] for mic in config['mics'][2:8]])
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
    
    # 位置平滑处理变量
    prev_position = None
    smoothing_factor = 0.6  # 平滑因子，可以调整

    print("\n开始采集与定位，按 Ctrl+C 退出")
    print("使用增强定位算法 + 平滑处理")
    print("请确保:")
    print("1. BlackHole 16ch 设备正在接收音频")
    print("2. Max/MSP 已启动并配置了OSC接收")
    print("3. Max/MSP 监听端口 11111 (主状态)")
    print("4. Max/MSP 监听端口 7777 (位置估计)")
    print("新布局: 蓝方(左) vs 红方(右)")
    print("麦克风布局: 1左门, 2右门, 3左下, 4左上, 5中下, 6中上, 7右下, 8右上")
    print("坐标系统: 原始坐标(0-117, 0-68) -> OSC坐标(-1到1, -1到1)")

    try:
        while True:
            audio_chunk = audio_stream.get_audio_chunk()  # (channels, samples)
            
            # 提取球门麦克风通道（1-2通道，对应索引0-1）
            goal_channels = audio_chunk[:2]  # 通道1-2用于进球检测
            # 提取定位麦克风通道（3-8通道，对应索引2-7）
            main_channels = audio_chunk[2:8]  # 通道3-8用于定位
            
            # 处理定位麦克风通道
            main_rms = compute_rms(main_channels, merge_stereo=False)  # 单声道处理
            
            # 使用增强的定位算法和平滑处理
            raw_pos = estimate_position_with_smoothing(main_rms, mic_positions, prev_position, smoothing_factor)
            prev_position = raw_pos.copy()  # 保存当前位置用于下次平滑
            
            # 映射到OSC坐标范围
            osc_x, osc_y = map_coordinates_to_osc_range(raw_pos[0], raw_pos[1])
            
            # 处理球门麦克风
            goal_rms = compute_rms(goal_channels, merge_stereo=False)  # 球门麦克风是单声道
            goal_detection = detect_goals(goal_rms)  # [左球门进球(0/1), 右球门进球(0/1)]
            
            # 计算BPM和映射响度
            bpm, mapped_intensity = tempo_mapper.update_bpm(main_rms)
            
            # 计算每个通道的映射响度
            mapped_channels = []
            for i in range(6):  # 6个定位麦克风通道
                channel_rms = main_rms[i] if i < len(main_rms) else 0
                channel_intensity = tempo_mapper.calculate_intensity([channel_rms])
                mapped_channel = tempo_mapper.map_intensity_to_0_127(channel_intensity)
                mapped_channels.append(mapped_channel)
            
            # 输出原始坐标和OSC坐标，确保同步，并显示球门音量
            print(f"映射响度: {[f'{v:.1f}' for v in mapped_channels]}, 原始位置: ({raw_pos[0]:.1f}, {raw_pos[1]:.1f}), OSC位置: ({osc_x:.3f}, {osc_y:.3f}), 球门音量: 左门[{goal_rms[0]:.3f}] 右门[{goal_rms[1]:.3f}], 进球检测: {goal_detection}, BPM: {bpm:.1f}")
            
            # 发送主状态数据（使用原始坐标）
            osc_sender.send_full_status(mapped_channels, raw_pos[0], raw_pos[1], goal_detection, bpm)
            
            # 发送位置估计到独立端口（使用OSC坐标）
            osc_sender.send_position(osc_x, osc_y)
    except KeyboardInterrupt:
        print("\n退出程序")
    finally:
        audio_stream.close()

if __name__ == "__main__":
    main()
