import tkinter as tk
from tkinter import ttk
import cv2
import numpy as np
from PIL import Image, ImageTk
from hand_tracking import Tracker
from calculator import Button, draw_calculator

class HandTrackingCalculator:
    def __init__(self, window):
        self.window = window
        self.window.title("Hand Tracking Calculator")
        self.window.geometry("1800x1000")  # Set a large fixed size
        self.window.configure(bg="#2C3E50")

        self.setup_ui()
        self.setup_camera()
        self.setup_calculator()

        self.equation = ''
        self.delay = 0
        self.running = False

    def setup_ui(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background='#2C3E50')
        style.configure('TButton', background='#3498DB', foreground='white', font=('Arial', 12, 'bold'))
        style.configure('TLabel', background='#2C3E50', foreground='white', font=('Arial', 12))
        style.configure('TLabelframe', background='#2C3E50', foreground='white')
        style.configure('TLabelframe.Label', background='#2C3E50', foreground='white', font=('Arial', 12, 'bold'))

        self.main_frame = ttk.Frame(self.window)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.video_frame = ttk.Frame(self.main_frame)
        self.video_frame.grid(row=0, column=0, rowspan=2, padx=(0, 20), sticky="nsew")

        self.canvas = tk.Canvas(self.video_frame, width=1400, height=900, bg='black')  # Increased width
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.control_frame = ttk.Frame(self.main_frame)
        self.control_frame.grid(row=0, column=1, sticky="nsew")

        self.start_button = ttk.Button(self.control_frame, text="Start Calculator", command=self.start_calculator)
        self.start_button.pack(pady=10, fill=tk.X)

        self.stop_button = ttk.Button(self.control_frame, text="Stop Calculator", command=self.stop_calculator)
        self.stop_button.pack(pady=10, fill=tk.X)

        self.equation_label = ttk.Label(self.control_frame, text="Equation:", font=("Arial", 16))
        self.equation_label.pack(pady=10)

        self.equation_var = tk.StringVar()
        self.equation_display = ttk.Label(self.control_frame, textvariable=self.equation_var, font=("Arial", 24, "bold"))
        self.equation_display.pack(pady=10)

        self.instructions_frame = ttk.LabelFrame(self.control_frame, text="Instructions")
        self.instructions_frame.pack(pady=20, fill=tk.X)

        instructions = [
            "1. Click 'Start Calculator' to begin",
            "2. Use your index and middle fingers to 'click' buttons",
            "3. Pinch your fingers together to select a button",
            "4. Click 'Stop Calculator' to end the session"
        ]

        for instruction in instructions:
            ttk.Label(self.instructions_frame, text=instruction, wraplength=250).pack(pady=5, anchor="w")

        self.main_frame.columnconfigure(0, weight=4)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(0, weight=1)

    def setup_camera(self):
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1400)  # Increased width
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 900)
        self.tracker = Tracker()

    def setup_calculator(self):
        _, self.img = self.cap.read()
        self.img, self.button_list, (self.start_x, self.start_y, self.calc_width, self.calc_height) = draw_calculator(self.img)

    def start_calculator(self):
        self.running = True
        self.update_frame()

    def stop_calculator(self):
        self.running = False

    def update_frame(self):
        if self.running:
            success, img = self.cap.read()
            if not success:
                print("Failed to read frame from webcam. Please check your camera settings.")
                return

            img = cv2.flip(img, 1)
            img_copy = img.copy()
            img_copy = self.tracker.hand_landmark(img_copy)
            img, self.button_list, (self.start_x, self.start_y, self.calc_width, self.calc_height) = draw_calculator(img)
            img_copy, dist, x1, y1 = self.tracker.tracking(img_copy)

            self.process_button_clicks(img, dist, x1, y1)
            self.display_equation(img)

            # Overlay hand landmarks without blurring
            mask = np.zeros(img.shape[:2], dtype=np.uint8)
            if self.tracker.results.multi_hand_landmarks:
                for hand_landmarks in self.tracker.results.multi_hand_landmarks:
                    for landmark in hand_landmarks.landmark:
                        x, y = int(landmark.x * img.shape[1]), int(landmark.y * img.shape[0])
                        cv2.circle(mask, (x, y), 10, 255, -1)
            
            img_copy = cv2.addWeighted(img, 1, cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR), 0.5, 0)

            self.photo = self.convert_img_to_tkinter(img_copy)
            self.canvas.config(width=self.photo.width(), height=self.photo.height())
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)

        if self.running:
            self.window.after(10, self.update_frame)

    def process_button_clicks(self, img, dist, x1, y1):
        for button in self.button_list:
            if button.check_click(img, dist, x1, y1) and self.delay == 0:
                if button.value == 'DEL':
                    self.equation = self.equation[:-1] if self.equation and self.equation != 'error' else ''
                elif button.value == '^':
                    self.equation += '**' if self.equation != 'error' else ''
                elif button.value == 'CLEAR':
                    self.equation = ''
                elif button.value == '=':
                    try:
                        self.equation = str(eval(self.equation)) if self.equation and self.equation != 'error' else ''
                    except:
                        self.equation = 'error'
                else:
                    self.equation += button.value if self.equation != 'error' else button.value
                self.delay = 1
                self.equation_var.set(self.equation)
                self.animate_button_press(button)

        if self.delay:
            self.delay += 1
            if self.delay > 10:
                self.delay = 0

    def display_equation(self, img):
        font_scale = self.calc_height * 0.0025
        font_thickness = max(2, int(self.calc_height * 0.006))
        text_size = cv2.getTextSize(self.equation, cv2.FONT_HERSHEY_SIMPLEX, font_scale, font_thickness)[0]
        text_x = self.start_x + (self.calc_width - text_size[0]) // 2
        text_y = self.start_y + self.calc_height // 8

        equation_img = np.zeros((self.calc_height // 5, self.calc_width, 3), np.uint8)
        cv2.putText(equation_img, self.equation, 
                    (self.calc_width // 20, self.calc_height // 7), 
                    cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), font_thickness)
        
        equation_img = cv2.GaussianBlur(equation_img, (3, 3), 0)

        img[self.start_y:self.start_y+self.calc_height//5, self.start_x:self.start_x+self.calc_width] = cv2.addWeighted(
            img[self.start_y:self.start_y+self.calc_height//5, self.start_x:self.start_x+self.calc_width], 1, equation_img, 1, 0
        )

    def animate_button_press(self, button):
        overlay = self.img.copy()
        cv2.rectangle(overlay, (button.x, button.y), (button.x + button.w, button.y + button.h), (0, 255, 0), -1)
        cv2.addWeighted(overlay, 0.3, self.img, 0.7, 0, self.img)

    def convert_img_to_tkinter(self, img):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)
        return ImageTk.PhotoImage(image=img_pil)

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    app = HandTrackingCalculator(root)
    app.run()

# Modify the draw_calculator function in calculator.py
def draw_calculator(img):
    h, w = img.shape[:2]
    calc_width = int(w * 0.3)  # Decreased calculator width
    calc_height = int(h * 0.8)  # Kept the same height
    start_x = w - calc_width - 20  # Moved to the right
    start_y = (h - calc_height) // 2
    button_width = calc_width // 4
    button_height = calc_height // 6

    button_list_values = [
        ['1', '2', '3', '/'],
        ['4', '5', '6', '*'],
        ['7', '8', '9', '-'],
        ['0', '.', '=', '+']
    ]

    button_list = []
    for i in range(4):
        for j in range(4):
            x = start_x + j * button_width
            y = start_y + (i + 2) * button_height
            button_list.append(Button(x, y, button_width, button_height, button_list_values[i][j]))

    button_list.append(Button(start_x, start_y + button_height, button_width * 2, button_height, 'CLEAR'))
    button_list.append(Button(start_x + button_width * 2, start_y + button_height, button_width, button_height, 'DEL'))
    button_list.append(Button(start_x + button_width * 3, start_y + button_height, button_width, button_height, '^'))

    cv2.rectangle(img, (start_x, start_y), (start_x + calc_width, start_y + calc_height), (30, 30, 30), cv2.FILLED)
    cv2.rectangle(img, (start_x, start_y), (start_x + calc_width, start_y + calc_height), (255, 255, 255), 2)

    cv2.rectangle(img, (start_x, start_y), (start_x + calc_width, start_y + button_height), (10, 10, 10), cv2.FILLED)
    cv2.rectangle(img, (start_x, start_y), (start_x + calc_width, start_y + button_height), (255, 255, 255), 2)

    for button in button_list:
        img = button.draw(img)

    return img, button_list, (start_x, start_y, calc_width, calc_height)