import numpy as np

def compute_rms(signals):
    """
    signals: np.array, shape (channels, samples)
    返回每个通道的RMS值，shape (channels,)
    """
    return np.sqrt(np.mean(signals ** 2, axis=1))

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
