import cv2
import numpy as np

class Button:
    def __init__(self, x, y, w, h, value):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.value = value

    def draw(self, img):
        cv2.rectangle(img, (self.x, self.y), (self.x + self.w, self.y + self.h), (50, 50, 50), cv2.FILLED)
        cv2.rectangle(img, (self.x, self.y), (self.x + self.w, self.y + self.h), (255, 255, 255), 2)

        font_scale = min(self.w, self.h) * 0.008
        font_thickness = max(2, int(min(self.w, self.h) * 0.02))

        text_img = np.zeros((self.h, self.w, 3), np.uint8)
        text_size = cv2.getTextSize(self.value, cv2.FONT_HERSHEY_SIMPLEX, font_scale, font_thickness)[0]
        text_x = (self.w - text_size[0]) // 2
        text_y = (self.h + text_size[1]) // 2

        cv2.putText(text_img, self.value, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), font_thickness)
        text_img = cv2.GaussianBlur(text_img, (3, 3), 0)

        img[self.y:self.y+self.h, self.x:self.x+self.w] = cv2.addWeighted(
            img[self.y:self.y+self.h, self.x:self.x+self.w], 1, text_img, 1, 0
        )

        return img

    def check_click(self, img, dist, x1, y1):
        if (self.x < x1 < self.x + self.w) and (self.y < y1 < self.y + self.h) and dist <= 20:
            cv2.rectangle(img, (self.x, self.y), (self.x + self.w, self.y + self.h), (0, 255, 0), cv2.FILLED)
            cv2.rectangle(img, (self.x, self.y), (self.x + self.w, self.y + self.h), (255, 255, 255), 2)

            font_scale = min(self.w, self.h) * 0.008
            font_thickness = max(2, int(min(self.w, self.h) * 0.02))

            text_img = np.zeros((self.h, self.w, 3), np.uint8)
            text_size = cv2.getTextSize(self.value, cv2.FONT_HERSHEY_SIMPLEX, font_scale, font_thickness)[0]
            text_x = (self.w - text_size[0]) // 2
            text_y = (self.h + text_size[1]) // 2

            cv2.putText(text_img, self.value, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), font_thickness)
            text_img = cv2.GaussianBlur(text_img, (3, 3), 0)

            img[self.y:self.y+self.h, self.x:self.x+self.w] = cv2.addWeighted(
                img[self.y:self.y+self.h, self.x:self.x+self.w], 1, text_img, 1, 0
            )

            return True
        return False

def draw_calculator(img):
    h, w = img.shape[:2]
    right_margin = int(w * 0.05)  # 5% right margin
    calc_width = int(w * 0.35)  # Reduce calculator width to 35% of the screen
    calc_height = int(h * 0.95)  # 95% of the screen height
    start_x = w - calc_width - right_margin  # Move calculator to the right, leaving margin
    start_y = int(h * 0.025)  # Start 2.5% from the top of the screen
    button_width = calc_width // 4
    button_height = (calc_height - start_y) // 6  # Adjust button height

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

def combine_camera_and_calculator(camera_img, calc_img):
    h, w = camera_img.shape[:2]
    calc_width = int(w * 0.4)
    result = camera_img.copy()
    result[:, -calc_width:] = calc_img[:, -calc_width:]
    return result