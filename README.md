# Gear4Skills AI Analyzer

An open-source AI tool using MediaPipe and computer vision to analyze badminton performance in real time. Built for under-resourced athletes.

## Features
- Real-time pose tracking using MediaPipe
- Classifies shots as offensive, defensive, or neutral
- Assesses shot quality, pressure, and movement
- Detects forehand/backhand handle use
- Gives live feedback for training

## Demo Video
[![Watch the demo](https://img.youtube.com/vi/MVhTiAEi5oI/0.jpg)](https://youtu.be/MVhTiAEi5oI)

## 💡 How It Works
- Uses OpenCV + MediaPipe for real-time pose detection
- Triggers PyAutoGUI actions based on movement
- Categorizes badminton actions using a basic classifier

## Getting Started
```bash
git clone https://github.com/TheBestGuy345/gear4skills-ai-analyzer.git
cd gear4skills-ai-analyzer
pip install -r requirements.txt
python main.py
