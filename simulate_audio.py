import numpy as np
import time
import yaml
from utils.localization import estimate_position, detect_goals
from utils.osc_sender import OSCSender
from utils.tempo_mapper import TempoMapper

def load_config(path="mic_config.yaml"):
    with open(path, 'r') as f:
        config = yaml.safe_load(f)
    return config

def generate_simulated_rms():
    """
    生成模拟的RMS值，6个通道同时发出随机大于60响度的数据
    """
    # 基础响度（60-100之间）
    base_intensity = np.random.uniform(60, 100)
    
    # 为每个通道添加随机变化（±20）
    channel_variations = np.random.uniform(-20, 20, 6)
    
    # 确保所有通道都大于60
    simulated_rms = np.maximum(base_intensity + channel_variations, 60)
    
    # 添加一些随机噪声让数据更真实
    noise = np.random.normal(0, 5, 6)
    simulated_rms += noise
    
    # 确保值在合理范围内
    simulated_rms = np.clip(simulated_rms, 0, 100)
    
    return simulated_rms

def simulate_audio_stream():
    """模拟音频流，生成连续的响度数据"""
    print("=== 模拟音频流测试 ===")
    print("生成6个通道的随机响度数据（>60）")
    print("按 Ctrl+C 退出")
    print("-" * 50)
    
    # 加载配置
    config = load_config()
    mic_positions = np.array([mic['position'] for mic in config['mics'][:6]])
    
    # OSC配置
    osc_ip = config['osc']['ip']
    osc_port = config['osc']['port']
    
    # 位置估计独立OSC配置
    position_osc_ip = config['position_osc']['ip']
    position_osc_port = config['position_osc']['port']
    
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
    
    # 模拟球门麦克风数据
    goal_rms = np.array([0.0, 0.0])  # 暂时设为0
    
    try:
        while True:
            # 生成模拟的RMS数据
            stereo_rms = generate_simulated_rms()
            
            # 计算位置
            pos = estimate_position(stereo_rms, mic_positions)
            
            # 检测进球
            goal_detection = detect_goals(goal_rms)
            
            # 计算BPM和映射响度
            bpm, mapped_intensity = tempo_mapper.update_bpm(stereo_rms)
            
            # 计算每个通道的映射响度
            mapped_channels = []
            for i in range(6):
                channel_rms = stereo_rms[i] if i < len(stereo_rms) else 0
                channel_intensity = tempo_mapper.calculate_intensity([channel_rms])
                mapped_channel = tempo_mapper.map_intensity_to_0_100(channel_intensity)
                mapped_channels.append(mapped_channel)
            
            print(f"映射响度: {[f'{v:.1f}' for v in mapped_channels]}, 估计位置: {pos.round(3)}, 进球检测: {goal_detection}, BPM: {bpm:.1f}")
            
            # 发送主状态数据
            osc_sender.send_full_status(stereo_rms, pos[0], pos[1], goal_detection, bpm)
            
            # 发送位置估计到独立端口
            osc_sender.send_position(pos[0], pos[1])
            
            # 控制更新频率
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\n退出模拟程序")

def test_bpm_calculation():
    """测试BPM计算逻辑"""
    print("=== BPM计算测试 ===")
    
    tempo_mapper = TempoMapper()
    
    # 测试不同响度级别的BPM变化
    test_scenarios = [
        "低响度测试 (60-70)",
        "中等响度测试 (70-80)", 
        "高响度测试 (80-90)",
        "最高响度测试 (90-100)"
    ]
    
    for scenario in test_scenarios:
        print(f"\n{scenario}:")
        print("-" * 30)
        
        for i in range(10):
            if "低响度" in scenario:
                rms_values = np.random.uniform(60, 70, 6)
            elif "中等响度" in scenario:
                rms_values = np.random.uniform(70, 80, 6)
            elif "高响度" in scenario:
                rms_values = np.random.uniform(80, 90, 6)
            else:
                rms_values = np.random.uniform(90, 100, 6)
            
            bpm, mapped_intensity = tempo_mapper.update_bpm(rms_values)
            avg_rms = np.mean(rms_values)
            
            print(f"  步骤 {i+1}: 平均响度={avg_rms:.1f}, BPM={bpm:.1f}")
            
            time.sleep(0.1)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_bpm_calculation()
    else:
        simulate_audio_stream() 