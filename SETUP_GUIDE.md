# Foosball 声音定位系统 - 完整设置指南

## 系统概述

这个系统通过分析来自BlackHole音频设备的输入，计算声音位置，并通过OSC协议将位置信息发送到VCV Rack。

## 1. 系统要求

### 软件依赖
- Python 3.7+
- VCV Rack
- BlackHole 16ch (音频虚拟设备，推荐) 或 BlackHole 2ch

### Python包
```bash
pip install sounddevice python-osc pyyaml numpy
```

## 2. 音频设备配置

### BlackHole设置
1. 确保BlackHole 16ch已安装并启用（推荐使用16通道版本）
2. 在系统音频设置中将BlackHole设为输入设备
3. 将音频源（如音乐播放器）输出到BlackHole
4. 如果使用BlackHole 2ch，请相应调整配置文件中的通道数

### 测试音频输入
```bash
# 测试 BlackHole 16ch 设备
python test_blackhole_16ch.py

# 运行主程序
python main.py
```
应该看到类似输出：
```
响度: [0.123 0.456 0.789 ...], 估计位置: [45.2  12.3]
```

## 3. VCV Rack配置

### 步骤1：启动VCV Rack
1. 打开VCV Rack
2. 创建新补丁

### 步骤2：添加OSC模块
1. 在模块浏览器中找到OSC-1模块
2. 拖拽到补丁中
3. 设置参数：
   - **Port**: 7000
   - **Address**: /position

### 步骤3：连接模块
```
OSC-1 → MIDI-CC → 你的音频处理模块
```

## 4. 测试流程

### 测试OSC连接
```bash
python test_osc.py
```
这个脚本会发送测试位置数据到VCV Rack。

### 测试完整系统
1. 启动VCV Rack并配置OSC接收
2. 运行主程序：`python main.py`
3. 播放音频到BlackHole设备
4. 观察VCV Rack中的数值变化

## 5. 配置文件说明

### mic_config.yaml
```yaml
# 麦克风位置配置
mics:
  - id: 0
    position: [0, 0]        # 左上角
  - id: 1
    position: [117, 0]      # 右上角

# 音频设备配置
device_id: 0                # BlackHole设备ID
sample_rate: 44100
channels: 2
chunk_duration: 0.1

# OSC配置
osc:
  ip: "127.0.0.1"
  port: 7000
  address: "/position"
```

## 6. 故障排除

### 常见问题

**Q: 程序显示"响度: [0. 0.]"**
A: 检查BlackHole是否正在接收音频，确认音频源已连接到BlackHole

**Q: VCV Rack收不到OSC数据**
A: 
1. 确认VCV Rack监听端口7000
2. 检查防火墙设置
3. 运行`python test_osc.py`测试OSC连接

**Q: 音频设备错误**
A: 
1. 检查`device_id`是否正确
2. 运行`python -c "import sounddevice as sd; print(sd.query_devices())"`查看可用设备

## 7. 高级配置

### 添加更多麦克风
如果需要更多输入通道，可以：
1. 配置Aggregate Device
2. 修改`mic_config.yaml`添加更多麦克风位置
3. 更新`channels`参数

### 自定义OSC地址
修改`mic_config.yaml`中的`osc.address`字段来改变OSC地址。

## 8. 性能优化

- 调整`chunk_duration`来平衡延迟和CPU使用
- 使用更低的采样率来减少计算量
- 考虑使用多线程处理音频和OSC发送 