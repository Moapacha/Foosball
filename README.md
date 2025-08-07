# Foosball 声音定位系统

一个基于声音定位的桌面足球游戏系统，使用多个麦克风阵列进行实时位置估计和进球检测。

## 功能特点

- **实时声音定位**: 使用6个麦克风阵列进行声源位置估计
- **进球检测**: 使用2个球门麦克风检测进球事件
- **BPM映射**: 实时计算和映射音频响度到BPM值
- **双OSC输出**: 支持独立的主状态端口和位置估计端口
- **模拟测试**: 提供完整的音频模拟测试功能

## OSC通信配置

系统支持双OSC端口输出：

### 主状态端口 (11111)
- **OSC地址**: `/foosball_status`
- **数据格式**: `[rms1, rms2, rms3, rms4, rms5, rms6, x, y, goal_left, goal_right, bpm]`
- **说明**: 包含所有通道的RMS值、位置坐标、进球检测状态和BPM值

### 位置估计端口 (11112)
- **OSC地址**: `/position`
- **数据格式**: `[x, y]`
- **说明**: 仅包含位置估计的x, y坐标值

## 配置文件

主要配置文件为 `mic_config.yaml`，包含：

- 麦克风位置坐标
- 音频设备配置
- OSC通信配置
- 位置估计独立OSC配置

## 使用方法

### 1. 运行主程序
```bash
python main.py
```

### 2. 运行模拟测试
```bash
python simulate_audio.py
```

### 3. 测试双OSC端口
```bash
python test_dual_osc.py
```

## 系统要求

- Python 3.7+
- BlackHole 16ch 音频设备
- Max/MSP 或其他OSC接收软件

## 依赖包

- numpy
- pyyaml
- python-osc
- pyaudio

## 安装依赖

```bash
pip install numpy pyyaml python-osc pyaudio
```

## 注意事项

1. 确保BlackHole 16ch设备正在接收音频
2. Max/MSP需要监听两个端口：
   - 端口11111 (主状态)
   - 端口11112 (位置估计)
3. 终端输出样式保持不变，但OSC数据会发送到两个不同的端口