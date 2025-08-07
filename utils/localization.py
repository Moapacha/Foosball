import numpy as np

def merge_stereo_to_mono(signals):
    """
    将立体声信号合并为单声道
    signals: np.array, shape (channels, samples)
    返回合并后的信号，shape (channels//2, samples)
    假设每两个连续通道构成一个立体声对
    """
    if signals.shape[0] % 2 != 0:
        raise ValueError("通道数必须是偶数，每个立体声对占用2个通道")
    
    num_stereo_pairs = signals.shape[0] // 2
    mono_signals = np.zeros((num_stereo_pairs, signals.shape[1]))
    
    for i in range(num_stereo_pairs):
        left_channel = signals[i * 2]      # 左声道
        right_channel = signals[i * 2 + 1] # 右声道
        # 合并为单声道 (L + R) / 2
        mono_signals[i] = (left_channel + right_channel) / 2.0
    
    return mono_signals

def compute_rms(signals, merge_stereo=True):
    """
    signals: np.array, shape (channels, samples)
    merge_stereo: 是否将立体声合并为单声道
    返回每个通道的RMS值，shape (channels,) 或 (channels//2,)
    """
    if merge_stereo and signals.shape[0] % 2 == 0:
        # 合并立体声为单声道
        mono_signals = merge_stereo_to_mono(signals)
        return np.sqrt(np.mean(mono_signals ** 2, axis=1))
    else:
        # 直接计算RMS
        return np.sqrt(np.mean(signals ** 2, axis=1))

def detect_goals(rms_values, goal_threshold=0.3, history_length=10):
    """
    检测进球
    rms_values: 包含球门麦克风RMS值的数组
    goal_threshold: 进球检测阈值
    history_length: 历史记录长度
    返回: [左球门进球(0/1), 右球门进球(0/1)]
    """
    # 球门麦克风在最后两个通道
    goal_rms = rms_values[-2:]  # 最后两个通道是球门麦克风
    
    # 简单的阈值检测（可以改进为更复杂的算法）
    left_goal = 1 if goal_rms[0] > goal_threshold else 0
    right_goal = 1 if goal_rms[1] > goal_threshold else 0
    
    return [left_goal, right_goal]

def estimate_position(rms_values, mic_positions):
    """
    rms_values: np.array, shape (channels,)
    mic_positions: np.array, shape (channels, 2) - XY坐标

    采用响度加权重心法估计声源位置
    """
    if np.sum(rms_values) == 0:
        # 防止除0
        weights = np.ones_like(rms_values) / len(rms_values)
    else:
        weights = rms_values / np.sum(rms_values)
    pos = np.sum(mic_positions * weights[:, None], axis=0)
    return pos
