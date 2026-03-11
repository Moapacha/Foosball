# Foosball Sound Localization System

A sound-localization-based foosball table system using an 8-microphone array for real-time position estimation and goal detection. Implements a full audio processing chain from Ableton Live to VCV Rack for parameter control.

## Table of Contents

- [Features](#features)
- [System Architecture](#system-architecture)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [OSC Communication](#osc-communication)
- [Max/MSP MIDI Conversion](#maxmsp-midi-conversion)
- [VCV Rack CV Control](#vcv-rack-cv-control)
- [Troubleshooting](#troubleshooting)
- [Technical Specifications](#technical-specifications)

## Features

- **Real-time sound localization** — 6-microphone array for source position estimation
- **Goal detection** — 2 goal microphones for goal event detection
- **BPM mapping** — Real-time audio loudness mapped to BPM values
- **Dual OSC output** — Separate main status port and position estimation port
- **MIDI conversion** — Max/MSP converts OSC data to MIDI signals
- **CV control** — `midicctocv` module in VCV Rack converts 0–127 MIDI to 0–10V CV
- **Blue vs Red layout** — Supports Blue (left) vs Red (right) team configuration

## System Architecture

```
Ableton Live → BlackHole → Python → OSC → Max/MSP → MIDI → VCV Rack → CV Control
```

### Audio Processing Chain

| Stage | Description |
|-------|-------------|
| **Ableton Live** | Audio source and mixing |
| **BlackHole** | Virtual audio device, routing Ableton audio to Python |
| **Python** | Real-time audio analysis, position estimation, and OSC sending |
| **Max/MSP** | Receives OSC and converts to MIDI |
| **VCV Rack** | Receives MIDI via `midicctocv` and outputs CV signals |
| **CV Control** | 0–10V voltage controls module parameters |

## Installation

### Prerequisites

- macOS (BlackHole supported)
- Python 3.7+
- BlackHole 16ch virtual audio device
- Max/MSP
- VCV Rack

### 1. Install BlackHole

```bash
# Install BlackHole via Homebrew
brew install blackhole-2ch

# Or download from: https://github.com/ExistentialAudio/BlackHole
```

### 2. Install Python Dependencies

```bash
pip install numpy pyyaml python-osc pyaudio matplotlib
```

### 3. Configure Audio Routing

- **Ableton Live**: Set output device to BlackHole 16ch, ensure 8 channels are routed
- **BlackHole**: Create 16-channel device, set sample rate to 44100 Hz
- **Python**: Reads channels 1–8 from BlackHole

## Quick Start

### 1. Run the Main Program

```bash
python main.py
```

### 2. Start Max/MSP

1. Open the Max/MSP patch
2. Ensure OSC receivers are listening on ports **11111** and **7777**
3. Configure MIDI output to VCV Rack

### 3. Start VCV Rack

1. Open VCV Rack
2. Add the `midicctocv` module
3. Configure MIDI input
4. Connect CV outputs to target modules

### 4. Run Tests (Optional)

```bash
python simulate_audio.py     # Audio simulation test
python test_4channel.py      # System test
python verify_config.py      # Configuration verification
python visualize_layout_en.py # Layout visualization
```

## Configuration

Main configuration file: `mic_config.yaml`

### Microphone Layout

| Channel | Role | Position |
|---------|------|----------|
| 1 | Goal (Blue) | (-10, 34) |
| 2 | Goal (Red) | (127, 34) |
| 3 | Localization | (0, 0) — Blue bottom-left |
| 4 | Localization | (0, 68) — Blue top-left |
| 5 | Localization | (58.5, 0) — Center bottom |
| 6 | Localization | (58.5, 68) — Center top |
| 7 | Localization | (117, 0) — Red bottom-right |
| 8 | Localization | (117, 68) — Red top-right |

### Coordinate System

- Origin: bottom-left (0, 0)
- Extent: top-right (117, 68)
- Layout: Blue (left) vs Red (right)
- Mapping: Raw coordinates map to -1…1 for Spat Revolution

### Layout Reference

- **Blue area**: x &lt; 58.5
- **Red area**: x &gt; 58.5
- **Center line**: x = 58.5

## OSC Communication

### Main Status Port (11111)

- **Address**: `/foosball_status`
- **Format**: `[mapped_intensity1–6, x, y, goal_left, goal_right, bpm]`
- **Contents**: 6-channel mapped loudness (0–127), position (x, y), goal flags (0/127), BPM

### Position Estimation Port (7777)

- **Address**: `/source/1/xyz`
- **Format**: `[x_mapped, y_mapped, 0.0]`
- **Contents**: Position mapped to -1…1 (Spat Revolution–compatible)

## Max/MSP MIDI Conversion

Max/MSP receives OSC and maps to MIDI:

- **OSC ports**: 11111 (main), 7777 (position)
- **Position**: X/Y → MIDI CC
- **Loudness**: 6 channels → 6 MIDI CCs
- **Goals**: Goal events → MIDI Note
- **BPM**: BPM → MIDI CC

## VCV Rack CV Control

`midicctocv` module:

- **Input**: MIDI CC (0–127)
- **Output**: CV (0–10V)
- **Mapping**: Linear 0–127 → 0–10V

### Example CC → CV Mappings

| Parameter | MIDI CC | Application |
|-----------|---------|-------------|
| X position | 1 | Spatial position X |
| Y position | 2 | Spatial position Y |
| Channel 1 loudness | 10 | Filter cutoff |
| Channel 2 loudness | 11 | Reverb amount |
| … | 12–15 | Delay, distortion, compression, modulation |
| Goal event | Note | Gate / trigger |
| BPM | 16 | Tempo / clock |

## Troubleshooting

### BlackHole Not Detected

- Confirm BlackHole is installed
- Check audio device permissions

### OSC Connection Fails

- Ensure ports 11111 and 7777 are free
- Verify Max/MSP is listening

### MIDI Connection Issues

- Check MIDI device setup
- Verify VCV Rack MIDI input configuration

### CV Signal Problems

- Review `midicctocv` configuration
- Confirm MIDI CC mapping

### Debug Commands

```bash
# List audio devices
python -c "import pyaudio; p = pyaudio.PyAudio(); print([p.get_device_info_by_index(i)['name'] for i in range(p.get_device_count())])"

# Test OSC send
python -c "from pythonosc import udp_client; c = udp_client.SimpleUDPClient('127.0.0.1', 11111); c.send_message('/test', [1, 2, 3])"
```

## Technical Specifications

| Spec | Value |
|------|-------|
| Sample rate | 44100 Hz |
| Processing latency | &lt; 100 ms |
| Position accuracy | ±2 cm |
| OSC rate | 10 Hz |
| MIDI resolution | 0–127 |
| CV range | 0–10V |
| Input channels | 8 (on 16-channel device) |

## Notes

- BlackHole 16ch must be receiving audio from Ableton
- Max/MSP must listen on 11111 (status) and 7777 (position)
- Goal mics: channels 1–2; localization mics: channels 3–8
- `midicctocv` converts 0–127 MIDI to 0–10V CV in VCV Rack
