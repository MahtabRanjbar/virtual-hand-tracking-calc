# Virtual Hand-Tracking Calculator

## Overview
This project is a virtual hand-tracking calculator built using **OpenCV**, **MediaPipe**, and **Tkinter**. It tracks the position of your hands using a webcam and allows you to interact with a calculator interface by "clicking" buttons with specific hand gestures (e.g., pinching your fingers together). The calculator displays real-time input on a graphical interface, providing a fun and intuitive way to perform basic mathematical operations without physically touching any keys.

## Features
- Hand-tracking using **MediaPipe**.
- Interactive calculator with **Tkinter** for graphical display.
- Real-time video feed and gesture recognition with **OpenCV**.
- Support for basic calculator operations: addition, subtraction, multiplication, division, and more.

## Demo
![Demo GIF or Image](demo.gif)


---

## Getting Started

### Prerequisites
To run this project, you need to have Python 3.x installed along with the required dependencies. You can install these by running the following commands.

### Installation

1. **Clone the repository**:
    ```bash
    git clone https://github.com/MahtabRanjbar/virtual-hand-tracking-calc.git
    cd virtual-hand-tracking-calc
    ```

2. **Install dependencies**:
    ```bash
    pip install requirements.txt
    ```

3. **Run the project**:
    To start the virtual calculator, navigate to the directory and run:
    ```bash
    python src/app.py
    ```


---

## How It Works

### Hand-Tracking
The **hand_tracking.py** module uses MediaPipe's hand-tracking model to detect and track specific hand landmarks in the video feed. The positions of key finger tips (such as the index and middle fingers) are identified to simulate "click" events on the virtual calculator interface.

### Calculator
The **calculator.py** module is responsible for creating the calculator layout, buttons, and handling button clicks. Each button has an associated value, and the user interacts with it through the hand-tracking feature.

### Application (Tkinter GUI)
The **app.py** module handles the GUI using Tkinter. The video feed from the webcam is displayed on a Tkinter canvas, and the calculator is overlaid on top. The hand positions detected by the hand-tracking module determine the interaction with the calculator buttons, and the result is displayed in the GUI.

---

