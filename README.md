# Team Visionx 🤟 – Smart Navigation & Object Detection Assistant

**Empowering the Visually Impaired through AI-Driven Spatial Awareness.**

---

## 📖 Table of Contents
* [Overview](#overview)
* [Key Features](#key-features)
* [How It Works](#how-it-works)
* [Installation](#installation)
* [Deployment](#deployment)
* [Configuration](#configuration)
* [License](#license)

---

## 🔍 Overview
**Team Visionx** is an assistive technology application designed to provide real-time spatial awareness for the visually impaired. Built using **Streamlit** and **YOLOv8**, the app acts as a "digital eye," identifying objects in the environment and translating their position into actionable voice instructions.

The project moves beyond simple labeling—it calculates the proximity and orientation of objects to guide users safely around obstacles.

---

## ✨ Key Features
* **Smart Navigation Brain**: Logic-based pathfinding that tells users to "Move Left," "Move Right," or "Stop" based on object position.
* **Danger Prioritization**: High-risk items (knives, fire, vehicles) are announced with higher priority than static objects.
* **Triple Input Support**: Process live data via **Webcam**, or analyze pre-recorded **Images** and **Videos**.
* **Voice Feedback System**: Integrated speech synthesis with a smart cooldown to prevent overlapping audio.
* **Interactive Dashboard**: Real-time confidence sliders and a user-friendly sidebar for navigation settings.

---

## 🧠 How It Works (The Logic)
The app divides the visual field into three distinct zones to help the user navigate:
1. **Left Zone**: (0% - 33% of frame width)
2. **Center Zone**: (33% - 66% of frame width) - *Triggers critical stop commands.*
3. **Right Zone**: (66% - 100% of frame width)



**Priority Levels:**
- **Level 1 (Danger):** Weapons, Fire, Sharp objects.
- **Level 2 (Moving):** People, Cars, Bicycles.
- **Level 3 (Static):** Chairs, Tables, Doors.

---

**Team Visionx 💙 – Seeing the world differently, one frame at a time.**
