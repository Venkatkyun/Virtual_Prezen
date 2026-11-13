# Virtual Presentation Controller PRO

A Python-based virtual presentation controller that allows users to control presentations and interact with their computer using real-time hand gestures.

Built using Computer Vision and MediaPipe, this project eliminates the need for a physical presentation remote or keyboard during presentations.

## Features

- **Cursor Control:** Move the mouse cursor using your index finger.
- **Gesture Click:** Perform a pinch gesture to simulate a mouse click.
- **Next Slide:** Use two fingers to navigate to the next slide.
- **Previous Slide:** Use three fingers to navigate to the previous slide.
- **Start Slideshow:** Show four fingers to start a slideshow.
- **Exit Slideshow:** Make a fist to exit the slideshow.
- **Zoom In:** Use your pinky finger.
- **Zoom Out:** Use your ring and pinky fingers.
- **Gesture Stabilization:** Uses frame-based gesture recognition and cooldown mechanisms to reduce accidental actions.
- **GUI Interface:** Provides a graphical interface to start, stop, and manage the controller.

## Technologies Used

- Python
- OpenCV
- MediaPipe
- PyAutoGUI
- CustomTkinter

## Gesture Controls

| Hand Gesture | Action |
|---|---|
| Index finger | Cursor movement |
| Pinch | Mouse click |
| Two fingers | Next slide |
| Three fingers | Previous slide |
| Four fingers | Start slideshow |
| Fist | Exit slideshow |
| Pinky only | Zoom in |
| Ring + Pinky | Zoom out |

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/Virtual-Presentation-Controller.git
```

### 2. Navigate to the project directory

```bash
cd Virtual-Presentation-Controller
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the application

```bash
python main.py
```

## How It Works

The application captures live video through a webcam and processes each frame using MediaPipe Hands to identify hand landmarks.

Based on the positions of the detected landmarks, the application identifies specific hand gestures and maps them to computer actions using PyAutoGUI.

A CustomTkinter graphical interface provides controls for starting and stopping the camera.

## Requirements

- Python
- Webcam
- Windows/Linux/macOS
- Required Python dependencies

## Future Improvements

- Add more customizable gestures.
- Improve cursor movement accuracy.
- Add support for additional presentation software.
- Introduce gesture sensitivity settings.

## Author

Venkat
