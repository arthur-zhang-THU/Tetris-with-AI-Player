# 🎮 Tetris AI Ultimate

![Python](https://img.shields.io/badge/Python-3.x-blue.svg)
![Pygame](https://img.shields.io/badge/Library-Pygame-green.svg)
![Status](https://img.shields.io/badge/Status-Completed-success.svg)

A highly optimized Tetris game built from scratch with Python, featuring a **2-Step Lookahead AI**, **Particle System**, and **Holographic Ghost Piece**.

## ✨ Features

* **🤖 AI Auto-Pilot**: A heuristic-based AI agent capable of playing indefinitely (tested up to 500k+ score). Uses a 2-step lookahead algorithm with pruning optimizations.
* **💥 Particle Engine**: Custom-built asynchronous particle system for shatter effects without blocking the game loop.
* **👻 Holographic Ghost**: Accurate landing prediction with semi-transparent rendering.
* **⚡ Optimized Performance**: Atomic row-clearing algorithm and fuse mechanisms to ensure stable 60 FPS even at high speeds.
* **🎮 Modern Controls**: Supports SRS wall-kicks, hard drops, and hold mechanics.

## 🛠️ Installation

1.  Clone the repository:
    ```bash
    git clone [https://github.com/YOUR_USERNAME/Tetris-AI-Ultimate.git](https://github.com/YOUR_USERNAME/Tetris-AI-Ultimate.git)
    ```
2.  Install dependencies:
    ```bash
    pip install pygame numpy
    ```
3.  Run the game:
    ```bash
    python main.py
    ```

## 🎮 Controls

| Key | Action |
| :--- | :--- |
| **A** | **Toggle AI Agent (Auto-Pilot)** |
| **Arrow Keys** | Move / Rotate / Soft Drop |
| **Space** | Hard Drop |
| **ESC** | Pause / Resume |
| **R** | Restart (on Game Over) |

## 🧠 AI Algorithm

The AI uses a heuristic scoring system based on the **El-Tetris** criteria:
* **Aggregate Height**: -0.51
* **Complete Lines**: +0.76
* **Holes**: -0.36
* **Bumpiness**: -0.18

It evaluates the current board + all possible next moves (2-Step Lookahead) to choose the optimal placement.

## 📄 License

This project is open-sourced under the MIT License.