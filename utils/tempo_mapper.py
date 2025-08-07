import numpy as np
import time

class TempoMapper:
    def __init__(self, base_bpm=120, max_bpm=180, min_bpm=60, 
                 attack_rate=0.1, decay_rate=0.05, silence_decay_rate=0.3,
                 silence_threshold=0.05, history_length=50):
        """
        基于响度数据的BPM映射器
        
        Args:
            base_bpm: 基础BPM (120)
            max_bpm: 最大BPM (180)
            min_bpm: 最小BPM (60)
            attack_rate: 上升速率 (0.1)
            decay_rate: 下降速率 (0.05)
            silence_decay_rate: 静音时下降速率 (0.3)
            silence_threshold: 静音阈值 (0.05)
            history_length: 历史记录长度 (50)
        """
        self.base_bpm = base_bpm
        self.max_bpm = max_bpm
        self.min_bpm = min_bpm
        self.attack_rate = attack_rate
        self.decay_rate = decay_rate
        self.silence_decay_rate = silence_decay_rate
        self.silence_threshold = silence_threshold
        self.history_length = history_length
        
        # 状态变量
        self.current_bpm = base_bpm
        self.last_update_time = time.time()
        self.rms_history = []
        self.intensity_history = []
        
    def map_intensity_to_0_100(self, intensity):
        """
        将强度值映射到0-100范围，使用超高对比度映射放大通道差异
        """
        if intensity <= 0:
            return 0.0
        
        # 使用超高对比度映射函数
        # 对于很小的值，使用指数放大
        if intensity < 0.001:
            # 使用指数函数放大差异
            mapped_value = np.power(intensity * 1000, 0.25) * 25
            return min(100.0, mapped_value)
        
        # 对于小值，使用幂函数映射
        elif intensity < 0.01:
            # 使用幂函数让差异更明显
            mapped_value = np.power(intensity * 100, 0.35) * 45
            return min(100.0, mapped_value)
        
        # 对于中等值，使用分段线性映射
        elif intensity < 0.1:
            # 将0.01-0.1映射到45-85，使用分段函数
            if intensity < 0.05:
                # 0.01-0.05映射到45-65
                normalized = (intensity - 0.01) / 0.04
                mapped_value = 45 + normalized * 20
            else:
                # 0.05-0.1映射到65-85
                normalized = (intensity - 0.05) / 0.05
                mapped_value = 65 + normalized * 20
            return min(100.0, mapped_value)
        
        # 对于大值，使用超高对比度线性映射
        else:
            # 将0.1-1.0映射到85-100，让高值差异更明显
            normalized = (intensity - 0.1) / 0.9
            # 使用立方根函数让高值差异更明显
            mapped_value = 85 + (normalized ** 0.33) * 15
            return min(100.0, mapped_value)
    
    def calculate_intensity(self, rms_values):
        """
        计算声音强度指标
        基于RMS值的加权平均和变化率
        """
        if len(rms_values) == 0:
            return 0.0
        
        # 计算加权平均（前面的麦克风权重更高）
        weights = np.linspace(1.0, 0.5, len(rms_values))
        weighted_rms = np.average(rms_values, weights=weights)
        
        # 计算RMS变化率
        if len(self.rms_history) > 0:
            rms_change = abs(weighted_rms - np.mean(self.rms_history[-5:]))
        else:
            rms_change = 0.0
        
        # 综合强度指标
        intensity = weighted_rms * 0.7 + rms_change * 0.3
        
        return intensity
    
    def update_bpm(self, rms_values):
        """
        更新BPM值，同时返回映射后的响度值(0-100)
        """
        current_time = time.time()
        dt = current_time - self.last_update_time
        self.last_update_time = current_time
        
        # 计算当前强度
        intensity = self.calculate_intensity(rms_values)
        
        # 映射到0-100范围
        mapped_intensity = self.map_intensity_to_0_100(intensity)
        
        # 更新历史记录
        self.rms_history.append(np.mean(rms_values))
        self.intensity_history.append(intensity)
        
        # 保持历史记录长度
        if len(self.rms_history) > self.history_length:
            self.rms_history.pop(0)
        if len(self.intensity_history) > self.history_length:
            self.intensity_history.pop(0)
        
        # 计算目标BPM
        if intensity < self.silence_threshold:
            # 静音状态，缓慢下降到最小BPM而不是归零
            target_bpm = self.min_bpm
            decay_rate = self.silence_decay_rate
        else:
            # 根据强度计算目标BPM
            # 使用非线性映射：低强度时接近base_bpm，高强度时接近max_bpm
            intensity_normalized = min(intensity, 1.0)
            bpm_range = self.max_bpm - self.base_bpm
            target_bpm = self.base_bpm + bpm_range * (intensity_normalized ** 2)
            
            # 根据强度变化率调整
            if len(self.intensity_history) > 5:
                recent_change = np.mean(np.diff(self.intensity_history[-5:]))
                if recent_change > 0.01:  # 强度在上升
                    target_bpm *= 1.1
                elif recent_change < -0.01:  # 强度在下降
                    target_bpm *= 0.95
            
            # 限制在合理范围内
            target_bpm = max(self.min_bpm, min(self.max_bpm, target_bpm))
            decay_rate = self.decay_rate
        
        # 平滑过渡到目标BPM
        if target_bpm > self.current_bpm:
            # 上升时使用attack_rate
            self.current_bpm += (target_bpm - self.current_bpm) * self.attack_rate
        else:
            # 下降时使用decay_rate
            self.current_bpm += (target_bpm - self.current_bpm) * decay_rate
        
        return self.current_bpm, mapped_intensity
    
    def get_bpm(self):
        """获取当前BPM值"""
        return self.current_bpm
    
    def reset(self):
        """重置状态"""
        self.current_bpm = self.base_bpm
        self.rms_history = []
        self.intensity_history = []
        self.last_update_time = time.time() 