import cv2
import mediapipe as mp
import pyautogui
import customtkinter as ctk
import threading
import time
import math

# ---------------- SETTINGS ----------------
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

pyautogui.FAILSAFE = False   # no exception when cursor touches a screen corner
pyautogui.PAUSE = 0          # no built-in delay after each pyautogui call

screen_w, screen_h = pyautogui.size()

MARGIN = 0.15          # inner box of the camera view mapped to the full screen
SMOOTHING = 5          # higher = smoother but slower cursor
HOLD_FRAMES = 8        # a gesture must be held this many frames before it fires
PINCH_CLICK = 0.25     # normalized pinch distance that counts as a click
COOLDOWN = {           # seconds between repeated actions
    "next": 1.0, "prev": 1.0, "start": 1.5, "exit": 1.5,
    "click": 0.6, "zoom_in": 0.5, "zoom_out": 0.5,
}

running = False
last_action_time = {}

mp_hands = mp.solutions.hands
draw = mp.solutions.drawing_utils


# ---------------- HELPERS ----------------
def fingers_up(hand):
    """Returns [index, middle, ring, pinky] -> 1 if up, 0 if down."""
    tips = [8, 12, 16, 20]
    return [1 if hand.landmark[t].y < hand.landmark[t - 2].y else 0 for t in tips]


def ready(name):
    """Cooldown check (replaces time.sleep so the video never freezes)."""
    now = time.time()
    if now - last_action_time.get(name, 0) > COOLDOWN[name]:
        last_action_time[name] = now
        return True
    return False


# ---------------- MAIN CAMERA LOOP ----------------
def start_camera():
    global running

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("ERROR: Could not open camera.")
        running = False
        return

    hands = mp_hands.Hands(
        max_num_hands=1,
        min_detection_confidence=0.75,
        min_tracking_confidence=0.75,
    )

    prev_time = 0
    cur_x, cur_y = pyautogui.position()
    prev_gesture = None
    stable = 0

    try:
        while running:
            ret, frame = cap.read()
            if not ret:
                continue

            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = hands.process(rgb)

            gesture_text = "No Hand"
            gesture = None

            if result.multi_hand_landmarks:
                hand = result.multi_hand_landmarks[0]
                draw.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)
                lm = hand.landmark

                fingers = fingers_up(hand)

                # Hand size (wrist -> middle finger base) used to normalize distances
                hand_size = math.hypot(lm[0].x - lm[9].x, lm[0].y - lm[9].y) + 1e-6
                pinch = math.hypot(lm[8].x - lm[4].x, lm[8].y - lm[4].y) / hand_size

                # Identify gesture
                if fingers == [1, 0, 0, 0]:
                    gesture = "cursor"
                elif fingers == [1, 1, 0, 0]:
                    gesture = "next"
                elif fingers == [1, 1, 1, 0]:
                    gesture = "prev"
                elif fingers == [1, 1, 1, 1]:
                    gesture = "start"
                elif fingers == [0, 0, 0, 0]:
                    gesture = "exit"
                elif fingers == [0, 0, 0, 1]:
                    gesture = "zoom_in"
                elif fingers == [0, 0, 1, 1]:
                    gesture = "zoom_out"

                # Count how long the same gesture is held
                if gesture == prev_gesture:
                    stable += 1
                else:
                    stable = 0
                    prev_gesture = gesture

                # ---- Cursor move + pinch click ----
                if gesture == "cursor":
                    gesture_text = "Cursor Move"

                    if pinch < PINCH_CLICK:
                        gesture_text = "Click"
                        if stable >= 3 and ready("click"):
                            pyautogui.click()
                    else:
                        # map inner box of camera to full screen
                        nx = (lm[8].x - MARGIN) / (1 - 2 * MARGIN)
                        ny = (lm[8].y - MARGIN) / (1 - 2 * MARGIN)
                        sx = max(0, min(screen_w - 1, nx * screen_w))
                        sy = max(0, min(screen_h - 1, ny * screen_h))

                        # smoothing
                        cur_x += (sx - cur_x) / SMOOTHING
                        cur_y += (sy - cur_y) / SMOOTHING
                        pyautogui.moveTo(cur_x, cur_y)

                # ---- Discrete actions (must be held for HOLD_FRAMES) ----
                elif gesture == "next":
                    gesture_text = "Next Slide"
                    if stable >= HOLD_FRAMES and ready("next"):
                        pyautogui.press("right")

                elif gesture == "prev":
                    gesture_text = "Previous Slide"
                    if stable >= HOLD_FRAMES and ready("prev"):
                        pyautogui.press("left")

                elif gesture == "start":
                    gesture_text = "Start Slide Show"
                    if stable >= HOLD_FRAMES and ready("start"):
                        pyautogui.press("f5")

                elif gesture == "exit":
                    gesture_text = "Exit Slide Show (hold)"
                    if stable >= HOLD_FRAMES * 2 and ready("exit"):
                        pyautogui.press("esc")

                elif gesture == "zoom_in":
                    gesture_text = "Zoom In"
                    if stable >= HOLD_FRAMES and ready("zoom_in"):
                        pyautogui.hotkey("ctrl", "=")

                elif gesture == "zoom_out":
                    gesture_text = "Zoom Out"
                    if stable >= HOLD_FRAMES and ready("zoom_out"):
                        pyautogui.hotkey("ctrl", "-")

                else:
                    gesture_text = "Unknown"
            else:
                prev_gesture = None
                stable = 0

            # FPS
            curr = time.time()
            fps = int(1 / (curr - prev_time + 0.001))
            prev_time = curr

            cv2.putText(frame, gesture_text, (10, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.putText(frame, f"FPS: {fps}", (10, 80),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            cv2.imshow("Virtual Presentation Controller PRO", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                running = False
    finally:
        hands.close()
        cap.release()
        cv2.destroyAllWindows()
        running = False


# ---------------- CONTROLS ----------------
def run():
    global running
    if not running:
        running = True
        threading.Thread(target=start_camera, daemon=True).start()


def stop_camera():
    global running
    running = False


def screenshot():
    img = pyautogui.screenshot()
    filename = f"screenshot_{int(time.time())}.png"
    img.save(filename)
    print(f"Saved {filename}")


def on_close():
    stop_camera()
    time.sleep(0.3)
    app.destroy()


# ---------------- GUI ----------------
app = ctk.CTk()
app.geometry("700x600")
app.title("Virtual Presentation Controller PRO")
app.protocol("WM_DELETE_WINDOW", on_close)

title = ctk.CTkLabel(app, text="🎯 Virtual Presentation Controller PRO",
                     font=("Arial", 28, "bold"))
title.pack(pady=20)

box = ctk.CTkTextbox(app, width=620, height=260)
box.pack(pady=10)

box.insert("0.0", """
GESTURES (hold ~0.3 s for slide actions):

☝ Index finger only     = Cursor Move
👌 Pinch (in cursor pose) = Click
✌ 2 Fingers            = Next Slide
🤟 3 Fingers            = Previous Slide
🖐 4 Fingers            = Start Slide Show
✊ Fist (hold ~0.6 s)   = Exit Slide Show
🤙 Pinky only           = Zoom In
Ring + Pinky            = Zoom Out

Press Q in the camera window to close the camera.
""")
box.configure(state="disabled")

ctk.CTkButton(app, text="▶ START", width=220, height=50, command=run).pack(pady=10)
ctk.CTkButton(app, text="⏹ STOP", width=220, height=50, command=stop_camera).pack(pady=10)
ctk.CTkButton(app, text="📸 Screenshot", width=220, height=50, command=screenshot).pack(pady=10)

app.mainloop()