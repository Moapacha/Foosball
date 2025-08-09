# Foosball 声音定位系统

一个基于声音定位的桌面足球游戏系统，使用8个麦克风阵列进行实时位置估计和进球检测，通过完整的音频处理链从Ableton Live到VCV Rack实现参数控制。

## 系统架构

```
Ableton Live → BlackHole → Python → OSC → Max/MSP → MIDI → VCV Rack → CV控制
```

### 完整音频处理链

1. **Ableton Live**: 音频源和混音
2. **BlackHole**: 虚拟音频设备，将Ableton音频路由到Python
3. **Python**: 实时音频分析、位置估计和OSC发送
4. **Max/MSP**: 接收OSC数据并转换为MIDI
5. **VCV Rack**: 接收MIDI并通过midicctocv模块转换为CV信号
6. **CV控制**: 0-10V电压控制模块参数

## 功能特点

- **实时声音定位**: 使用6个麦克风阵列进行声源位置估计
- **进球检测**: 使用2个球门麦克风检测进球事件
- **BPM映射**: 实时计算和映射音频响度到BPM值
- **-10到10映射**: 将音频强度映射到-10到10范围，确保变化幅度明显
- **双OSC输出**: 支持独立的主状态端口和位置估计端口
- **MIDI转换**: Max/MSP将OSC数据转换为MIDI信号
- **CV控制**: VCV Rack中的midicctocv模块将0-127 MIDI转换为0-10V CV
- **模拟测试**: 提供完整的音频模拟测试功能
- **蓝方vs红方**: 支持蓝方(左) vs 红方(右)的对战布局

## 麦克风配置

系统使用8个麦克风：
- **球门麦克风** (通道1-2): 进球检测
  - 通道1: 左门 (-10, 34) - 蓝方球门
  - 通道2: 右门 (127, 34) - 红方球门
- **定位麦克风** (通道3-8): 桌面位置估计
  - 通道3: 左下 (0, 0) - 蓝方
  - 通道4: 左上 (0, 68) - 蓝方
  - 通道5: 中下 (58.5, 0)
  - 通道6: 中上 (58.5, 68)
  - 通道7: 右下 (117, 0) - 红方
  - 通道8: 右上 (117, 68) - 红方

## 坐标系

- **坐标系**: 左下(0,0), 右上(117,68)
- **布局**: 蓝方(左) vs 红方(右)
- **映射**: 原始坐标映射到Spat Revolution的-1到1范围

## OSC通信配置

系统支持双OSC端口输出：

### 主状态端口 (11111)
- **OSC地址**: `/foosball_status`
- **数据格式**: `[mapped_intensity1, mapped_intensity2, mapped_intensity3, mapped_intensity4, mapped_intensity5, mapped_intensity6, x, y, goal_left, goal_right, bpm]`
- **说明**: 包含6个通道的映射响度值(0-127)、位置坐标、进球检测状态(0/127)和BPM值

### 位置估计端口 (7777)
- **OSC地址**: `/source/1/xyz`
- **数据格式**: `[x_mapped, y_mapped, 0.0]`
- **说明**: 位置坐标映射到-1到1范围，适用于Spat Revolution

## Max/MSP MIDI转换

Max/MSP接收OSC数据并转换为MIDI信号：

### OSC接收配置
- **主状态端口**: 11111
- **位置估计端口**: 7777
- **MIDI输出**: 发送到VCV Rack

### MIDI数据映射
- **位置坐标**: X/Y坐标映射到MIDI CC
- **响度值**: 6个通道响度映射到不同MIDI CC
- **进球检测**: 进球事件触发MIDI Note
- **BPM值**: BPM映射到MIDI CC

## VCV Rack CV控制

VCV Rack接收MIDI并通过midicctocv模块转换为CV信号：

### midicctocv模块配置
- **输入**: MIDI CC信号 (0-127)
- **输出**: CV电压信号 (0-10V)
- **映射**: 线性映射0-127到0-10V

### CV控制参数
- **位置控制**: X/Y坐标控制空间位置
- **响度控制**: 6个通道响度控制不同参数
- **进球触发**: 进球事件触发门限信号
- **BPM控制**: BPM值控制节奏相关参数

## 配置文件

主要配置文件为 `mic_config.yaml`，包含：

- 麦克风位置坐标（8个麦克风）
- 音频设备配置
- OSC通信配置
- 位置估计独立OSC配置

## 安装和设置

### 1. 系统要求

- macOS (支持BlackHole)
- Python 3.7+
- BlackHole 16ch 音频设备
- Max/MSP
- VCV Rack

### 2. 安装BlackHole

```bash
# 使用Homebrew安装BlackHole
brew install blackhole-2ch

# 或下载最新版本
# https://github.com/ExistentialAudio/BlackHole
```

### 3. 配置音频路由

1. **Ableton Live设置**:
   - 输出设备选择: BlackHole 16ch
   - 确保8个通道正确路由

2. **BlackHole配置**:
   - 创建16通道设备
   - 设置采样率为44100Hz

3. **Python音频输入**:
   - 从BlackHole读取音频
   - 处理通道1-8

### 4. 安装Python依赖

```bash
pip install numpy pyyaml python-osc pyaudio matplotlib
```

### 5. Max/MSP设置

1. **OSC接收**:
   - 监听端口11111 (主状态)
   - 监听端口7777 (位置估计)

2. **MIDI输出**:
   - 配置MIDI输出到VCV Rack
   - 设置MIDI CC映射

### 6. VCV Rack设置

1. **MIDI输入**:
   - 配置MIDI输入设备
   - 接收来自Max/MSP的MIDI

2. **midicctocv模块**:
   - 添加midicctocv模块
   - 配置CC到CV映射

## 使用方法

### 1. 启动音频路由

```bash
# 启动Python主程序
python main.py
```

### 2. 启动Max/MSP

1. 打开Max/MSP补丁
2. 确保OSC接收器正在监听
3. 配置MIDI输出到VCV Rack

### 3. 启动VCV Rack

1. 打开VCV Rack
2. 添加midicctocv模块
3. 配置MIDI输入
4. 连接CV输出到目标模块

### 4. 运行模拟测试

```bash
# 运行音频模拟测试
python simulate_audio.py

# 运行系统测试
python test_4channel.py

# 测试新布局
python verify_config.py

# 可视化布局
python visualize_layout_en.py
```

## 音频处理流程详解

### 1. Ableton Live → BlackHole
- Ableton输出8通道音频到BlackHole
- 通道1-2: 球门麦克风
- 通道3-8: 定位麦克风

### 2. BlackHole → Python
- Python从BlackHole读取16通道音频
- 处理通道1-8的数据
- 实时计算RMS值和位置估计

### 3. Python → OSC
- 发送主状态数据到端口11111
- 发送位置估计数据到端口7777
- 数据包含响度、位置、进球检测、BPM

### 4. OSC → Max/MSP
- Max/MSP接收OSC数据
- 将数据转换为MIDI CC信号
- 发送MIDI到VCV Rack

### 5. MIDI → VCV Rack
- VCV Rack接收MIDI信号
- midicctocv模块将0-127 MIDI转换为0-10V CV
- CV信号控制模块参数

## 参数映射示例

### 位置控制
- **X坐标**: MIDI CC 1 → CV 0-10V → 空间位置X
- **Y坐标**: MIDI CC 2 → CV 0-10V → 空间位置Y

### 响度控制
- **通道1响度**: MIDI CC 10 → CV 0-10V → 滤波器频率
- **通道2响度**: MIDI CC 11 → CV 0-10V → 混响量
- **通道3响度**: MIDI CC 12 → CV 0-10V → 延迟时间
- **通道4响度**: MIDI CC 13 → CV 0-10V → 失真量
- **通道5响度**: MIDI CC 14 → CV 0-10V → 压缩比
- **通道6响度**: MIDI CC 15 → CV 0-10V → 调制深度

### 事件控制
- **进球检测**: MIDI Note → Gate信号 → 触发效果
- **BPM值**: MIDI CC 16 → CV 0-10V → 时钟速度

## 故障排除

### 常见问题

1. **BlackHole未检测到**:
   - 检查BlackHole安装
   - 确认音频设备权限

2. **OSC连接失败**:
   - 检查端口11111和7777是否被占用
   - 确认Max/MSP正在监听

3. **MIDI连接问题**:
   - 检查MIDI设备配置
   - 确认VCV Rack MIDI输入设置

4. **CV信号异常**:
   - 检查midicctocv模块配置
   - 确认MIDI CC映射正确

### 调试命令

```bash
# 检查音频设备
python -c "import pyaudio; p = pyaudio.PyAudio(); print([p.get_device_info_by_index(i)['name'] for i in range(p.get_device_count())])"

# 测试OSC发送
python -c "from pythonosc import udp_client; client = udp_client.SimpleUDPClient('127.0.0.1', 11111); client.send_message('/test', [1, 2, 3])"
```

## 注意事项

1. 确保BlackHole 16ch设备正在接收音频
2. Max/MSP需要监听两个端口：11111 (主状态) 和 7777 (位置估计)
3. 系统使用6个定位麦克风进行位置估计，2个球门麦克风进行进球检测
4. 球门麦克风从BlackHole的通道1-2输入，定位麦克风从通道3-8输入
5. 新布局支持蓝方(左) vs 红方(右)的对战模式
6. 坐标系已重新规整：左下(0,0), 右上(117,68)
7. VCV Rack中的midicctocv模块确保0-127 MIDI正确转换为0-10V CV

## 布局说明

- **蓝方区域**: 左侧 (x < 58.5)
- **红方区域**: 右侧 (x > 58.5)
- **中场线**: x = 58.5
- **球门位置**: 左门(-10,34), 右门(127,34)
- **通道映射**: 1左门, 2右门, 3左下, 4左上, 5中下, 6中上, 7右下, 8右上

## 技术规格

- **音频采样率**: 44100Hz
- **处理延迟**: < 100ms
- **位置精度**: ±2cm
- **OSC频率**: 10Hz
- **MIDI分辨率**: 0-127
- **CV范围**: 0-10V
- **支持通道**: 8通道输入，16通道设备