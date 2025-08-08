import numpy as np
import time

class TempoMapper:
    def __init__(self, base_bpm=120, max_bpm=180, min_bpm=60, 
                 attack_rate=0.15, decay_rate=0.08, silence_decay_rate=0.2,
                 silence_threshold=0.05, history_length=50):
        """
        基于响度数据的BPM映射器
        
        Args:
            base_bpm: 基础BPM (120)
            max_bpm: 最大BPM (180)
            min_bpm: 最小BPM (60)
            attack_rate: 上升速率 (0.15) - 更快的响应
            decay_rate: 下降速率 (0.08) - 更快的响应
            silence_decay_rate: 静音时下降速率 (0.2) - 更快的响应
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
        
    def map_intensity_to_minus10_10(self, intensity):
        """
        将强度值映射到-10到10范围，基准值提升到0左右，对很小信号也有响应
        """
        if intensity <= 0:
            return 0.0
        
        # 提升基准值，让整体响度在0左右，对很小信号也有响应
        # 对于很小的值，映射到0到2
        if intensity < 0.001:
            # 使用指数函数放大差异，映射到0到2
            mapped_value = np.power(intensity * 1000, 0.25) * 2
            return max(-10.0, min(10.0, mapped_value))
        
        # 对于小值，使用幂函数映射到0到4
        elif intensity < 0.01:
            # 使用幂函数让差异更明显，映射到0到4
            mapped_value = np.power(intensity * 100, 0.35) * 4
            return max(-10.0, min(10.0, mapped_value))
        
        # 对于中等值，使用分段线性映射到0到7
        elif intensity < 0.1:
            # 将0.01-0.1映射到0到7，使用分段函数
            if intensity < 0.05:
                # 0.01-0.05映射到0到3.5
                normalized = (intensity - 0.01) / 0.04
                mapped_value = normalized * 3.5
            else:
                # 0.05-0.1映射到3.5到7
                normalized = (intensity - 0.05) / 0.05
                mapped_value = 3.5 + normalized * 3.5
            return max(-10.0, min(10.0, mapped_value))
        
        # 对于大值，使用更极端的映射产生大幅跳动
        else:
            # 使用更极端的映射函数，让高值也有大幅差异
            # 将0.1-100映射到7-10，使用更激进的函数
            if intensity < 1.0:
                # 0.1-1.0映射到7-10，使用指数函数
                normalized = (intensity - 0.1) / 0.9
                mapped_value = 7 + (normalized ** 0.5) * 3
            elif intensity < 10.0:
                # 1.0-10.0映射到10 (保持高值)
                mapped_value = 10.0
            elif intensity < 50.0:
                # 10.0-50.0映射到10 (保持高值)
                mapped_value = 10.0
            else:
                # 50.0+映射到10
                mapped_value = 10.0
            
            return max(-10.0, min(10.0, mapped_value))
    
    def map_intensity_to_0_100(self, intensity):
        """
        将强度值映射到0-100范围，基准值提升到50左右
        """
        if intensity <= 0:
            return 50.0  # 静音时返回50而不是0
        
        # 提升基准值，让整体响度在50左右
        # 对于很小的值，映射到40到50
        if intensity < 0.001:
            # 使用指数函数放大差异
            mapped_value = 40 + np.power(intensity * 1000, 0.25) * 10
            return min(100.0, mapped_value)
        
        # 对于小值，使用幂函数映射到40到60
        elif intensity < 0.01:
            # 使用幂函数让差异更明显
            mapped_value = 40 + np.power(intensity * 100, 0.35) * 20
            return min(100.0, mapped_value)
        
        # 对于中等值，使用分段线性映射到40到90
        elif intensity < 0.1:
            # 将0.01-0.1映射到40-90，使用分段函数
            if intensity < 0.05:
                # 0.01-0.05映射到40-65
                normalized = (intensity - 0.01) / 0.04
                mapped_value = 40 + normalized * 25
            else:
                # 0.05-0.1映射到65-90
                normalized = (intensity - 0.05) / 0.05
                mapped_value = 65 + normalized * 25
            return min(100.0, mapped_value)
        
        # 对于大值，使用更极端的映射产生大幅跳动
        else:
            # 使用更极端的映射函数，让高值也有大幅差异
            # 将0.1-100映射到90-100，使用更激进的函数
            if intensity < 1.0:
                # 0.1-1.0映射到90-100，使用指数函数
                normalized = (intensity - 0.1) / 0.9
                mapped_value = 90 + (normalized ** 0.5) * 10
            elif intensity < 10.0:
                # 1.0-10.0映射到100-100 (保持高值)
                mapped_value = 100.0
            elif intensity < 50.0:
                # 10.0-50.0映射到100-100 (保持高值)
                mapped_value = 100.0
            else:
                # 50.0+映射到100
                mapped_value = 100.0
            
            return min(100.0, mapped_value)
    
    def map_intensity_to_0_127(self, intensity):
        """
        将强度值映射到0-127范围，大幅增加轨道间差异
        """
        if intensity <= 0:
            return 0
        
        # 大幅增加轨道间差异，使用更敏感的分段映射
        # 对于很小的值，映射到0到60
        if intensity < 0.001:
            # 使用指数函数放大差异，映射到0到60
            mapped_value = np.power(intensity * 1000, 0.25) * 60
            return min(127, int(mapped_value))
        
        # 对于小值，使用幂函数映射到0到100
        elif intensity < 0.01:
            # 使用幂函数让差异更明显，映射到0到100
            mapped_value = np.power(intensity * 100, 0.35) * 100
            return min(127, int(mapped_value))
        
        # 对于中等值，使用分段线性映射到0到127
        elif intensity < 0.1:
            # 将0.01-0.1映射到0到127，使用分段函数
            if intensity < 0.05:
                # 0.01-0.05映射到0到80
                normalized = (intensity - 0.01) / 0.04
                mapped_value = normalized * 80
            else:
                # 0.05-0.1映射到80到127
                normalized = (intensity - 0.05) / 0.05
                mapped_value = 80 + normalized * 47
            return min(127, int(mapped_value))
        
        # 对于大值，使用更极端的映射产生大幅跳动
        else:
            # 使用更极端的映射函数，让高值也有大幅差异
            # 将0.1-100映射到127，使用更激进的函数
            if intensity < 1.0:
                # 0.1-1.0映射到127
                mapped_value = 127
            elif intensity < 10.0:
                # 1.0-10.0映射到127 (保持高值)
                mapped_value = 127
            elif intensity < 50.0:
                # 10.0-50.0映射到127 (保持高值)
                mapped_value = 127
            else:
                # 50.0+映射到127
                mapped_value = 127
            
            return min(127, int(mapped_value))
    
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
        
        # 映射到-10到10范围
        mapped_intensity = self.map_intensity_to_minus10_10(intensity)
        
        # 更新历史记录
        self.rms_history.append(np.mean(rms_values))
        self.intensity_history.append(intensity)
        
        # 保持历史记录长度
        if len(self.rms_history) > self.history_length:
            self.rms_history.pop(0)
        if len(self.intensity_history) > self.history_length:
            self.intensity_history.pop(0)
        
        # 计算目标BPM - 让变化更明显
        if intensity < self.silence_threshold:
            # 静音状态，快速下降到接近min_bpm
            target_bpm = self.min_bpm + (self.base_bpm - self.min_bpm) * 0.3  # 降到78而不是114
            decay_rate = self.silence_decay_rate
        else:
            # 根据强度计算目标BPM，让变化更明显
            intensity_normalized = min(intensity, 1.0)
            
            # 使用更激进的映射，让BPM变化更明显
            if intensity_normalized < 0.2:
                # 低强度时，在min_bpm到base_bpm之间变化
                bpm_range = self.base_bpm - self.min_bpm
                target_bpm = self.min_bpm + bpm_range * (intensity_normalized / 0.2) * 0.8
            elif intensity_normalized < 0.6:
                # 中等强度时，在base_bpm到max_bpm之间变化
                bpm_range = self.max_bpm - self.base_bpm
                normalized = (intensity_normalized - 0.2) / 0.4
                target_bpm = self.base_bpm + bpm_range * normalized * 0.8
            else:
                # 高强度时，接近max_bpm
                bpm_range = self.max_bpm - self.base_bpm
                normalized = (intensity_normalized - 0.6) / 0.4
                target_bpm = self.base_bpm + bpm_range * (0.8 + normalized * 0.2)
            
            # 根据强度变化率调整，让变化更明显
            if len(self.intensity_history) > 3:
                recent_change = np.mean(np.diff(self.intensity_history[-3:]))
                if recent_change > 0.005:  # 强度在上升
                    target_bpm *= 1.05  # 更明显的上升
                elif recent_change < -0.005:  # 强度在下降
                    target_bpm *= 0.95  # 更明显的下降
            
            # 限制在合理范围内
            target_bpm = max(self.min_bpm, min(self.max_bpm, target_bpm))
            decay_rate = self.decay_rate
        
        # 平滑过渡到目标BPM，但响应更快
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