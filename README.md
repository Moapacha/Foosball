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

Requires: macOS, Python 3.7+, BlackHole 16ch, Max/MSP, VCV Rack

```bash
pip install numpy pyyaml python-osc pyaudio matplotlib
```

Route Ableton output to BlackHole 16ch (8 channels). Edit `mic_config.yaml` for your setup.

## Quick Start

```bash
python main.py
```

Then run Max/MSP (OSC ports 11111, 7777 → MIDI) and VCV Rack with `midicctocv`.

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

Bottom-left (0, 0) to top-right (117, 68). Blue (x &lt; 58.5) vs Red (x &gt; 58.5).

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

- **BlackHole**: Check install and audio device permissions
- **OSC**: Ports 11111 and 7777 must be free; Max/MSP must be listening
- **MIDI/CV**: Verify VCV Rack input and `midicctocv` mapping