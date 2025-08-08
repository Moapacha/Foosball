import numpy as np

# 全局变量用于进球检测的历史记录
goal_history = {
    'left_rms_history': [],
    'right_rms_history': [],
    'left_goal_cooldown': 0,
    'right_goal_cooldown': 0
}

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

def detect_goals(rms_values, goal_threshold=0.3, history_length=20, volume_increase_threshold=3.0, cooldown_frames=30):
    """
    基于音量变化的进球检测
    rms_values: 包含球门麦克风RMS值的数组
    goal_threshold: 基础进球检测阈值
    history_length: 历史记录长度
    volume_increase_threshold: 音量增大倍数阈值
    cooldown_frames: 进球检测冷却帧数
    返回: [左球门进球(0/127), 右球门进球(0/127)]
    新布局: 通道1是左门，通道2是右门
    """
    global goal_history
    
    # 球门麦克风在前两个通道（通道1-2，对应索引0-1）
    left_rms = rms_values[0] if len(rms_values) > 0 else 0   # 左门（通道1）
    right_rms = rms_values[1] if len(rms_values) > 1 else 0  # 右门（通道2）
    
    # 更新历史记录
    goal_history['left_rms_history'].append(left_rms)
    goal_history['right_rms_history'].append(right_rms)
    
    # 保持历史记录长度
    if len(goal_history['left_rms_history']) > history_length:
        goal_history['left_rms_history'] = goal_history['left_rms_history'][-history_length:]
    if len(goal_history['right_rms_history']) > history_length:
        goal_history['right_rms_history'] = goal_history['right_rms_history'][-history_length:]
    
    # 减少冷却时间
    if goal_history['left_goal_cooldown'] > 0:
        goal_history['left_goal_cooldown'] -= 1
    if goal_history['right_goal_cooldown'] > 0:
        goal_history['right_goal_cooldown'] -= 1
    
    # 检测进球
    left_goal = 0
    right_goal = 0
    
    # 左门进球检测
    if (goal_history['left_goal_cooldown'] == 0 and 
        len(goal_history['left_rms_history']) >= 5):
        
        # 计算最近5帧的平均音量
        recent_avg = np.mean(goal_history['left_rms_history'][-5:])
        # 计算之前10帧的平均音量（排除最近5帧）
        if len(goal_history['left_rms_history']) >= 15:
            previous_avg = np.mean(goal_history['left_rms_history'][-15:-5])
        else:
            previous_avg = np.mean(goal_history['left_rms_history'][:-5])
        
        # 检测音量突然增大
        if (recent_avg > goal_threshold and 
            recent_avg > previous_avg * volume_increase_threshold and
            left_rms > goal_threshold):
            left_goal = 127
            goal_history['left_goal_cooldown'] = cooldown_frames
            print(f"左门进球检测! 当前音量: {left_rms:.3f}, 平均音量: {recent_avg:.3f}, 之前平均: {previous_avg:.3f}")
    
    # 右门进球检测
    if (goal_history['right_goal_cooldown'] == 0 and 
        len(goal_history['right_rms_history']) >= 5):
        
        # 计算最近5帧的平均音量
        recent_avg = np.mean(goal_history['right_rms_history'][-5:])
        # 计算之前10帧的平均音量（排除最近5帧）
        if len(goal_history['right_rms_history']) >= 15:
            previous_avg = np.mean(goal_history['right_rms_history'][-15:-5])
        else:
            previous_avg = np.mean(goal_history['right_rms_history'][:-5])
        
        # 检测音量突然增大
        if (recent_avg > goal_threshold and 
            recent_avg > previous_avg * volume_increase_threshold and
            right_rms > goal_threshold):
            right_goal = 127
            goal_history['right_goal_cooldown'] = cooldown_frames
            print(f"右门进球检测! 当前音量: {right_rms:.3f}, 平均音量: {recent_avg:.3f}, 之前平均: {previous_avg:.3f}")
    
    return [left_goal, right_goal]

def estimate_position_enhanced(rms_values, mic_positions, noise_threshold=0.01, max_distance=200):
    """
    增强的位置估计算法，确保位置在左右两侧平滑移动
    rms_values: np.array, shape (channels,)
    mic_positions: np.array, shape (channels, 2) - XY坐标
    noise_threshold: 噪声阈值，低于此值的信号将被忽略
    max_distance: 最大有效距离，用于过滤异常值
    
    采用改进的加权重心法，包含噪声处理、动态权重和左右平衡机制
    """
    # 确保输入是numpy数组
    rms_values = np.array(rms_values)
    mic_positions = np.array(mic_positions)
    
    # 1. 噪声过滤
    valid_indices = rms_values > noise_threshold
    if np.sum(valid_indices) < 2:
        # 如果有效信号太少，返回中心位置
        center_pos = np.mean(mic_positions, axis=0)
        return center_pos
    
    # 2. 动态权重计算（使用平方根增强对比度）
    valid_rms = rms_values[valid_indices]
    valid_positions = mic_positions[valid_indices]
    
    # 使用平方根增强对比度，让强信号更有影响力
    enhanced_weights = np.sqrt(valid_rms)
    weights = enhanced_weights / np.sum(enhanced_weights)
    
    # 3. 计算加权位置
    weighted_pos = np.sum(valid_positions * weights[:, None], axis=0)
    
    # 4. 确保位置在有效范围内（0-117, 0-68）
    weighted_pos[0] = max(0, min(117, weighted_pos[0]))  # X坐标限制在0-117
    weighted_pos[1] = max(0, min(68, weighted_pos[1]))   # Y坐标限制在0-68
    
    # 5. 增强的左右平衡调整 - 确保x值在正负两侧平滑移动
    left_mics = valid_positions[:, 0] < 58.5  # 左侧麦克风（X < 58.5）
    right_mics = valid_positions[:, 0] > 58.5  # 右侧麦克风（X > 58.5）
    
    if np.sum(left_mics) > 0 and np.sum(right_mics) > 0:
        # 如果左右都有麦克风，计算左右权重
        left_weight = np.sum(weights[left_mics])
        right_weight = np.sum(weights[right_mics])
        
        # 动态调整权重平衡
        total_weight = left_weight + right_weight
        if total_weight > 0:
            left_ratio = left_weight / total_weight
            right_ratio = right_weight / total_weight
            
            # 如果一侧权重过小，增加该侧的影响
            if left_ratio < 0.2 and right_ratio > 0.8:
                # 左侧权重太小，增加左侧影响
                weighted_pos[0] = weighted_pos[0] * 0.7 + 20  # 向左偏移
            elif right_ratio < 0.2 and left_ratio > 0.8:
                # 右侧权重太小，增加右侧影响
                weighted_pos[0] = weighted_pos[0] * 0.7 + 97  # 向右偏移
            elif left_ratio < 0.1:
                # 左侧几乎没有信号，强制向左偏移
                weighted_pos[0] = weighted_pos[0] * 0.5 + 10
            elif right_ratio < 0.1:
                # 右侧几乎没有信号，强制向右偏移
                weighted_pos[0] = weighted_pos[0] * 0.5 + 107
    
    # 6. 距离约束（防止位置跳跃过大）
    center_pos = np.mean(mic_positions, axis=0)
    distance_to_center = np.linalg.norm(weighted_pos - center_pos)
    
    if distance_to_center > max_distance:
        # 如果距离中心太远，可能是噪声，返回中心位置
        return center_pos
    
    # 7. 确保x值在合理范围内，避免过于集中在中心
    if weighted_pos[0] < 20:
        weighted_pos[0] = max(10, weighted_pos[0])  # 确保不会太靠左
    elif weighted_pos[0] > 97:
        weighted_pos[0] = min(107, weighted_pos[0])  # 确保不会太靠右
    
    return weighted_pos

def estimate_position(rms_values, mic_positions):
    """
    原始的位置估计算法（保持向后兼容）
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

def estimate_position_with_smoothing(rms_values, mic_positions, prev_position=None, smoothing_factor=0.7):
    """
    带平滑处理的位置估计算法
    rms_values: np.array, shape (channels,)
    mic_positions: np.array, shape (channels, 2) - XY坐标
    prev_position: 前一个位置估计
    smoothing_factor: 平滑因子 (0-1)，越大越平滑
    
    结合增强算法和平滑处理，确保x值在正负两侧平滑移动
    """
    # 使用增强算法计算当前位置
    current_pos = estimate_position_enhanced(rms_values, mic_positions)
    
    # 如果有前一个位置，进行平滑处理
    if prev_position is not None:
        # 对x坐标使用更强的平滑，确保平滑移动
        x_smoothing = min(smoothing_factor + 0.1, 0.9)  # x坐标使用更强的平滑
        y_smoothing = smoothing_factor  # y坐标使用正常平滑
        
        smoothed_pos = np.array([
            x_smoothing * prev_position[0] + (1 - x_smoothing) * current_pos[0],
            y_smoothing * prev_position[1] + (1 - y_smoothing) * current_pos[1]
        ])
        return smoothed_pos
    else:
        return current_pos
